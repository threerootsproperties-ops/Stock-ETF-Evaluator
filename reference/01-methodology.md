# Methodology

Version 0.1, written 2026-11-24. This file defines what the evaluator measures, how each measure is calculated, and how results are shown. The Project reads it as reference. The scripts in the skill are the final word on any formula; where this file and a script disagree, fix this file.

This is non-personalized research for the person running it. It is not investment advice, and nothing here knows your holdings, goals or account size.

## How a run works

1. You type a ticker.
2. The Project pulls raw data through the connected data source and records the source and as-of date of every figure.
3. The raw data is saved to a file, and the scripts calculate every ratio, percentile, level and rating from that file.
4. The Project writes the PDF from the script output, following `04-report-template.md`.

No number in the report is calculated in conversation. If the scripts did not produce it, it does not appear.

## Stock or ETF

The first step is deciding which track applies. Common stocks, ADRs and REITs go through the stock track. Exchange-traded funds go through the ETF track. Exchange-traded notes, geared (2x, 3x) funds, inverse funds and single-stock funds are identified and flagged, then given a reduced report (see the ETF track).

## The four pillars

A stock report shows four pillars side by side. Each pillar is a percentile from 0 to 100 against a peer group, with its components listed underneath. There is no blended score, on purpose: a single composite hides disagreement between pillars, and none of the professional methods reviewed uses tuned weights.

Inside a pillar, every component gets equal weight. A component with missing data is dropped and the pillar says how many components it used. A pillar with fewer than two components prints "not available".

### Quality

| Component | Formula | Better when |
|---|---|---|
| Gross profitability | Gross profit / total assets | Higher |
| Operating margin | Operating income / revenue | Higher |
| Return on equity | Net income / average shareholder equity | Higher |
| Debt load | Total debt / shareholder equity | Lower |
| Earnings stability | Standard deviation of year-over-year EPS growth, last 5 fiscal years | Lower |

Return on equity, debt and earnings stability are the three inputs MSCI uses for its quality indexes. Gross profitability is the measure with the strongest return evidence. Negative shareholder equity gets the worst rank on return on equity and debt load. Banks, insurers and REITs use the substitutions in `03-sector-metric-map.md`.

### Value

Value is ranked on yields, not multiples, because a yield still sorts correctly when earnings are negative.

| Component | Formula | Notes |
|---|---|---|
| Earnings yield | Trailing 12-month EPS / price | Negative values rank last, not excluded |
| Free cash flow yield | (Operating cash flow - capital expenditure) / enterprise value | Skipped for banks and insurers |
| EBITDA yield | EBITDA / enterprise value | Skipped for banks, insurers and REITs |
| Sales yield | Revenue / enterprise value | Used when earnings and EBITDA are both negative |
| Forward earnings yield | Next fiscal year consensus EPS / price | Needs an estimates source |

The report also shows each multiple against the stock's own 5-year median, so "cheap against peers" and "cheap against its own history" can be told apart.

Value is never shown alone. If the value pillar is in the top third while quality is in the bottom quarter and price is below its 200-day average, the report prints a value-trap flag.

### Momentum and trend

| Component | Formula |
|---|---|
| 12-1 momentum | Total return from 12 months ago to 1 month ago |
| 52-week high proximity | Current price / highest close of the last 252 sessions |
| Relative strength | Return minus SPY return over 3, 6 and 12 months; the same against the sector ETF |
| Trend position | Price against the 50-day and 200-day simple averages, and whether the 50-day is above the 200-day |

Until a peer price panel is available, this pillar is shown as raw values against SPY and the sector ETF instead of a peer percentile.

The pillar also carries a state label. A stock is "Extended" when its price sits 2.5 or more standard deviations above its 50-day average. Extended suppresses the buy range (see Levels). In the author's own testing on an earlier project this do-not-chase state was the one entry-side rule that held up, and it weakened sharply in bear markets.

### Estimate revisions

| Component | Formula |
|---|---|
| Revision magnitude | Percent change in consensus EPS for the current and next fiscal year over 30 and 90 days |
| Revision breadth | (Analysts raising - analysts lowering) / analysts covering, last 30 days |
| Post-report change | Percent change in next-quarter consensus in the 30 days after the last earnings report |

This pillar needs a paid estimates source. Without one it prints "not available". Forecast dispersion (standard deviation of estimates / absolute mean) is shown as an uncertainty flag and does not enter the pillar.

## Peer groups and percentiles

Peers are companies in the same industry from the data vendor's classification, widened to the sector until there are at least 10. Each component is ranked as a percentile within the peer group, flipped where lower is better, and the pillar is the average of its component percentiles. The report also prints the market-wide percentile when the vendor supplies enough data, so a reader can see when a whole sector is expensive.

Percentiles are read in thirds: 67 and above is "strong", 34 to 66 is "middle", 33 and below is "weak". These cut points are a display convention.

## Positioning line

Positioning is one line, not a pillar, because the data is late and the effects are small.

| Item | Formula | How it is read |
|---|---|---|
| Days to cover | Short interest / 20-day average share volume | Above 10 flags squeeze risk and a crowded short |
| Short percent of float | Short interest / float | Shown beside days to cover |
| Insider buying | Open-market purchases minus sales by officers and directors, last 6 months, excluding trades marked as 10b5-1 plan trades | Net buying by 2 or more insiders is noted |
| Institutional change | Change in number of 13F holders and shares held, latest quarter against the prior one | Shown with the filing date; up to 135 days old |

The thresholds in this table are design choices, not published standards.

## Liquidity

| Item | Formula |
|---|---|
| Dollar volume | Median of (close x volume) over 20 sessions |
| Amihud illiquidity | Average of (absolute daily return / dollar volume) over 60 sessions |
| Relative volume | Today's volume / 50-day average volume |

Liquidity feeds the risk rating. It makes no claim about future returns.

## Levels

All levels come from price structure. The evaluator does not estimate fair value and does not print a percent gain forecast. A level is a planning reference; a price gap can pass straight through one.

| Level | Rule |
|---|---|
| Buy range | From the 50-day pivot high up to the pivot plus 2 x ATR(14). Shown only when the stock is not Extended and the trend position is positive. |
| Initial stop | Entry minus 2 x ATR(14), or 8% below entry, whichever is closer to entry |
| Trailing exit | The higher of the 50-day average and the most recent higher swing low, minus 1 x ATR(14) |
| Tightened trail | The same reference minus 0.5 x ATR(14) once any topping flag has fired for 5 sessions |
| Reward to risk | (Measured-move reference - entry) / (entry - stop), with the break-even win rate 1 / (1 + R) |

Topping flags are: a close below the 50-day average on above-average volume, 5 or more distribution days in 25 sessions, a failed breakout (close back below the pivot by 7% or more), and a lower high followed by a lower low. The exact definitions are fixed by the scripts.

For a stock in a downtrend, the report replaces the buy range with the nearest structure references: the last swing low held, and the 50-day and 200-day averages.

## Context block

Context items are shown with one line on their track record and never move a pillar or a level.

| Item | What is shown |
|---|---|
| Sector | Sector ETF return against SPY over 1, 3, 6 and 12 months |
| Market backdrop | SPY against its 200-day average |
| Earnings | Next report date, the last four surprises, and the average absolute move on past earnings days |
| Earnings quality | GAAP against adjusted EPS, and operating cash flow against net income over 4 quarters |
| Analyst targets | Low, median and high target, with the note that targets have historically overshot |
| Distress checks | Piotroski and Altman scores where the sector allows them |

## ETF track

An ETF report replaces the quality, value and revisions pillars with four ETF sections. Momentum and trend, liquidity, levels and the risk rating carry over, calculated on a distribution-adjusted price series.

| Section | What is checked |
|---|---|
| Structure | Legal form: open-end fund, unit investment trust, grantor trust, commodity pool, or exchange-traded note. Tax form and issuer credit risk follow from it. |
| Cost | Expense ratio, and realized tracking difference against the index when index returns are available |
| Tradability | Median dollar volume, 30-day median bid-ask spread, premium or discount to net asset value |
| Survival | Assets under management, with a warning below $50 million, and fund age |
| Exposure | Top-10 weight, effective number of holdings (1 / sum of squared weights), sector weights, and holdings-weighted earnings yield and dividend yield |

Geared, inverse and single-stock funds reset daily. Their report shows structure, cost and tradability with a holding-period warning, pins the risk rating at the top class, and omits trend scores and levels. Exchange-traded notes carry the issuer's credit risk, and the report says so in the summary.

## Rules that apply everywhere

Every figure carries its source and as-of date. Missing data prints "not available"; the evaluator never fills a gap with an estimate or a generic ratio. A figure older than its expected refresh cycle is marked stale. Each report prints the methodology and script versions it was built with, so two reports can be compared.
