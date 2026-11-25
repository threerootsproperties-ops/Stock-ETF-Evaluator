# Risk rating specification

Version 0.3, written 2026-11-24. The risk rating is a class from 1 (lowest) to 5 (highest) that describes how rough the ride has been and what could make it rougher. It says nothing about expected return. A high rating marks variance, not opportunity.

This version calculates volatility from weekly prices, because the free data supplies only 100 days of daily history, and drops the crowding group, because short interest is not available free. Version 0.3 changed the market backdrop from a notch to a flag: in testing it raised every stock and fund by one class at the same time, which pushed unlike securities to the same top rating.

## Design

The rating starts from the stock's own volatility and can only be raised from there. A strong balance sheet never lowers it. This follows the pattern of the EU's risk indicator for retail investment products, where a volatility class is the base and a credit overlay can raise the result but never reduce it ([Regulation (EU) 2017/653, Annex II](https://eur-lex.europa.eu/eli/reg_del/2017/653/oj)). Value Line's Safety rank combines price stability with financial strength in a similar way ([Value Line](https://www3.valueline.com/vlu/4-safety.html)).

No regulator or vendor publishes this exact scale. The base bands borrow the EU regulation's volatility boundaries at 12%, 20% and 30%. Everything else in this file is a design choice, and it has not been tested for predictive value.

## Step 1: base class from volatility

Annualized volatility is the standard deviation of weekly log returns, calculated from adjusted weekly closes, multiplied by the square root of 52. The window is the last 5 years, or the full history if shorter.

| Annualized volatility | Base class |
|---|---|
| Below 12% | 1 |
| 12% to below 20% | 2 |
| 20% to below 30% | 3 |
| 30% to below 50% | 4 |
| 50% and above | 5 |

At least 2 years of weekly history are required; with less, the rating prints "not available, insufficient history". The EU regulation asks for 4 years when weekly data is used, so a rating built on 2 to 4 years carries the note "short history; the class may understate risk".

The EU regulation uses a "VaR-equivalent volatility" that also accounts for skew and fat tails. This specification uses plain volatility because it is easier to check by hand. The report prints the maximum drawdown over the same window beside the class so tail behavior is still visible. Drawdown is measured on weekly closes, so it understates declines that reversed within a week.

A stock whose window contains no decline of 20% or more in SPY gets the note "history includes no bear market; the class may understate risk".

## Step 2: notches

Each group below can add at most one notch, however many of its conditions are met. The total is capped at class 5.

| Group | Adds one notch when any condition is true |
|---|---|
| Balance sheet | Negative net income over the trailing 4 quarters; operating income less than 2 times interest expense; total debt more than 4 times EBITDA; negative shareholder equity |
| Liquidity | Median 20-day dollar volume below $5 million (stocks only); share price below $5 |

A test whose inputs are missing is skipped and listed as "not tested", never counted as passed or failed. Interest expense reported as zero or "None" at a company with debt counts as missing.

Banks, insurers and REITs skip the debt and interest tests, which do not suit their balance sheets, and use the tests in `03-sector-metric-map.md`.

For ETFs the balance sheet group is replaced by a structure group, which adds one notch when the top 10 holdings exceed 50% of assets or when net assets are below $50 million.

## Step 3: overrides

Geared, inverse and single-stock funds are set to class 5 regardless of the steps above.

## Step 4: flags that do not change the class

| Flag | Condition |
|---|---|
| Market backdrop | SPY closing below its 40-week average. It applies to every security alike, so it informs the reader without changing the class. |
| Thin trading (ETFs) | Median 20-day dollar volume below $5 million. A fund's own volume understates how easily it trades, because its liquidity comes from the securities it holds, so for ETFs this is a flag and not a notch. The spread would settle the question and is not in the free data. |
| Recent earnings | The latest earnings report is more than 75 days old, so the next one is likely near. The exact date is not in the free data. |
| Stale data | Latest price is more than 3 trading days old, or latest statements are more than 6 months old |

## What the report prints

The report shows the class, the base class, each notch with the figure that triggered it, any tests that were skipped, the annualized volatility, the maximum drawdown and the length of history used. A reader should be able to rebuild the class from the printed inputs.

Example: "Risk 5 of 5. Base class 5 (weekly volatility 96% over 5 years, maximum drawdown 71%). Balance sheet notch triggered (trailing net income negative) but the class is already at the cap."

## Known limits

Past volatility understates risk for young companies and for names that have not yet lived through a downturn. Weekly data smooths over violent single days. The notch thresholds are round numbers chosen for clarity and should be reviewed once there are 50 or more reports to compare against what happened next. The rating does not measure valuation risk, crowding, fraud, or single-event risk such as a drug trial result.
