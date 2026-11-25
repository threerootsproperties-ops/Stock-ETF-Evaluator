# Methodology

Version 0.2, written 2026-11-24. This file defines what the evaluator measures, how each measure is calculated, and how results are shown. The Project reads it as reference. The scripts in the skill are the final word on any formula; where this file and a script disagree, fix this file.

Version 0.2 is built around free data. It runs on the free tiers of two data connectors, which sets the limits described below. Version 0.1 assumed a paid data plan and peer rankings; those parts are listed under "Left out of this version".

This is non-personalized research for the person running it. It is not investment advice, and nothing here knows your holdings, goals or account size.

## How a run works

1. You type a ticker.
2. The Project pulls raw data through the two connectors, one request at a time, and records the source and as-of date of every figure.
3. The raw data is saved to a file, and the scripts calculate every ratio, level and rating from that file.
4. The Project writes the PDF from the script output, following `04-report-template.md`.

No number in the report is calculated in conversation. If the scripts did not produce it, it does not appear.

## Data sources and the daily budget

| Source | Free tier limit | What the evaluator takes from it |
|---|---|---|
| Financial Modeling Prep (FMP) | 250 requests a day; full data only for a short list of very large companies, but the company profile works for any ticker | Company profile: name, sector, industry, market capitalization, whether the ticker is an ETF |
| Alpha Vantage | 25 requests a day, no faster than one per second | Income statement, balance sheet, cash flow, earnings history, the last 100 days of daily prices, full weekly price history, and ETF profiles with holdings |

A stock report uses 1 FMP request and 8 Alpha Vantage requests: three statements, earnings, daily prices, and weekly prices for the stock, SPY and the sector fund. An ETF report uses 1 FMP request and 4 Alpha Vantage requests. That allows about three stock reports or six ETF reports a day on free keys.

Tested on 2026-11-24: the FMP profile, and Alpha Vantage's income statement, daily prices, weekly prices and ETF profile. The balance sheet, cash flow and earnings requests come from the same group as the income statement and are expected to work, but had not been tested when this file was written.

Two consequences of the free tiers shape everything below. Daily prices cover only the last 100 trading days, so anything that needs a longer window uses weekly prices. And there is no budget to pull data for a group of peers, so figures are compared with the company's own history and with fixed reference points, not with a peer ranking.

## Stock or ETF

The FMP profile says whether a ticker is an ETF. Common stocks, ADRs and REITs go through the stock track. Exchange-traded funds go through the ETF track. Geared (2x, 3x), inverse and single-stock funds are identified and given a reduced report (see the ETF track).

## The three pillars

A stock report shows three pillars side by side: quality, value, and momentum and trend. Each lists its components with the current figure, the company's own 5-year median where that applies, and whether the current figure is better or worse than that median.

There is no blended score and no single grade per pillar. A composite hides disagreement between pillars, none of the professional methods reviewed uses tuned weights, and without peer data a grade would rest on thresholds nobody has tested.

A component with missing data prints "not available". Alpha Vantage reports some missing fields as the text "None" or as zero; the scripts treat both as missing for fields that cannot sensibly be zero, such as interest expense at a company with debt.

### Quality

| Component | Formula | Better when |
|---|---|---|
| Gross profitability | Gross profit / total assets | Higher |
| Operating margin | Operating income / revenue | Higher |
| Return on equity | Net income / average shareholder equity | Higher |
| Debt load | Total debt / shareholder equity | Lower |
| Earnings stability | Standard deviation of year-over-year net income growth, last 5 fiscal years | Lower |
| Cash conversion | Operating cash flow / net income, trailing 4 quarters | Higher, and above 1 |

Return on equity, debt and earnings stability are the three inputs MSCI uses for its quality indexes. Gross profitability is the measure with the strongest return evidence. Negative shareholder equity is flagged and return on equity and debt load print "not meaningful". Banks, insurers and REITs use the substitutions in `03-sector-metric-map.md`.

### Value

Value is shown as yields, not multiples, because a yield still reads correctly when earnings are negative.

| Component | Formula | Notes |
|---|---|---|
| Earnings yield | Trailing 4-quarter net income / market capitalization | Negative values are shown, not hidden |
| Free cash flow yield | (Operating cash flow - capital expenditure) / enterprise value | Skipped for banks and insurers |
| EBITDA yield | EBITDA / enterprise value | Skipped for banks, insurers and REITs |
| Sales yield | Revenue / enterprise value | The main measure when earnings and EBITDA are negative |

Enterprise value is market capitalization plus total debt minus cash and short-term investments.

Each yield is shown beside the company's own median for the last 5 fiscal years, using the year-end price from the weekly series, so a reader can see whether the stock is cheaper or dearer than its own recent norm. This says nothing about whether it is cheap against other companies.

Value is never shown alone. If earnings yield and free cash flow yield are both above their 5-year medians while return on equity is negative and price is below its 40-week average, the report prints a value-trap flag.

### Momentum and trend

| Component | Formula | Data |
|---|---|---|
| 12-1 momentum | Return from 52 weeks ago to 4 weeks ago | Weekly |
| 52-week high proximity | Last close / highest high of the last 52 weeks | Weekly and daily |
| Relative strength | Return minus SPY return over 13, 26 and 52 weeks; the same against the sector fund | Weekly |
| Trend position | Price against the 50-day average and the 40-week average, and whether the 10-week average is above the 40-week | Daily and weekly |

The 40-week average stands in for the 200-day average, which cannot be calculated from 100 days of daily data. They cover the same span.

The pillar also carries a state label. A stock is "Extended" when its last close sits 2.5 or more standard deviations above its 50-day average, using the standard deviation of the last 50 daily closes. Extended suppresses the buy range (see Levels). In the author's own testing on an earlier project this do-not-chase state was the one entry-side rule that held up, and it weakened sharply in bear markets.

## Liquidity

| Item | Formula |
|---|---|
| Dollar volume | Median of (close x volume) over the last 20 sessions |
| Amihud illiquidity | Average of (absolute daily return / dollar volume) over the last 60 sessions |
| Relative volume | Latest session volume / 50-day average volume |

Liquidity feeds the risk rating. It makes no claim about future returns.

## Levels

All levels come from price structure. The evaluator does not estimate fair value and does not print a percent gain forecast. A level is a planning reference; a price gap can pass straight through one.

| Level | Rule |
|---|---|
| Buy range | From the 50-day pivot high up to the pivot plus 2 x ATR(14). Shown only when the stock is not Extended and price is above the 40-week average. |
| Initial stop | Entry minus 2 x ATR(14), or 8% below entry, whichever is closer to entry |
| Trailing exit | The higher of the 50-day average and the most recent higher swing low, minus 1 x ATR(14) |
| Tightened trail | The same reference minus 0.5 x ATR(14) once any topping flag has been active for 5 sessions |
| Reward to risk | (Measured-move reference - entry) / (entry - stop), with the break-even win rate 1 / (1 + R) |

The pivot high is the highest daily high of the last 50 sessions. ATR(14) is Wilder's average true range over 14 sessions. All of these fit inside 100 days of daily data.

Topping flags are: a close below the 50-day average on above-average volume, 5 or more distribution days in 25 sessions, a failed breakout (a close back below the pivot by 7% or more), and a lower high followed by a lower low. The exact definitions are fixed by the scripts.

For a stock below its 40-week average, the report replaces the buy range with the nearest structure references: the last swing low held, the 50-day average and the 40-week average.

## Context block

Context items are shown with one line on their track record and never move a pillar or a level.

| Item | What is shown |
|---|---|
| Sector | Sector fund return against SPY over 13, 26 and 52 weeks |
| Market backdrop | SPY against its 40-week average |
| Earnings | The last four quarterly results against the consensus estimate, from the earnings history |
| Earnings quality | Cash conversion over 4 quarters, and the trend in share count |
| Growth | Revenue and net income growth, latest year and 3-year rate |

## ETF track

An ETF report replaces quality and value with ETF sections. Momentum and trend, liquidity, levels and the risk rating carry over unchanged.

| Section | What is checked | Source |
|---|---|---|
| Cost | Net expense ratio and portfolio turnover | Alpha Vantage ETF profile |
| Size and age | Net assets, with a warning below $50 million, and inception date | Alpha Vantage ETF profile |
| Exposure | Top 10 holdings with weights, top-10 total, effective number of holdings (1 / sum of squared weights), and sector weights | Alpha Vantage ETF profile |
| Tradability | Median dollar volume and relative volume | Daily prices |
| Structure | Whether the fund is geared | Alpha Vantage ETF profile |

Three things an ETF analyst would normally check are not in the free data and print "not available, check the issuer's website": the fund's legal structure (which decides tax treatment), the bid-ask spread, and the premium or discount to net asset value.

Geared, inverse and single-stock funds reset daily. A fund is treated as one of these when the ETF profile marks it as geared, or when its name contains terms such as "2X", "3X", "Ultra", "Inverse", "Short" or "Bear". Their report shows cost, size and tradability with a holding-period warning, sets the risk rating to the top class, and omits trend readings and levels.

## Left out of this version

These were in the original design and are not available on free data. Each is listed in the report's data section as "not included in this version".

| Item | Why it is out |
|---|---|
| Peer percentiles | Pulling statements for ten peers would use several days of free requests |
| Estimate revisions | History of analyst estimates is a paid feature |
| Short interest and days to cover | Not offered by either free source |
| Institutional holdings and insider activity | Alpha Vantage lists requests for both, but they were not tested and would add to the daily budget |
| Next earnings date | The free earnings history shows past reports only |
| Analyst price targets | Free only for the largest companies |

## Rules that apply everywhere

Every figure carries its source and as-of date. Missing data prints "not available"; the evaluator never fills a gap with an estimate or a generic ratio. Each report prints the methodology and script versions it was built with, so two reports can be compared.
