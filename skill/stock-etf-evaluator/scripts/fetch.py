#!/usr/bin/env python3
"""Download the raw data for one ticker straight from Alpha Vantage.

  ALPHAVANTAGE_API_KEY=... python fetch.py stock BE RUN_DIR --sector-fund XLI
  ALPHAVANTAGE_API_KEY=... python fetch.py etf   XLK RUN_DIR

Files are saved into RUN_DIR under the names evaluate.py expects. Requests go
out one at a time with a pause between them, because the free tier rejects
anything faster than one per second and allows 25 a day. A stock uses 8
requests and an ETF uses 4.

This only works where the code sandbox is allowed to reach
www.alphavantage.co. If it is not, the script says so and SKILL.md describes
the connector route.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://www.alphavantage.co/query"
PAUSE = 1.6


def call(params, key):
    url = BASE + "?" + urllib.parse.urlencode({**params, "apikey": key})
    req = urllib.request.Request(url, headers={"User-Agent": "stock-etf-evaluator/0.2"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} from Alpha Vantage")
    except (urllib.error.URLError, OSError) as e:
        raise ConnectionError(f"could not reach www.alphavantage.co ({e}). The sandbox may not be allowed to "
                              f"call outside sites; use the connector route in SKILL.md.")


def problem_in(text):
    """Alpha Vantage reports limits and errors inside a 200 response."""
    t = text.lstrip()
    if not t.startswith("{"):
        return None
    try:
        obj = json.loads(t)
    except json.JSONDecodeError:
        return None
    for k in ("Error Message", "Information", "Note"):
        if k in obj and len(obj) <= 2:
            return f"{k}: {obj[k]}"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["stock", "etf"])
    ap.add_argument("symbol")
    ap.add_argument("run_dir")
    ap.add_argument("--sector-fund", default=None, help="sector comparison fund, for stocks")
    ap.add_argument("--benchmark", default="SPY")
    a = ap.parse_args()
    key = os.environ.get("ALPHAVANTAGE_API_KEY", "").strip()
    if not key:
        sys.exit("Set ALPHAVANTAGE_API_KEY before running. Never write the key into a file in the repository.")
    sym = a.symbol.upper()
    os.makedirs(a.run_dir, exist_ok=True)

    daily = {"function": "TIME_SERIES_DAILY", "symbol": sym, "outputsize": "compact", "datatype": "csv"}
    weekly = lambda s: {"function": "TIME_SERIES_WEEKLY_ADJUSTED", "symbol": s, "datatype": "csv"}  # noqa: E731
    jobs = [("daily.csv", daily), ("weekly.csv", weekly(sym)), ("spy_weekly.csv", weekly(a.benchmark))]
    if a.kind == "stock":
        if a.sector_fund and a.sector_fund.lower() != "none":
            jobs.append(("sector_weekly.csv", weekly(a.sector_fund.upper())))
        jobs += [("income.json", {"function": "INCOME_STATEMENT", "symbol": sym}),
                 ("balance.json", {"function": "BALANCE_SHEET", "symbol": sym}),
                 ("cashflow.json", {"function": "CASH_FLOW", "symbol": sym}),
                 ("earnings.json", {"function": "EARNINGS", "symbol": sym})]
    else:
        jobs.append(("etf_profile.json", {"function": "ETF_PROFILE", "symbol": sym}))

    saved, failed = [], []
    for i, (name, params) in enumerate(jobs):
        if i:
            time.sleep(PAUSE)
        try:
            text = call(params, key)
        except ConnectionError as e:
            sys.exit(f"STOPPED: {e}")
        except RuntimeError as e:
            failed.append(f"{name}: {e}")
            continue
        bad = problem_in(text)
        if bad or len(text.strip()) < 20 or text.strip() == "{}":
            failed.append(f"{name}: {bad or 'empty response'}")
            if bad and ("25 requests per day" in bad or "rate limit" in bad.lower()):
                failed.append("Daily or per-second limit reached; stopping so no more requests are spent.")
                break
            continue
        with open(os.path.join(a.run_dir, name), "w", encoding="utf-8") as f:
            f.write(text)
        saved.append(name)

    print(f"Requests sent: {len(saved) + len([f for f in failed if ':' in f and not f.startswith('Daily')])}")
    print("Saved: " + (", ".join(saved) or "nothing"))
    if failed:
        print("Not saved:")
        for f in failed:
            print("  - " + f)
        sys.exit(1 if not saved else 0)


if __name__ == "__main__":
    main()
