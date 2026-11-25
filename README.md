# Stock and ETF Evaluator

A Claude Project that takes a ticker symbol and returns a PDF evaluation of that US-listed stock or ETF: four evidence-backed pillars, a risk rating from 1 to 5, and buy, stop and exit levels based on price structure.

This repository holds everything needed to rebuild the Project in your own Claude subscription.

**Status: in progress.** The reference files are written. The calculation scripts and the data connection are not built yet, so the Project cannot produce a report today. This page will be updated as each piece lands.

Read [DISCLAIMER.md](DISCLAIMER.md) before using anything here. This is a research tool, not investment advice.

## What the report contains

A stock report shows quality, value, momentum and trend, and estimate revisions side by side as percentiles against sector peers. There is no single blended score, because a composite hides the places where the pillars disagree. Below the pillars come the risk rating with the reasons for it, the price levels with a chart, liquidity and positioning, and a context section.

An ETF report replaces the company pillars with fund structure, cost, tradability, closure risk and holdings exposure.

Every figure carries its source and date. Missing data prints "not available". The report never forecasts a price or a percent gain.

## How it is built

| Piece | What it does | Status |
|---|---|---|
| Project description | Tells Claude the job and the rules | Written, below |
| Reference files | Define the method, the risk rating, sector rules, the report layout and the evidence | Written, in `reference/` |
| Skill with scripts | Calculates every number and builds the PDF | Not built |
| Data connector | Supplies prices, financials and estimates | Not chosen |

Claude writes the short prose in each report. Every number comes from a script, so two reports on the same ticker and date match.

## Reference files

| File | Contents |
|---|---|
| [01-methodology.md](reference/01-methodology.md) | The pillars, formulas, peer ranking, levels and the ETF track |
| [02-risk-rating.md](reference/02-risk-rating.md) | How the 1 to 5 risk rating is built |
| [03-sector-metric-map.md](reference/03-sector-metric-map.md) | Which metrics apply to banks, insurers, REITs, software and other groups |
| [04-report-template.md](reference/04-report-template.md) | The PDF layout and wording rules |
| [05-evidence-table.md](reference/05-evidence-table.md) | What published research says about each factor and how the evaluator treats it |

## Setup

These steps work today as far as they go. Steps 4 and 5 will be filled in when the scripts and connector are ready.

1. In Claude, create a new project and name it `Stock and ETF Evaluator`.
2. Paste the text under "Project description" below into the description or instructions field.
3. Add the five files from `reference/` as project context.
4. Install the evaluator skill. (Not available yet.)
5. Connect a market data source. (Instructions to come. You will need your own account with a data vendor; this repository contains no data and no API keys.)
6. Open the project and type a ticker.

### Project description

```
When I type a ticker symbol, produce a PDF evaluation of that US-listed stock or ETF.

For every ticker: pull current data through the connected data source, run the
evaluation scripts, and build the PDF from the script output. Never calculate a
ratio, level, or rating in conversation; every number in the report comes from a
script.

Follow the reference files: 01-methodology for what is measured, 02-risk-rating
for the risk class, 03-sector-metric-map for sector rules, 04-report-template for
the layout and wording, and 05-evidence-table for how much weight each factor
deserves.

Show the date and source of every data point. If data is missing, print "not
available" and never substitute an estimate. Do not give a percent gain forecast
or a fair-value price. This is non-personalized research, not investment advice.
```

## What you need

A paid Claude plan is recommended so the project can search its reference files and run code. Price data can start on a free vendor tier. Financial statements, analyst estimates and ETF holdings need a paid data plan, roughly $29 to $139 a month depending on the vendor and tier; check current prices with the vendor before subscribing.

## Limits

The factors shown come from published research on large groups of stocks, and published effects tend to shrink after publication. None of it shows that a factor predicts what one stock will do. The thresholds in the risk rating are design choices that have not been tested. Levels are planning references drawn from past prices, and a price can gap through them. Data from any vendor can be late or wrong.

## License

Released under the [MIT License](LICENSE). You are free to copy, change and share anything here, as long as the copyright notice stays with it.
