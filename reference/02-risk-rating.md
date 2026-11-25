# Risk rating specification

Version 0.1, written 2026-11-24. The risk rating is a class from 1 (lowest) to 5 (highest) that describes how rough the ride has been and what could make it rougher. It says nothing about expected return. A high rating marks variance, not opportunity.

## Design

The rating starts from the stock's own volatility and can only be raised from there. A strong balance sheet never lowers it. This follows the pattern of the EU's risk indicator for retail investment products, where a volatility class is the base and a credit overlay can raise the result but never reduce it ([Regulation (EU) 2017/653, Annex II](https://eur-lex.europa.eu/eli/reg_del/2017/653/oj)). Value Line's Safety rank combines price stability with financial strength in a similar way ([Value Line](https://www3.valueline.com/vlu/4-safety.html)).

No regulator or vendor publishes this exact scale. The base bands borrow the EU regulation's volatility boundaries at 12%, 20% and 30%. Everything else in this file is a design choice, and it has not been tested for predictive value.

## Step 1: base class from volatility

Annualized volatility is the standard deviation of daily log returns multiplied by the square root of 252, using up to 5 years of history. At least 2 years are required; with less, the rating prints "not available, insufficient history".

| Annualized volatility | Base class |
|---|---|
| Below 12% | 1 |
| 12% to below 20% | 2 |
| 20% to below 30% | 3 |
| 30% to below 50% | 4 |
| 50% and above | 5 |

The EU regulation uses a "VaR-equivalent volatility" that also accounts for skew and fat tails. This specification uses plain volatility because it is easier to check by hand. The report prints the maximum drawdown over the same window beside the class so tail behavior is still visible.

A stock whose history contains no market decline of 20% or more gets the note "history includes no bear market; the class may understate risk".

## Step 2: notches

Each group below can add at most one notch, however many of its conditions are met. The total is capped at class 5.

| Group | Adds one notch when any condition is true |
|---|---|
| Balance sheet | Negative net income over the trailing 12 months; operating income less than 2 times interest expense; total debt more than 4 times EBITDA; negative shareholder equity |
| Liquidity | Median 20-day dollar volume below $5 million; share price below $5 |
| Crowding | Days to cover above 10; short interest above 20% of float |
| Market backdrop | SPY closing below its 200-day average |

Banks, insurers and REITs skip the debt and interest tests, which do not suit their balance sheets, and use the tests in `03-sector-metric-map.md`.

For ETFs the balance sheet and crowding groups are replaced by a structure group, which adds one notch when the top 10 holdings exceed 50% of assets, when assets are below $50 million, or when the fund is an exchange-traded note.

## Step 3: overrides

Geared, inverse and single-stock funds are set to class 5 regardless of the steps above.

## Step 4: flags that do not change the class

| Flag | Condition |
|---|---|
| Earnings event | Next earnings report within 10 trading days |
| Estimate uncertainty | Forecast dispersion in the top fifth of the peer group |
| Stale data | Any input older than its expected refresh cycle |

## What the report prints

The report shows the class, the base class, each notch with the figure that triggered it, the annualized volatility, the maximum drawdown and the length of history used. A reader should be able to rebuild the class from the printed inputs.

Example: "Risk 4 of 5. Base class 3 (volatility 27% over 5 years, maximum drawdown 41%). Plus 1 for balance sheet (interest cover 1.4x). Flag: earnings in 6 trading days."

## Known limits

Past volatility understates risk for young companies and for names that have not yet lived through a downturn. The notch thresholds are round numbers chosen for clarity and should be reviewed once there are 50 or more reports to compare against what happened next. The rating does not measure valuation risk, fraud, or single-event risk such as a drug trial result.
