---
name: stock-etf-evaluator
description: Builds a PDF evaluation of a US stock or ETF from a ticker symbol. Use when the user types a ticker or asks to evaluate, analyze or get a report on a stock or ETF.
---

# Stock and ETF Evaluator

Turn one ticker into a PDF report: three pillars (quality, value, momentum and trend), a risk rating from 1 to 5, and price levels. Scripts do every calculation. You gather the data, run the scripts, and write one summary paragraph.

## Rules that never bend

1. Every number in the report comes from script output. Do not calculate, round, estimate or correct a figure yourself.
2. If data is missing, the report says "not available". Never fill a gap from memory or from a web search.
3. No price forecast, no percent gain estimate, no fair-value price, and no advice to buy or sell.
4. Alpha Vantage's free key allows 25 requests a day and one per second. Send only the requests listed here, one at a time. A stock uses 8, an ETF uses 4.
5. Never print an API key, write one to a file, or put one in the report.

## Step 1: find the scripts

If a `scripts` folder sits beside this file, use it. Otherwise fetch the public copy:

```
git clone --depth 1 https://github.com/threerootsproperties-ops/Stock-ETF-Evaluator /tmp/sev
SCRIPTS=/tmp/sev/skill/stock-etf-evaluator/scripts
```

The scripts need pandas, numpy, matplotlib and reportlab. Install any that are missing with pip.

Make a working folder for the run, for example `RUN=/tmp/run-TICKER`.

## Step 2: company profile

Call the FMP connector's company tool with endpoint `profile-symbol` and the ticker. Write `$RUN/profile.json` holding exactly these fields copied from the result: `symbol`, `companyName`, `sector`, `industry`, `marketCap`, `price`, `isEtf`. Add `"source": "FMP company profile"` and `"asOf"` with today's date.

If the profile comes back empty, the ticker is not recognized. Tell the user and stop.

`isEtf` decides the track. For a stock, get the sector comparison fund:

```
python $SCRIPTS/evaluate.py sector-fund "SECTOR NAME FROM THE PROFILE"
```

## Step 3: download the data

Use the direct route first. It needs the user's Alpha Vantage key, which they keep in the project instructions as `ALPHAVANTAGE_API_KEY`. Pass it on the command line as an environment variable and nowhere else.

```
ALPHAVANTAGE_API_KEY=... python $SCRIPTS/fetch.py stock TICKER $RUN --sector-fund XLI
ALPHAVANTAGE_API_KEY=... python $SCRIPTS/fetch.py etf   TICKER $RUN
```

Read what it prints. "Saved" lists the files it wrote. If a file is listed under "Not saved" with a daily-limit message, tell the user the free quota is used up for today and stop. Do not retry.

If the script prints "STOPPED: could not reach www.alphavantage.co", or no key is in the project instructions, use the connector route below.

### Connector route (fallback)

Call the Alpha Vantage connector tools one at a time, never in parallel. Pass `return_full_data: true` on each call.

| File to create in $RUN | Tool | Arguments |
|---|---|---|
| `daily.csv` | TIME_SERIES_DAILY | symbol, outputsize `compact` |
| `weekly.csv` | TIME_SERIES_WEEKLY_ADJUSTED | symbol |
| `spy_weekly.csv` | TIME_SERIES_WEEKLY_ADJUSTED | symbol `SPY` |
| `sector_weekly.csv` (stocks) | TIME_SERIES_WEEKLY_ADJUSTED | the sector fund |
| `income.json` (stocks) | INCOME_STATEMENT | symbol |
| `balance.json` (stocks) | BALANCE_SHEET | symbol |
| `cashflow.json` (stocks) | CASH_FLOW | symbol |
| `earnings.json` (stocks) | EARNINGS | symbol |
| `etf_profile.json` (ETFs) | ETF_PROFILE | symbol |

When a result was saved to a file by the app, copy that file into `$RUN` under the name above. The scripts read the connector's wrapper format as it is.

When a result arrived in the conversation instead, write the file yourself, copying values exactly:

- Price files: keep the header row. For `daily.csv` write every row. For weekly files write the most recent 265 rows; the columns `timestamp`, `high`, `close` and `adjusted close` are enough.
- Statement files: write JSON with `annualReports` (most recent 6) and `quarterlyReports` (most recent 8), keeping the original field names and the text "None" where it appears. The scripts use these fields: `fiscalDateEnding`, `totalRevenue`, `grossProfit`, `operatingIncome`, `interestExpense`, `depreciationAndAmortization`, `ebitda`, `netIncome`, `totalAssets`, `totalShareholderEquity`, `shortLongTermDebtTotal`, `shortTermDebt`, `longTermDebt`, `cashAndShortTermInvestments`, `cashAndCashEquivalentsAtCarryingValue`, `goodwill`, `intangibleAssetsExcludingGoodwill`, `commonStockSharesOutstanding`, `operatingCashflow`, `capitalExpenditures`.
- `earnings.json`: the most recent 4 entries of `quarterlyEarnings`.
- `etf_profile.json`: every top-level field, all sectors, and all holdings if there are 60 or fewer, otherwise the largest 60.

If a tool returns "premium endpoint" or a rate-limit message, do not retry it. Leave that file out; the report will mark the item as not available.

## Step 4: calculate

```
python $SCRIPTS/evaluate.py compute $RUN
```

This prints a fact sheet and saves it as `$RUN/facts.txt`. If it prints "PROBLEMS FOUND IN THE DATA", a file was written wrongly. Fix the file from the original tool result and run compute again. If it prints "Cannot continue", tell the user which data is missing and stop.

## Step 5: write the summary

Write `$RUN/summary.txt`: one paragraph of 4 to 6 sentences, using only figures that appear in the fact sheet. Cover, in this order:

1. What the pillars show and where they disagree. For an ETF: what it holds, how concentrated it is, and what it costs.
2. The risk class and its main driver.
3. Where price sits against the levels.
4. The most important flag or warning.

Wording rules:

- Describe; do not recommend. Never write "buy", "sell", "should", "undervalued" or "overvalued" as a conclusion. "Buy range" and "trailing exit" are fine as the names of levels.
- "Better than its own history" must not become "good". "Cheaper than its own history" must not become "cheap".
- When pillars disagree, say so. Do not average them into a verdict.
- No em dashes.

## Step 6: build and deliver the PDF

```
python $SCRIPTS/evaluate.py report $RUN
```

Send the user the PDF it names. In the chat, add two or three sentences: the risk class, whether a buy range is shown, anything that was not available, and how many Alpha Vantage requests the run used. Do not repeat the report.

## Reduced reports

When the fact sheet says "GEARED OR INVERSE FUND", the scripts already drop trend readings and levels and set the risk class to 5. Write the summary about cost, size and the daily reset only.

## When something fails

Say plainly what failed and what the user can do. Common cases: the daily quota is used up (wait until tomorrow), the ticker has under two years of history (no risk rating), or the FMP connector is not connected (the profile cannot be read, so the run cannot start).
