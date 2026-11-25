# Sector metric map

Version 0.1, written 2026-11-24. Generic ratios mislead in several sectors. This file tells the evaluator which metrics to use, which to hide, and which sector fund to compare against.

Classification comes from the data vendor's sector and industry fields. Research comparing classification systems found that GICS groups explain valuation multiples and return comovement better than SIC or NAICS codes ([Bhojraj, Lee and Oler](https://ideas.repec.org/a/bla/joares/v41y2003i5p745-774.html)). Vendor sectors follow the same eleven-sector layout closely enough for peer grouping; where a vendor's label differs, map it to the nearest row below.

## Benchmark fund by sector

| Sector | Comparison ETF |
|---|---|
| Information Technology | XLK |
| Financials | XLF |
| Health Care | XLV |
| Consumer Discretionary | XLY |
| Communication Services | XLC |
| Industrials | XLI |
| Consumer Staples | XLP |
| Energy | XLE |
| Utilities | XLU |
| Materials | XLB |
| Real Estate | XLRE |

The market benchmark is SPY. Information Technology was close to 40% of the S&P 500 in late 2026, so "relative to SPY" leans heavily toward large technology companies; the report shows the sector comparison beside it for that reason.

## Metric routing

"Use" lists what replaces or joins the default pillars. "Hide" lists default metrics that must not be shown for that group. "Usually missing" lists company-reported figures that standard data feeds rarely carry; the report prints "not available" for them and never substitutes a generic ratio.

| Group | Use | Hide | Usually missing |
|---|---|---|---|
| Default (most industrial, consumer, technology and health care companies) | The pillars as defined in `01-methodology.md` | Nothing | Nothing |
| Banks | Price / tangible book value, return on equity, net interest margin, efficiency ratio, nonperforming loans / total loans | EBITDA yield, free cash flow yield, debt load, interest cover, current ratio | Common equity tier 1 ratio, deposit mix |
| Insurers | Price / book value, return on equity, combined ratio | EBITDA yield, free cash flow yield, debt load | Reserve development, catastrophe losses |
| Equity REITs | Price / funds from operations, dividend yield, net debt / EBITDA | Earnings yield and P/E (depreciation distorts earnings) | Adjusted funds from operations, net asset value, occupancy |
| Software | Sales yield, revenue growth, free cash flow margin, Rule of 40 (revenue growth % + free cash flow margin %) | Nothing; earnings yield is shown but may be negative | Annual recurring revenue, net revenue retention |
| Loss-making growth companies in any sector | Sales yield, revenue growth, gross margin, cash runway (cash and investments / trailing 12-month operating cash burn) | Earnings yield as a ranking input | Pipeline and milestone data |
| Oil and gas producers | EBITDA yield, free cash flow yield, net debt / EBITDA | Nothing | Reserves, reserve life, breakeven price |
| Retailers | The default pillars plus inventory growth against sales growth | Nothing | Comparable-store sales |
| Semiconductors | The default pillars plus inventory days and gross margin trend | Nothing | Book-to-bill, utilization |
| Utilities | The default pillars, with dividend yield and debt shown prominently | Nothing | Allowed return on equity, rate base |

## Definitions for the sector metrics

| Metric | Formula |
|---|---|
| Net interest margin | (Interest income - interest expense) / average earning assets |
| Efficiency ratio | Non-interest expense / revenue; lower is better |
| Combined ratio | Loss ratio + expense ratio; below 100% means an underwriting profit |
| Funds from operations | Net income + real estate depreciation and amortization - gains on property sales |
| Rule of 40 | Revenue growth % + profit margin %; 40 or above is the usual benchmark |
| Cash runway | Cash and investments / trailing 12-month operating cash burn, in years |

Bank and insurer formulas follow [Corporate Finance Institute](https://corporatefinanceinstitute.com/learn/resources/wealth-management/bank-specific-ratios) and [S&P Global Market Intelligence](https://www.spglobal.com/content/dam/spglobal/mi/en/documents/solutions/p-c-insurance-industry-guide.pdf). The REIT definition follows [Nareit](https://reit.com/what-reit/glossary-reit-terms).

## Risk rating tests by sector

The balance sheet notch in `02-risk-rating.md` uses these tests in place of the debt and interest tests.

| Group | Adds the balance sheet notch when |
|---|---|
| Banks | Trailing 12-month net income is negative, or nonperforming loans exceed 3% of total loans |
| Insurers | Trailing 12-month net income is negative, or the combined ratio exceeds 105% |
| Equity REITs | Net debt exceeds 8 times EBITDA, or funds from operations are negative |

These thresholds are design choices. No published benchmark was confirmed for them.

## Known gaps

Semiconductor, biotech and energy metrics were only partly sourced in the research behind this file. Adjusted funds from operations and net revenue retention are not standardized, so comparisons across companies depend on each company's definition. The 2026 GICS review proposed splitting semiconductors and adding a financial technology group for 2027; the outcome was not confirmed when this file was written, so check the classification rows again in 2027.
