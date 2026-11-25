# Stock and ETF Evaluator

A Claude Project that takes a ticker symbol and returns a PDF evaluation of that US-listed stock or ETF: three evidence-backed pillars, a risk rating from 1 to 5, and buy, stop and exit levels based on price structure.

It runs on free data. You need a Claude subscription and two free data accounts, and nothing else.

This repository holds everything needed to rebuild the Project in your own Claude subscription.

**Status: first working version.** The reference files, the scripts and the skill are written. The scripts have been run end to end on two stocks and one ETF, with data pulled through the connectors. The whole thing has not yet been run inside a Claude Project, so expect rough edges.

Read [DISCLAIMER.md](DISCLAIMER.md) before using anything here. This is a research tool, not investment advice.

## What the report contains

A stock report shows quality, value, and momentum and trend side by side. Each figure is set beside the company's own five-year history, so you can see whether it is better or worse than its recent norm. There is no single blended score, because a composite hides the places where the pillars disagree. Below the pillars come the risk rating with the reasons for it, the price levels with charts, liquidity, and a context section.

An ETF report replaces the company pillars with cost, size, and holdings exposure.

Every figure carries its source and date. Missing data prints "not available". The report never forecasts a price or a percent gain.

## What free data costs you

| Limit | Detail |
|---|---|
| About three stock reports a day | Alpha Vantage's free key allows 25 requests a day and a stock report uses 8. ETF reports use 4, so about six a day. |
| No comparison with peer companies | Pulling data for ten peers would use several days of requests. Figures are compared with the company's own history. |
| No analyst estimate revisions, short interest, insider or institutional data | These are paid features or were left out to protect the daily budget. |
| Some ETF checks are missing | Legal structure, bid-ask spread and premium or discount to net asset value are not in the free data. The report tells you to check the issuer's website. |

## How it is built

| Piece | What it does | Status |
|---|---|---|
| Project description | Tells Claude the job and the rules | Written, below |
| Reference files | Define the method, the risk rating, sector rules, the report layout and the evidence | Written, in `reference/` |
| Data sources | Financial Modeling Prep for company profiles, Alpha Vantage for statements, prices and ETF holdings | Chosen and tested |
| Skill with scripts | Downloads the data, calculates every number and builds the PDF | Written, in `skill/` |

Claude writes the short prose in each report. Every number comes from a script, so two reports on the same ticker and date match.

## Reference files

| File | Contents |
|---|---|
| [01-methodology.md](reference/01-methodology.md) | Data sources, the pillars, formulas, levels and the ETF track |
| [02-risk-rating.md](reference/02-risk-rating.md) | How the 1 to 5 risk rating is built |
| [03-sector-metric-map.md](reference/03-sector-metric-map.md) | Which metrics apply to banks, insurers, REITs, software and other groups |
| [04-report-template.md](reference/04-report-template.md) | The PDF layout and wording rules |
| [05-evidence-table.md](reference/05-evidence-table.md) | What published research says about each factor and how the evaluator treats it |

## Setup

1. Create a free account at financialmodelingprep.com and a free API key at alphavantage.co. Store both keys in a password manager.
2. In Claude, connect the FMP connector and the Alpha Vantage connector from the connector directory. Each asks for your key in its own sign-in screen.
3. Create a new project and name it `Stock and ETF Evaluator`.
4. Paste the text under "Project description" below into the project's instructions.
5. Add the five files from `reference/` as project context.
6. Install the skill. Zip the `skill/stock-etf-evaluator` folder and upload it in Claude's skill settings.
7. Open the project and type a ticker.

Your keys live only inside the two connectors. Never put a key in this repository or in anything you share. If a key is ever exposed, request a new free one and replace it.

There is an optional faster route. If you add a line `ALPHAVANTAGE_API_KEY=your key` to your own project's instructions, the skill downloads the data with a script instead of through the connector. That needs Claude's code sandbox to be allowed to reach `www.alphavantage.co`, and it puts your key in your project's instructions, which only you can see.

### Project description

```
When I type a ticker symbol, produce a PDF evaluation of that US-listed stock or ETF.

For every ticker: use the stock-etf-evaluator skill. It reads the company profile
through the FMP connector, pulls the rest through the Alpha Vantage connector,
runs the evaluation scripts, and builds the PDF from the script output. Never
calculate a ratio, level, or rating in conversation; every number in the report
comes from a script.

The free Alpha Vantage tier allows 25 requests a day and one per second. A
stock report uses 8 and an ETF report uses 4. Send no others.

Follow the reference files: 01-methodology for what is measured and where the
data comes from, 02-risk-rating for the risk class, 03-sector-metric-map for
sector rules, 04-report-template for the layout and wording, and
05-evidence-table for how much weight each factor deserves.

Show the date and source of every data point. If data is missing, print "not
available" and never substitute an estimate. Do not give a percent gain forecast
or a fair-value price. This is non-personalized research, not investment advice.
```

## Limits

The factors shown come from published research on large groups of stocks, and published effects tend to shrink after publication. None of it shows that a factor predicts what one stock will do. The thresholds in the risk rating are design choices that have not been tested. Levels are planning references drawn from past prices, and a price can gap through them. Data from any vendor can be late or wrong, and free tiers can change or be withdrawn without notice.

## License

Released under the [MIT License](LICENSE). You are free to copy, change and share anything here, as long as the copyright notice stays with it.
