"""Read raw data files into clean tables.

Accepts Alpha Vantage output in every shape it arrives in: plain CSV, plain
JSON, or the connector wrapper ([{"type": "text", "text": "..."}]) around
either. Missing values ("None", "", "-") become None, never zero.
"""
import io
import json
import os

import pandas as pd

MISSING = {"none", "", "-", "null", "nan", "n/a"}


def num(x):
    """Convert a raw field to float, or None when it is missing."""
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(",", "")
    if s.lower() in MISSING:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _unwrap(raw_text):
    """Return the inner payload as text, removing the connector wrapper."""
    t = raw_text.lstrip("﻿").strip()
    if t.startswith("["):
        try:
            obj = json.loads(t)
            if isinstance(obj, list) and obj and isinstance(obj[0], dict) and "text" in obj[0]:
                return "".join(part.get("text", "") for part in obj).strip()
        except json.JSONDecodeError:
            pass
    return t


def find(run_dir, base):
    """Find base.csv, base.json or base.txt in the run folder."""
    for ext in (".csv", ".json", ".txt"):
        p = os.path.join(run_dir, base + ext)
        if os.path.exists(p):
            return p
    return None


def read_payload(path):
    with open(path, "r", encoding="utf-8") as f:
        return _unwrap(f.read())


def read_json(run_dir, base):
    p = find(run_dir, base)
    if not p:
        return None
    text = read_payload(p)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(f"{os.path.basename(p)} is not valid JSON")


def read_prices(run_dir, base):
    """Return a price table sorted oldest to newest, or None if absent.

    Columns: open, high, low, close, adj_close, volume. Index: date.
    """
    p = find(run_dir, base)
    if not p:
        return None
    text = read_payload(p)
    if text.startswith("{"):
        obj = json.loads(text)
        key = next((k for k in obj if "Time Series" in k and not k.endswith(("_count", "_truncated"))), None)
        if key is None:
            raise ValueError(f"{os.path.basename(p)} has no price series: {list(obj)[:3]}")
        rows = []
        for d, r in obj[key].items():
            row = {"timestamp": d}
            for k, v in r.items():
                name = k.split(". ", 1)[-1].strip()
                row[name] = v
            rows.append(row)
        df = pd.DataFrame(rows)
    else:
        df = pd.read_csv(io.StringIO(text.replace("\r\n", "\n")))
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns={"adjusted close": "adj_close", "adjusted_close": "adj_close", "date": "timestamp"})
    if "timestamp" not in df.columns or "close" not in df.columns:
        raise ValueError(f"{os.path.basename(p)} is missing timestamp or close columns")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    for c in ("open", "high", "low", "close", "adj_close", "volume"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "adj_close" not in df.columns:
        df["adj_close"] = df["close"]
    for c in ("open", "high", "low"):
        if c not in df.columns:
            df[c] = df["close"]
    if "volume" not in df.columns:
        df["volume"] = float("nan")
    df = df.dropna(subset=["close"]).drop_duplicates("timestamp").sort_values("timestamp").set_index("timestamp")
    df = df[["open", "high", "low", "close", "adj_close", "volume"]].copy()
    add_split_adjusted(df)
    return df


def add_split_adjusted(df):
    """Add s_close, s_high and s_low: prices restated for stock splits only.

    A split shows up as a jump in close / adjusted close from one bar to the
    next (2 for a 2-for-1 split). Dividends move that ratio by a percent or
    two, so only jumps beyond 20% are treated as splits. The list of splits
    found is stored in df.attrs["splits"].
    """
    g = (df["close"] / df["adj_close"]).values
    factor = [1.0] * len(df)
    splits, run = [], 1.0
    for i in range(len(df) - 2, -1, -1):
        step = g[i] / g[i + 1] if g[i + 1] else 1.0
        if step > 1.2 or step < 0.8:
            run *= step
            splits.append({"week_ending": str(df.index[i + 1].date()), "ratio": round(step, 4)})
        factor[i] = run
    df["s_close"] = df["close"] / factor
    df["s_high"] = df["high"] / factor
    df["s_low"] = df["low"] / factor
    # The bar in which a split happened mixes old and new prices: restate the side that is still on the old basis.
    for sp in splits:
        d, k = __import__("pandas").Timestamp(sp["week_ending"]), sp["ratio"]
        if k > 1 and df.at[d, "s_high"] / df.at[d, "s_close"] > 1.3:
            df.at[d, "s_high"] = df.at[d, "s_high"] / k
        if k < 1 and df.at[d, "s_low"] / df.at[d, "s_close"] < 0.77:
            df.at[d, "s_low"] = df.at[d, "s_low"] / k
    df.attrs["splits"] = splits


def apply_splits_to_daily(daily, weekly):
    """Restate daily bars for any split that falls inside the daily window.

    Returns a list of notes describing what was done or could not be done.
    """
    import math
    notes = []
    for sp in (weekly.attrs.get("splits") or []):
        end = __import__("pandas").Timestamp(sp["week_ending"])
        if end <= daily.index[0]:
            continue
        win = daily[(daily.index > end - __import__("pandas").Timedelta(days=7)) & (daily.index <= end)]
        prev = daily["close"].shift()
        jump = (win["close"] / prev[win.index]).dropna()
        target = 1 / sp["ratio"]
        hit = [d for d, v in jump.items() if abs(math.log(v) - math.log(target)) < 0.15]
        if not hit:
            notes.append(f"A stock split near {sp['week_ending']} could not be located in the daily prices; levels may be distorted.")
            continue
        before = daily.index < hit[0]
        for c in ("open", "high", "low", "close", "adj_close", "s_close", "s_high", "s_low"):
            daily.loc[before, c] = daily.loc[before, c] / sp["ratio"]
        daily.loc[before, "volume"] = daily.loc[before, "volume"] * sp["ratio"]
        notes.append(f"Daily prices before {hit[0].date()} were restated for a {sp['ratio']:g}-for-1 stock split.")
    return notes


def read_statement(run_dir, base):
    """Return (annual, quarterly) tables sorted oldest to newest, or (None, None)."""
    obj = read_json(run_dir, base)
    if not obj:
        return None, None
    if "annualReports" not in obj and "quarterlyReports" not in obj:
        note = obj.get("Information") or obj.get("Note") or obj.get("error") or list(obj)[:3]
        raise ValueError(f"{base} file holds no reports: {note}")

    def table(records):
        if not records:
            return None
        df = pd.DataFrame(records)
        df["fiscalDateEnding"] = pd.to_datetime(df["fiscalDateEnding"])
        for c in df.columns:
            if c not in ("fiscalDateEnding", "reportedCurrency"):
                df[c] = df[c].map(num)
        return df.sort_values("fiscalDateEnding").set_index("fiscalDateEnding")

    return table(obj.get("annualReports")), table(obj.get("quarterlyReports"))


def check_prices(df, label, min_rows):
    """Return a list of problems found in a price table."""
    problems = []
    if df is None:
        return [f"{label}: file not found"]
    if len(df) < min_rows:
        problems.append(f"{label}: only {len(df)} rows, need at least {min_rows}")
    bad = df[(df["high"] < df["low"]) | (df["close"] > df["high"] * 1.0001) | (df["close"] < df["low"] * 0.9999)]
    if len(bad):
        problems.append(f"{label}: {len(bad)} rows where close is outside the high-low range (first: {bad.index[0].date()})")
    if (df["close"] <= 0).any():
        problems.append(f"{label}: non-positive prices")
    return problems
