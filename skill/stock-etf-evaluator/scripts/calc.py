"""All calculations. Every number in a report is produced here.

Definitions follow reference/01-methodology.md and reference/02-risk-rating.md.
Functions return plain dicts so the results can be saved as JSON.
"""
import math

import numpy as np
import pandas as pd

SECTOR_FUNDS = {
    "technology": "XLK", "information technology": "XLK",
    "financial services": "XLF", "financials": "XLF", "financial": "XLF",
    "healthcare": "XLV", "health care": "XLV",
    "consumer cyclical": "XLY", "consumer discretionary": "XLY",
    "communication services": "XLC",
    "industrials": "XLI",
    "consumer defensive": "XLP", "consumer staples": "XLP",
    "energy": "XLE",
    "utilities": "XLU",
    "basic materials": "XLB", "materials": "XLB",
    "real estate": "XLRE",
}

GEARED_WORDS = ("2x", "3x", "-1x", "1.5x", "ultra", "inverse", "leveraged", " short ", " bear ", "daily target")


def sector_fund(sector):
    return SECTOR_FUNDS.get((sector or "").strip().lower())


def company_group(sector, industry):
    """Route a company to the sector rules in reference/03-sector-metric-map.md."""
    ind = (industry or "").lower()
    if "bank" in ind:
        return "bank"
    if "insurance" in ind:
        return "insurer"
    if "reit" in ind:
        return "reit"
    return "default"


# ---------------------------------------------------------------- helpers

def _f(x):
    """Float or None; turns NaN and infinity into None."""
    if x is None:
        return None
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _div(a, b):
    a, b = _f(a), _f(b)
    if a is None or b is None or b == 0:
        return None
    return a / b


def _get(df, field, pos=-1):
    """Value of a field at a row position, or None."""
    if df is None or field not in df.columns or len(df) < abs(pos) + (0 if pos < 0 else 1):
        return None
    return _f(df[field].iloc[pos])


def _ttm(q, field):
    """Sum of the last four quarters; None unless all four are present."""
    if q is None or field not in q.columns or len(q) < 4:
        return None
    vals = [_f(v) for v in q[field].iloc[-4:]]
    if any(v is None for v in vals):
        return None
    return sum(vals)


def _debt(row):
    d = _f(row.get("shortLongTermDebtTotal"))
    if d is not None:
        return d
    parts = [_f(row.get("shortTermDebt")), _f(row.get("longTermDebt"))]
    if all(p is None for p in parts):
        return None
    return sum(p for p in parts if p is not None)


def _cash(row):
    c = _f(row.get("cashAndShortTermInvestments"))
    return c if c is not None else _f(row.get("cashAndCashEquivalentsAtCarryingValue"))


def _vs_history(cur, med, higher_is_better):
    if cur is None or med is None:
        return None
    if abs(cur - med) <= 0.10 * abs(med):
        return "in line"
    better = cur > med if higher_is_better else cur < med
    return "better" if better else "worse"


def _median(vals, need=3):
    vals = [v for v in vals if v is not None]
    return float(np.median(vals)) if len(vals) >= need else None


def _row(name, cur, hist, higher_is_better=True, unit="ratio", note=None, yield_row=False):
    med = _median(hist) if hist is not None else None
    cur = _f(cur)
    vs = _vs_history(cur, med, higher_is_better)
    if yield_row and vs is not None:
        if cur <= 0 or med <= 0:
            vs = "not comparable: negative now or in its history"
        else:
            vs = {"better": "cheaper", "worse": "dearer"}.get(vs, vs)
    return {"name": name, "current": cur, "median_5y": med, "unit": unit, "vs_history": vs, "note": note}


# ---------------------------------------------------------------- quality

def quality(inc_a, inc_q, bal_a, bal_q, cf_q, group):
    rows = []
    n = min(5, len(inc_a)) if inc_a is not None else 0
    fy = list(inc_a.index[-n:]) if n else []

    def bal_at(date):
        if bal_a is None or date not in bal_a.index:
            return None
        return bal_a.loc[date]

    # Gross profitability
    hist = [_div(inc_a.loc[d].get("grossProfit"), (bal_at(d) if bal_at(d) is not None else {}).get("totalAssets")) for d in fy]
    cur = _div(_ttm(inc_q, "grossProfit"), _get(bal_q, "totalAssets"))
    rows.append(_row("Gross profitability (gross profit / total assets)", cur, hist))

    # Operating margin
    hist = [_div(inc_a.loc[d].get("operatingIncome"), inc_a.loc[d].get("totalRevenue")) for d in fy]
    cur = _div(_ttm(inc_q, "operatingIncome"), _ttm(inc_q, "totalRevenue"))
    rows.append(_row("Operating margin", cur, hist, unit="pct"))

    # Return on equity
    def roe_fy(d):
        b = bal_at(d)
        i = list(bal_a.index).index(d) if b is not None else None
        if b is None or i == 0:
            return None
        e1, e0 = _f(b.get("totalShareholderEquity")), _f(bal_a.iloc[i - 1].get("totalShareholderEquity"))
        if e1 is None or e0 is None or e1 <= 0 or e0 <= 0:
            return None
        return _div(inc_a.loc[d].get("netIncome"), (e1 + e0) / 2)

    hist = [roe_fy(d) for d in fy]
    e_now, e_then = _get(bal_q, "totalShareholderEquity"), _get(bal_q, "totalShareholderEquity", -5)
    ni_ttm = _ttm(inc_q, "netIncome")
    neg_equity = e_now is not None and e_now <= 0
    if neg_equity:
        rows.append(_row("Return on equity", None, None, unit="pct", note="not meaningful: shareholder equity is negative"))
    else:
        avg_e = (e_now + e_then) / 2 if e_now is not None and e_then is not None and e_then > 0 else e_now
        rows.append(_row("Return on equity", _div(ni_ttm, avg_e), hist, unit="pct"))

    # Debt load
    if group in ("bank", "insurer"):
        pass
    elif neg_equity:
        rows.append(_row("Debt load (total debt / equity)", None, None, note="not meaningful: shareholder equity is negative"))
    else:
        hist = []
        for d in fy:
            b = bal_at(d)
            e = _f(b.get("totalShareholderEquity")) if b is not None else None
            hist.append(_div(_debt(b), e) if b is not None and e and e > 0 else None)
        cur = _div(_debt(bal_q.iloc[-1]) if bal_q is not None and len(bal_q) else None, e_now)
        rows.append(_row("Debt load (total debt / equity)", cur, hist, higher_is_better=False))

    # Earnings stability
    ni = [_f(v) for v in inc_a["netIncome"].iloc[-6:]] if inc_a is not None and "netIncome" in inc_a.columns else []
    if len(ni) < 6 or any(v is None for v in ni):
        rows.append(_row("Earnings stability (st. dev. of net income growth, 5 years)", None, None, note="not available: fewer than 6 fiscal years"))
    elif any(v <= 0 for v in ni[:-1]):
        rows.append(_row("Earnings stability (st. dev. of net income growth, 5 years)", None, None,
                         note="not meaningful: net income was zero or negative in at least one of the last 5 base years"))
    else:
        g = [ni[i] / ni[i - 1] - 1 for i in range(1, 6)]
        rows.append(_row("Earnings stability (st. dev. of net income growth, 5 years)", float(np.std(g, ddof=1)), None, higher_is_better=False))

    # Cash conversion
    if group not in ("bank", "insurer"):
        ocf = _ttm(cf_q, "operatingCashflow")
        if ni_ttm is not None and ni_ttm <= 0:
            rows.append(_row("Cash conversion (operating cash flow / net income, 4 quarters)", None, None,
                             note="not meaningful: trailing net income is zero or negative"))
        else:
            rows.append(_row("Cash conversion (operating cash flow / net income, 4 quarters)", _div(ocf, ni_ttm), None))
    return rows


# ---------------------------------------------------------------- value

def value(inc_a, inc_q, bal_a, bal_q, cf_a, cf_q, weekly, market_cap, group):
    rows, notes = [], []
    last_bal = bal_q.iloc[-1] if bal_q is not None and len(bal_q) else None
    debt, cash = (_debt(last_bal), _cash(last_bal)) if last_bal is not None else (None, None)
    mc = _f(market_cap)
    ev = mc + (debt or 0) - (cash or 0) if mc is not None and last_bal is not None else None

    n = min(5, len(inc_a)) if inc_a is not None else 0
    fy = list(inc_a.index[-n:]) if n else []

    def hist_caps(d):
        """Market cap and enterprise value at a fiscal year end."""
        if bal_a is None or d not in bal_a.index or weekly is None:
            return None, None
        b = bal_a.loc[d]
        px = weekly["close"][:d]
        sh = _f(b.get("commonStockSharesOutstanding"))
        if len(px) == 0 or sh is None:
            return None, None
        if (d - px.index[-1]).days > 14:
            return None, None
        m = float(px.iloc[-1]) * sh
        return m, m + (_debt(b) or 0) - (_cash(b) or 0)

    caps = {d: hist_caps(d) for d in fy}

    def capex(row):
        c = _f(row.get("capitalExpenditures"))
        return abs(c) if c is not None else None

    # Earnings yield
    hist = [_div(inc_a.loc[d].get("netIncome"), caps[d][0]) for d in fy]
    rows.append(_row("Earnings yield (trailing net income / market cap)", _div(_ttm(inc_q, "netIncome"), mc), hist, unit="pct", yield_row=True))

    if group not in ("bank", "insurer"):
        # Free cash flow yield
        def fcf_fy(d):
            if cf_a is None or d not in cf_a.index:
                return None
            o, c = _f(cf_a.loc[d].get("operatingCashflow")), capex(cf_a.loc[d])
            return None if o is None or c is None else o - c
        hist = [_div(fcf_fy(d), caps[d][1]) for d in fy]
        o_ttm = _ttm(cf_q, "operatingCashflow")
        c_ttm = None
        if cf_q is not None and "capitalExpenditures" in cf_q.columns and len(cf_q) >= 4:
            cs = [_f(v) for v in cf_q["capitalExpenditures"].iloc[-4:]]
            c_ttm = sum(abs(v) for v in cs) if all(v is not None for v in cs) else None
        fcf = o_ttm - c_ttm if o_ttm is not None and c_ttm is not None else None
        rows.append(_row("Free cash flow yield (free cash flow / enterprise value)", _div(fcf, ev), hist, unit="pct", yield_row=True))

    if group == "default":
        hist = [_div(inc_a.loc[d].get("ebitda"), caps[d][1]) for d in fy]
        rows.append(_row("EBITDA yield (EBITDA / enterprise value)", _div(_ttm(inc_q, "ebitda"), ev), hist, unit="pct", yield_row=True))

    if group != "bank" and group != "insurer":
        hist = [_div(inc_a.loc[d].get("totalRevenue"), caps[d][1]) for d in fy]
        rows.append(_row("Sales yield (revenue / enterprise value)", _div(_ttm(inc_q, "totalRevenue"), ev), hist, unit="pct", yield_row=True))

    if group in ("bank", "insurer") and last_bal is not None:
        eq = _f(last_bal.get("totalShareholderEquity"))
        intang = (_f(last_bal.get("goodwill")) or 0) + (_f(last_bal.get("intangibleAssetsExcludingGoodwill")) or 0)
        book = eq - intang if group == "bank" and eq is not None else eq
        label = "Tangible book yield (tangible book value / market cap)" if group == "bank" else "Book yield (book value / market cap)"
        rows.append(_row(label, _div(book, mc), None, unit="pct"))

    # Sanity check: profile market cap against price times shares
    sh = _f(last_bal.get("commonStockSharesOutstanding")) if last_bal is not None else None
    if sh and weekly is not None and mc:
        implied = sh * float(weekly["close"].iloc[-1])
        if abs(implied / mc - 1) > 0.15:
            notes.append(f"Market cap from the profile ({mc/1e9:.1f}B) differs from last close times reported shares "
                         f"({implied/1e9:.1f}B) by more than 15%. Yields use the profile figure.")
    return {"rows": rows, "enterprise_value": ev, "market_cap": mc, "total_debt": debt, "cash": cash, "notes": notes}


# ---------------------------------------------------------------- prices

def _ret(series, weeks):
    if series is None or len(series) <= weeks:
        return None
    return _f(series.iloc[-1] / series.iloc[-1 - weeks] - 1)


def momentum(daily, weekly, spy_w, sec_w):
    w = weekly["adj_close"]
    out = {"returns": {}, "notes": []}
    for label, wk in (("13w", 13), ("26w", 26), ("52w", 52)):
        out["returns"][label] = {
            "stock": _ret(w, wk),
            "spy": _ret(spy_w["adj_close"], wk) if spy_w is not None else None,
            "sector": _ret(sec_w["adj_close"], wk) if sec_w is not None else None,
        }

    def m12_1(s):
        return _f(s.iloc[-5] / s.iloc[-53] - 1) if s is not None and len(s) >= 53 else None

    out["mom_12_1"] = {"stock": m12_1(w), "spy": m12_1(spy_w["adj_close"]) if spy_w is not None else None,
                       "sector": m12_1(sec_w["adj_close"]) if sec_w is not None else None}
    close = float(daily["close"].iloc[-1])
    hi52 = max(float(weekly["high"].iloc[-52:].max()), float(daily["high"].max())) if len(weekly) >= 52 else None
    out["last_close"] = close
    out["last_date"] = str(daily.index[-1].date())
    out["high_52w"] = hi52
    out["pct_of_52w_high"] = _div(close, hi52)
    sma50 = _f(daily["close"].iloc[-50:].mean()) if len(daily) >= 50 else None
    sd50 = _f(daily["close"].iloc[-50:].std(ddof=1)) if len(daily) >= 50 else None
    wk40 = _f(weekly["close"].iloc[-40:].mean()) if len(weekly) >= 40 else None
    wk10 = _f(weekly["close"].iloc[-10:].mean()) if len(weekly) >= 10 else None
    out.update({"sma50": sma50, "avg_40w": wk40, "avg_10w": wk10,
                "above_sma50": None if sma50 is None else close > sma50,
                "above_40w": None if wk40 is None else close > wk40,
                "avg10w_above_40w": None if wk40 is None or wk10 is None else wk10 > wk40})
    z = (close - sma50) / sd50 if sma50 is not None and sd50 else None
    out["extension_z"] = _f(z)
    out["extended"] = None if z is None else z >= 2.5
    return out


def liquidity(daily):
    d = daily.dropna(subset=["volume"])
    if len(d) < 20:
        return {"dollar_volume_median_20d": None, "amihud_60d": None, "relative_volume": None}
    dv = d["close"] * d["volume"]
    r = d["close"].pct_change().abs()
    am = (r / dv).iloc[-60:].replace([np.inf, -np.inf], np.nan).dropna()
    avg50 = d["volume"].iloc[-50:].mean()
    return {"dollar_volume_median_20d": _f(dv.iloc[-20:].median()),
            "amihud_60d": _f(am.mean() * 1e9) if len(am) else None,   # per $1 billion traded
            "relative_volume": _div(d["volume"].iloc[-1], avg50),
            "last_price": _f(d["close"].iloc[-1])}


def atr14(daily):
    h, l, c = daily["high"], daily["low"], daily["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - l.iloc[0]
    if len(tr) < 15:
        return None
    atr = tr.iloc[:14].mean()
    for v in tr.iloc[14:]:
        atr = (atr * 13 + v) / 14
    return _f(atr)


def _swings(series, kind, k=3):
    """Positions of swing lows or highs: extreme of the k bars on each side."""
    vals, out = series.values, []
    for i in range(k, len(vals) - k):
        win = vals[i - k:i + k + 1]
        if (kind == "low" and vals[i] == win.min()) or (kind == "high" and vals[i] == win.max()):
            if not out or i - out[-1] > k:
                out.append(i)
    return out


def topping_flags(daily):
    """Topping flags as of the last row of the table given."""
    flags = []
    if len(daily) < 55:
        return flags
    c, v = daily["close"], daily["volume"]
    sma50 = c.iloc[-50:].mean()
    if c.iloc[-1] < sma50 and v.iloc[-1] > v.iloc[-50:].mean():
        flags.append("Close below the 50-day average on above-average volume")
    down = (c.pct_change() <= -0.002) & (v > v.shift())
    n_dist = int(down.iloc[-25:].sum())
    if n_dist >= 5:
        flags.append(f"{n_dist} distribution days in the last 25 sessions")
    prior_high = daily["high"].rolling(50).max().shift()
    broke = (c > prior_high).iloc[-30:]
    if broke.any():
        level = float(prior_high[broke[broke].index[-1]])
        if c.iloc[-1] <= level * 0.93:
            flags.append(f"Failed breakout: close is 7% or more below the {level:.2f} breakout level")
    sh, sl = _swings(daily["high"], "high"), _swings(daily["low"], "low")
    if len(sh) >= 2 and len(sl) >= 2:
        if daily["high"].iloc[sh[-1]] < daily["high"].iloc[sh[-2]] and daily["low"].iloc[sl[-1]] < daily["low"].iloc[sl[-2]]:
            flags.append("Lower swing high followed by a lower swing low")
    return flags


def levels(daily, mom):
    out = {"notes": []}
    atr = atr14(daily)
    close = float(daily["close"].iloc[-1])
    win = daily.iloc[-50:]
    pivot = float(win["high"].max())
    pivot_date = win["high"].idxmax()
    out.update({"atr14": atr, "pivot_high_50d": pivot, "pivot_date": str(pivot_date.date()), "last_close": close})
    if atr is None:
        out["notes"].append("Not enough daily history for ATR; levels not available.")
        return out

    reasons = []
    if mom.get("extended"):
        reasons.append("the stock is Extended (2.5 or more standard deviations above its 50-day average)")
    if mom.get("above_40w") is False:
        reasons.append("price is below its 40-week average")
    out["buy_range"] = None if reasons else {"low": pivot, "high": pivot + 2 * atr}
    out["no_buy_range_reason"] = "; ".join(reasons) if reasons else None

    entry = pivot
    stop = max(entry - 2 * atr, entry * 0.92)
    if out["buy_range"]:
        out["reference_entry"] = entry
        out["initial_stop"] = stop
        out["initial_stop_basis"] = "2 x ATR" if entry - 2 * atr >= entry * 0.92 else "8% below entry"

    lows = _swings(daily["low"], "low")
    higher = None
    for a, b in zip(lows[:-1], lows[1:]):
        if daily["low"].iloc[b] > daily["low"].iloc[a]:
            higher = b
    sma50 = mom.get("sma50")
    hsl = float(daily["low"].iloc[higher]) if higher is not None else None
    refs = [x for x in (sma50, hsl) if x is not None]
    if refs:
        ref = max(refs)
        out["trail_reference"] = ref
        out["trail_reference_basis"] = "50-day average" if ref == sma50 else f"higher swing low of {daily.index[higher].date()}"
        out["trailing_exit"] = ref - atr
        out["trailing_exit_breached"] = close < ref - atr
        flags_now = topping_flags(daily)
        flags_then = topping_flags(daily.iloc[:-5]) if len(daily) > 60 else []
        out["topping_flags"] = flags_now
        out["tightened_active"] = bool(flags_now) and bool(flags_then)
        out["tightened_trail"] = ref - 0.5 * atr
    out["last_swing_low"] = float(daily["low"].iloc[lows[-1]]) if lows else None
    out["last_swing_low_date"] = str(daily.index[lows[-1]].date()) if lows else None

    recent = daily["low"].iloc[-10:]
    if out["last_swing_low"] is None or float(recent.min()) < out["last_swing_low"]:
        out["recent_low"] = float(recent.min())
        out["recent_low_date"] = str(recent.idxmin().date())

    out["measured_move"] = None
    after = daily.loc[pivot_date:]
    if out["buy_range"] and len(after) > 1:
        pull_low = float(after["low"].iloc[1:].min())
        mm = pivot + (pivot - pull_low)
        out["measured_move"] = mm
        out["measured_move_basis"] = f"pivot plus the depth of the pullback to {pull_low:.2f}"
        rr = _div(mm - entry, entry - stop)
        out["reward_to_risk"] = rr
        out["breakeven_win_rate"] = _div(1, 1 + rr) if rr is not None else None
    elif out["buy_range"]:
        out["notes"].append("The pivot high is the latest session, so there is no pullback to measure.")
    return out


# ---------------------------------------------------------------- risk

def _max_drawdown(series):
    peak = series.cummax()
    return _f((series / peak - 1).min())


def risk(weekly, spy_w, liq, group, inc_q, bal_q, earnings, is_etf=False, etf=None, geared=False, today=None):
    out = {"notches": [], "skipped": [], "flags": [], "notes": []}
    w = weekly["adj_close"].iloc[-261:]
    years = (w.index[-1] - w.index[0]).days / 365.25
    out["history_years"] = round(years, 1)
    if len(w) < 105:
        out.update({"class": None, "base_class": None})
        out["notes"].append("Not available, insufficient history: fewer than 2 years of weekly prices.")
        return out
    r = np.log(w / w.shift()).dropna()
    vol = float(r.std(ddof=1) * math.sqrt(52))
    base = 1 if vol < 0.12 else 2 if vol < 0.20 else 3 if vol < 0.30 else 4 if vol < 0.50 else 5
    out.update({"volatility": vol, "max_drawdown": _max_drawdown(w), "base_class": base})
    if years < 4:
        out["notes"].append("Short history; the class may understate risk.")
    if spy_w is not None:
        s = spy_w["adj_close"][w.index[0]:]
        dd = _max_drawdown(s) if len(s) > 10 else None
        if dd is not None and dd > -0.20:
            out["notes"].append("History includes no bear market (no 20% decline in SPY in the window); the class may understate risk.")

    def notch(group_name, reasons):
        if reasons:
            out["notches"].append({"group": group_name, "reasons": reasons})

    if is_etf:
        reasons = []
        if etf:
            if etf.get("top10_weight") is not None and etf["top10_weight"] > 0.50:
                reasons.append(f"top 10 holdings are {etf['top10_weight']*100:.0f}% of assets")
            if etf.get("net_assets") is not None and etf["net_assets"] < 50e6:
                reasons.append(f"net assets are ${etf['net_assets']/1e6:.0f} million, below $50 million")
        else:
            out["skipped"].append("Structure tests: ETF profile not available")
        notch("Structure", reasons)
    else:
        reasons = []
        ni = _ttm(inc_q, "netIncome")
        if ni is None:
            out["skipped"].append("Trailing net income: not available")
        elif ni < 0:
            reasons.append(f"trailing 4-quarter net income is negative (${ni/1e6:,.0f} million)")
        last_bal = bal_q.iloc[-1] if bal_q is not None and len(bal_q) else None
        eq = _f(last_bal.get("totalShareholderEquity")) if last_bal is not None else None
        if eq is None:
            out["skipped"].append("Shareholder equity: not available")
        elif eq < 0:
            reasons.append("shareholder equity is negative")
        if group == "default":
            oi, ie = _ttm(inc_q, "operatingIncome"), _ttm(inc_q, "interestExpense")
            debt = _debt(last_bal) if last_bal is not None else None
            if ie is None or ie <= 0:
                out["skipped"].append("Interest cover: interest expense not available")
            elif oi is not None and oi < 2 * ie:
                reasons.append(f"operating income is {oi/ie:.1f} times interest expense, below 2")
            eb = _ttm(inc_q, "ebitda")
            if debt is None or eb is None:
                out["skipped"].append("Debt to EBITDA: not available")
            elif eb <= 0 and debt > 0:
                reasons.append("EBITDA is zero or negative while the company carries debt")
            elif eb > 0 and debt > 4 * eb:
                reasons.append(f"total debt is {debt/eb:.1f} times EBITDA, above 4")
        elif group == "reit":
            debt, cash, eb = _debt(last_bal) if last_bal is not None else None, _cash(last_bal) if last_bal is not None else None, _ttm(inc_q, "ebitda")
            if debt is None or eb is None or eb <= 0:
                out["skipped"].append("Net debt to EBITDA: not available")
            elif (debt - (cash or 0)) > 8 * eb:
                reasons.append(f"net debt is {(debt-(cash or 0))/eb:.1f} times EBITDA, above 8")
            da = _ttm(inc_q, "depreciationAndAmortization")
            if ni is not None and da is not None and ni + da < 0:
                reasons.append("approximate funds from operations are negative")
        notch("Balance sheet", reasons)

    reasons = []
    dv, px = liq.get("dollar_volume_median_20d"), liq.get("last_price")
    if dv is None:
        out["skipped"].append("Dollar volume: not available")
    elif dv < 5e6:
        reasons.append(f"median dollar volume is ${dv/1e6:.1f} million, below $5 million")
    if px is not None and px < 5:
        reasons.append(f"share price is ${px:.2f}, below $5")
    notch("Liquidity", reasons)

    if spy_w is not None and len(spy_w) >= 40:
        s_close, s_avg = float(spy_w["close"].iloc[-1]), float(spy_w["close"].iloc[-40:].mean())
        out["spy_vs_40w"] = {"close": s_close, "avg_40w": s_avg, "above": s_close > s_avg}
        if s_close < s_avg:
            notch("Market backdrop", [f"SPY ({s_close:.2f}) is below its 40-week average ({s_avg:.2f})"])
    else:
        out["skipped"].append("Market backdrop: SPY weekly prices not available")

    cls = min(5, base + len(out["notches"]))
    out["capped"] = base + len(out["notches"]) > 5
    if geared:
        cls = 5
        out["notes"].append("Set to class 5: geared, inverse and single-stock funds reset daily.")
    out["class"] = cls

    today = today or weekly.index[-1]
    if earnings:
        try:
            last = pd.to_datetime(earnings[0]["reportedDate"])
            age = (today - last).days
            out["last_earnings_date"] = str(last.date())
            if age > 75:
                out["flags"].append(f"Last earnings report was {age} days ago, so the next one is likely near. The exact date is not in the free data.")
        except (KeyError, ValueError, TypeError):
            pass
    return out


# ---------------------------------------------------------------- context

def context(inc_a, inc_q, bal_q, earnings, spy_w, sec_w):
    out = {"net_income_ttm": _ttm(inc_q, "netIncome")}
    if inc_a is not None and len(inc_a) >= 2:
        def growth(field, years):
            if len(inc_a) <= years:
                return None
            a, b = _f(inc_a[field].iloc[-1]), _f(inc_a[field].iloc[-1 - years])
            if a is None or b is None or b <= 0 or a <= 0:
                return None
            return (a / b) ** (1 / years) - 1
        out["fiscal_year"] = str(inc_a.index[-1].date())
        out["revenue_growth_1y"] = growth("totalRevenue", 1)
        out["revenue_growth_3y"] = growth("totalRevenue", 3)
        out["net_income_growth_1y"] = growth("netIncome", 1)
        out["net_income_latest_fy"] = _f(inc_a["netIncome"].iloc[-1])
        out["net_income_prior_fy"] = _f(inc_a["netIncome"].iloc[-2])
    if bal_q is not None and "commonStockSharesOutstanding" in bal_q.columns and len(bal_q) >= 5:
        out["share_count_change_1y"] = _div(_get(bal_q, "commonStockSharesOutstanding"), _get(bal_q, "commonStockSharesOutstanding", -5))
        if out["share_count_change_1y"] is not None:
            out["share_count_change_1y"] -= 1
    out["earnings"] = [{"quarter": e.get("fiscalDateEnding"), "reported": e.get("reportedDate"),
                        "eps": _f_str(e.get("reportedEPS")), "estimate": _f_str(e.get("estimatedEPS")),
                        "surprise_pct": _f_str(e.get("surprisePercentage"))} for e in (earnings or [])[:4]]
    if spy_w is not None and sec_w is not None:
        out["sector_vs_spy"] = {k: None if _ret(sec_w["adj_close"], n) is None or _ret(spy_w["adj_close"], n) is None
                                else _ret(sec_w["adj_close"], n) - _ret(spy_w["adj_close"], n)
                                for k, n in (("13w", 13), ("26w", 26), ("52w", 52))}
    return out


def _f_str(x):
    from loader import num
    return num(x)


# ---------------------------------------------------------------- ETF

def etf_profile(raw, name):
    from loader import num
    if not raw or "net_assets" not in raw and "holdings" not in raw:
        return None
    holdings = [{"symbol": h.get("symbol"), "name": h.get("description"), "weight": num(h.get("weight"))}
                for h in raw.get("holdings", []) if num(h.get("weight")) is not None]
    holdings.sort(key=lambda h: -h["weight"])
    weights = [h["weight"] for h in holdings]
    total = sum(weights)
    out = {
        "net_assets": num(raw.get("net_assets")),
        "expense_ratio": num(raw.get("net_expense_ratio")),
        "turnover": num(raw.get("portfolio_turnover")),
        "dividend_yield": num(raw.get("dividend_yield")),
        "inception_date": raw.get("inception_date"),
        "last_updated": raw.get("last_updated"),
        "leveraged_field": raw.get("leveraged"),
        "top10": holdings[:10],
        "top10_weight": sum(weights[:10]) if weights else None,
        "holdings_count": len(holdings),
        "holdings_weight_total": total if weights else None,
        "effective_holdings": 1 / sum(w * w for w in weights) if weights and sum(w * w for w in weights) > 0 else None,
        "sectors": sorted([{"sector": s.get("sector"), "weight": num(s.get("weight"))} for s in raw.get("sectors", [])
                           if num(s.get("weight"))], key=lambda s: -s["weight"]),
    }
    padded = f" {(name or '').lower()} "
    hit = next((wd.strip() for wd in GEARED_WORDS if wd in padded), None)
    out["geared"] = str(raw.get("leveraged", "")).upper() == "YES" or hit is not None
    out["geared_reason"] = ("profile marks the fund as geared" if str(raw.get("leveraged", "")).upper() == "YES"
                            else f"fund name contains '{hit}'" if hit else None)
    return out
