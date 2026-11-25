#!/usr/bin/env python3
"""Stock and ETF Evaluator: command line entry point.

  python evaluate.py sector-fund "Industrials"     print the comparison fund for a sector
  python evaluate.py compute RUN_DIR               calculate everything, write results.json
  python evaluate.py report  RUN_DIR               build the PDF from results.json

RUN_DIR holds the raw data files listed in SKILL.md. Nothing here calls the
network; see fetch.py for that.
"""
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd  # noqa: E402

import calc  # noqa: E402
import loader  # noqa: E402

VERSION = {"methodology": "0.3", "scripts": "0.3.0"}

NOT_INCLUDED_STOCK = ("comparison with peer companies, analyst estimate revisions, short interest, "
                      "institutional and insider activity, the next earnings date, and analyst price targets")
NOT_AVAILABLE_ETF = ("legal structure and tax treatment, bid-ask spread, premium or discount to net asset value, "
                     "and tracking difference against the index")


def compute(run_dir):
    problems, warnings = [], []
    profile = loader.read_json(run_dir, "profile")
    if isinstance(profile, list) and profile:
        profile = profile[0]
    if not profile:
        sys.exit("profile.json is missing. It must hold symbol, companyName, sector, industry, marketCap, price and isEtf.")
    symbol = profile.get("symbol", "?").upper()
    is_etf = bool(profile.get("isEtf")) or bool(profile.get("isFund"))

    daily = loader.read_prices(run_dir, "daily")
    weekly = loader.read_prices(run_dir, "weekly")
    spy_w = loader.read_prices(run_dir, "spy_weekly")
    sec_w = loader.read_prices(run_dir, "sector_weekly")
    problems += loader.check_prices(daily, "daily", 60)
    problems += loader.check_prices(weekly, "weekly", 53)
    if spy_w is None:
        warnings.append("spy_weekly file not found: comparisons with SPY and the market backdrop test are not available.")
    if sec_w is None and not is_etf:
        warnings.append("sector_weekly file not found: comparisons with the sector fund are not available.")
    if daily is None or weekly is None or [p for p in problems if "need at least" in p]:
        sys.exit("Cannot continue:\n  " + "\n  ".join(problems))
    warnings += loader.apply_splits_to_daily(daily, weekly)
    for sp in weekly.attrs.get("splits") or []:
        if pd.Timestamp(sp["week_ending"]) > weekly.index[-1] - pd.Timedelta(days=5 * 366):
            warnings.append(f"Stock split of {sp['ratio']:g}-for-1 in the week ending {sp['week_ending']}; price history is restated for it.")
    if abs(daily["close"].iloc[-1] / weekly["close"].iloc[-1] - 1) > 0.02 and daily.index[-1] == weekly.index[-1]:
        problems.append("daily and weekly files disagree on the latest close by more than 2%")
    px = loader.num(profile.get("price"))
    if px and abs(daily["close"].iloc[-1] / px - 1) > 0.10:
        warnings.append(f"Profile price ({px}) differs from the latest daily close ({daily['close'].iloc[-1]}) by more than 10%.")
    today = dt.date.today()
    if (today - daily.index[-1].date()).days > 5:
        warnings.append(f"Stale data: the latest daily price is from {daily.index[-1].date()}.")

    res = {"symbol": symbol, "name": profile.get("companyName") or profile.get("name"),
           "sector": profile.get("sector"), "industry": profile.get("industry"),
           "market_cap": loader.num(profile.get("marketCap")), "is_etf": is_etf,
           "report_date": str(today), "version": VERSION, "sources": [], "not_available": []}
    res["sources"].append({"item": "Company profile", "source": profile.get("source", "FMP company profile"),
                           "as_of": profile.get("asOf", str(today))})
    res["sources"].append({"item": "Daily prices (last 100 sessions)", "source": "Alpha Vantage TIME_SERIES_DAILY",
                           "as_of": str(daily.index[-1].date())})
    res["sources"].append({"item": "Weekly prices", "source": "Alpha Vantage TIME_SERIES_WEEKLY_ADJUSTED",
                           "as_of": str(weekly.index[-1].date())})

    mom = calc.momentum(daily, weekly, spy_w, sec_w)
    liq = calc.liquidity(daily)
    res["momentum"], res["liquidity"] = mom, liq

    if is_etf:
        raw = loader.read_json(run_dir, "etf_profile")
        etf = calc.etf_profile(raw, res["name"]) if raw else None
        if etf is None:
            res["not_available"].append("ETF profile (cost, size and holdings)")
        else:
            res["sources"].append({"item": "ETF profile and holdings", "source": "Alpha Vantage ETF_PROFILE",
                                   "as_of": (etf.get("last_updated") or "")[:10] or str(today)})
        geared = bool(etf and etf.get("geared"))
        res["etf"], res["geared"] = etf, geared
        res["risk"] = calc.risk(weekly, spy_w, liq, "etf", None, None, None, is_etf=True, etf=etf, geared=geared,
                                today=daily.index[-1])
        res["levels"] = None if geared else calc.levels(daily, mom)
        res["standing_note"] = "Not available in the free data, check the issuer's website: " + NOT_AVAILABLE_ETF + "."
    else:
        group = calc.company_group(res["sector"], res["industry"])
        res["group"] = group
        res["sector_fund"] = calc.sector_fund(res["sector"])
        inc_a, inc_q = loader.read_statement(run_dir, "income")
        bal_a, bal_q = loader.read_statement(run_dir, "balance")
        cf_a, cf_q = loader.read_statement(run_dir, "cashflow")
        earn = loader.read_json(run_dir, "earnings") or {}
        earnings = earn.get("quarterlyEarnings", [])
        for nm, tab in (("Income statement", inc_q), ("Balance sheet", bal_q), ("Cash flow statement", cf_q)):
            if tab is None:
                res["not_available"].append(nm)
            else:
                res["sources"].append({"item": nm, "source": "Alpha Vantage", "as_of": f"quarter ended {tab.index[-1].date()}"})
                if (daily.index[-1] - tab.index[-1]).days > 200:
                    warnings.append(f"Stale data: the latest {nm.lower()} is for the quarter ended {tab.index[-1].date()}.")
        if not earnings:
            res["not_available"].append("Earnings history")
        else:
            res["sources"].append({"item": "Earnings history", "source": "Alpha Vantage EARNINGS",
                                   "as_of": earnings[0].get("reportedDate")})
        if inc_a is not None and inc_q is not None:
            res["quality"] = calc.quality(inc_a, inc_q, bal_a, bal_q, cf_q, group)
            res["value"] = calc.value(inc_a, inc_q, bal_a, bal_q, cf_a, cf_q, weekly, res["market_cap"], group)
            vr = {r["name"].split(" (")[0]: r for r in res["value"]["rows"]}
            roe = next((r for r in res["quality"] if r["name"].startswith("Return on equity")), {})
            ey, fy = vr.get("Earnings yield", {}), vr.get("Free cash flow yield", {})
            res["value_trap"] = bool(ey.get("vs_history") == "better" and fy.get("vs_history") == "better"
                                     and roe.get("current") is not None and roe["current"] < 0
                                     and mom.get("above_40w") is False)
        else:
            res["quality"], res["value"], res["value_trap"] = None, None, False
        res["context"] = calc.context(inc_a, inc_q, bal_q, earnings, spy_w, sec_w)
        res["risk"] = calc.risk(weekly, spy_w, liq, group, inc_q, bal_q, earnings, today=daily.index[-1])
        res["levels"] = calc.levels(daily, mom)
        res["standing_note"] = "Not included in this version: " + NOT_INCLUDED_STOCK + "."

    res["problems"], res["warnings"] = problems, warnings
    with open(os.path.join(run_dir, "results.json"), "w") as f:
        json.dump(res, f, indent=1, default=str)
    import report
    facts = report.facts_text(res)
    with open(os.path.join(run_dir, "facts.txt"), "w") as f:
        f.write(facts)
    print(facts)
    if problems:
        print("\nPROBLEMS FOUND IN THE DATA (fix the files and run compute again):")
        for p in problems:
            print("  - " + p)


def build_report(run_dir):
    import report
    with open(os.path.join(run_dir, "results.json")) as f:
        res = json.load(f)
    summary = None
    sp = os.path.join(run_dir, "summary.txt")
    if os.path.exists(sp):
        summary = open(sp, encoding="utf-8").read().strip()
    daily = loader.read_prices(run_dir, "daily")
    weekly = loader.read_prices(run_dir, "weekly")
    loader.apply_splits_to_daily(daily, weekly)
    out = report.build_pdf(res, daily, weekly, summary, run_dir)
    print("PDF written:", out)


def main(argv):
    if len(argv) >= 3 and argv[1] == "sector-fund":
        print(calc.sector_fund(argv[2]) or "none")
    elif len(argv) >= 3 and argv[1] == "compute":
        compute(argv[2])
    elif len(argv) >= 3 and argv[1] == "report":
        build_report(argv[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
