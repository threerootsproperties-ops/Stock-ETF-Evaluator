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
    return df[["open", "high", "low", "close", "adj_close", "volume"]]


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
