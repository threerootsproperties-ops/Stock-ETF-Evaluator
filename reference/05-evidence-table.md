# Evidence table

Version 0.1, written 2026-11-24. This file records how much published evidence stands behind each factor the evaluator shows, and how the evaluator treats it as a result. It exists so the report can be honest about weight: a factor with weak evidence is shown as context and never moves a pillar.

Three cautions apply to every row. Most academic samples end between 1996 and 2016, and factor performance for 2020 to 2026 was not reviewed. Published effects shrink: across 97 predictors, average returns fell by more than half after publication ([McLean and Pontiff, via CFA Institute](https://rpc.cfainstitute.org/research/cfa-digest/2016/06/does-academic-research-destroy-stock-return-predictability-digest-summary)). And nearly all of this evidence comes from portfolios of many stocks; none of it shows that a factor predicts what one stock will do.

Treatment key: "Pillar" enters a scored pillar. "Risk" can raise the risk rating. "Context" is shown with its track record and moves nothing. "Not used" is left out.

## Fundamentals and valuation

| Factor | What the evidence says | Strength | Treatment |
|---|---|---|---|
| Gross profitability | The most profitable fifth beat the least profitable by 0.33% a month, 1963 to 2009 ([Novy-Marx](https://www.nber.org/system/files/working_papers/w15940/w15940.pdf)) | Strong | Pillar (quality) |
| Quality composites | Significant risk-adjusted returns in the US and 24 other countries ([Asness, Frazzini and Pedersen](https://papers.ssrn.com/abstract=2312432)) | Strong | Pillar (quality) |
| Value on its own | Price to book lost about half its cumulative gain after 2007 ([CFA Institute](https://rpc.cfainstitute.org/blogs/enterprising-investor/2022/fama-and-french-the-five-factor-model-revisited/)) | Weak since 2007 | Pillar (value), never shown alone |
| Value with quality and trend | Removing the bottom quarter on quality or momentum restored the value premium, 1990 to 2022, before costs ([Research Affiliates](https://www.researchaffiliates.com/content/dam/ra/publications/pdf/1013-avoiding-value-traps.pdf)) | Moderate | Value-trap flag |
| Piotroski, Altman and Beneish scores | Calibrated on narrow groups: small neglected value stocks, manufacturers, non-financial firms | Narrow | Context |
| Accruals | The anomaly decayed to roughly zero ([Green, Hand and Soliman](https://ideas.repec.org/a/inm/ormnsc/v57y2011i5p797-816.html)) | Faded | Context (earnings quality) |

## Earnings

| Factor | What the evidence says | Strength | Treatment |
|---|---|---|---|
| Estimate revisions | Upward revisions returned 1.84% the next month against 0.72% for downward, 1983 to 2001, stronger in small names ([Zhang](https://www.cis.upenn.edu/~mkearns/finread/UncertaintyAndReturns.pdf)). No recent large-cap evidence was reviewed. | Moderate, dated | Pillar (revisions) |
| Earnings surprise | Beating consensus is the norm, at about 78% of S&P 500 companies over five years ([FactSet](https://advantage.factset.com/hubfs/Website/Resources%20Section/Research%20Desk/Earnings%20Insight/EarningsInsight_111326.pdf)) | Weak as a signal | Context |
| Drift after earnings | Largely gone in large stocks since about 2006 ([Martineau](https://ideas.repec.org/a/now/jnlcfr/104.00000122.html)); still found in samples that keep the smallest stocks | Weak outside small caps | Not used |
| Forecast dispersion | Predicted lower returns in 1983 to 2000, mainly in the smallest stocks ([Diether, Malloy and Scherbina](https://www.kellogg.northwestern.edu/faculty/mcdonald/ftp/practicum/papers/dms3.pdf)) | Weak | Flag (uncertainty) |
| Adjusted against GAAP earnings | 72% of S&P 500 companies reported adjusted figures in 2025, most of them above GAAP ([Schwab](https://www.schwab.com/learn/story/gaap-vs-adjusted-earnings-know-difference)) | Descriptive | Context (earnings quality) |

## Price, volume and liquidity

| Factor | What the evidence says | Strength | Treatment |
|---|---|---|---|
| 12-month momentum | Significant across every formation and holding window in the original tests; carries crash risk after market declines ([Daniel and Moskowitz](https://www.nber.org/papers/w20439)) | Strong | Pillar (momentum) |
| 52-week high proximity | Beat past-return momentum from 1963 to 2001 without reversing ([Alpha Architect summary](https://alphaarchitect.com/the-secret-to-momentum-is-the-52-week-high/)) | Strong | Pillar (momentum) |
| Long moving-average filters | Cut the worst S&P 500 drawdown from about 83% to 50% over 1901 to 2012 with similar returns, before costs; the return edge is contested | Risk reduction only | Risk (market backdrop) and trend position |
| Stand-alone technical rules | The best of 7,846 rules failed out of sample ([Sullivan, Timmermann and White](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf)) | Not supported | Not used |
| Breakout volume | One large self-published test found high-volume breakouts gained 37.6% against 35.8% for low-volume ones ([Bulkowski](https://www.thepatternsite.com/VolumeStudy.html)) | Weak | Context (relative volume) |
| OBV, A/D line, CMF, MFI | No peer-reviewed support was found | Not supported | Not used |
| Off-exchange volume share | Most of it is dealer flow, not institutional buying ([Cboe](https://www.cboe.com/insights/posts/off-exchange-trends-beyond-sub-dollar-trading)) | Not a signal | Not used |
| Dollar volume and Amihud illiquidity | Sound measures of trading cost; no return claim | Sound as cost measures | Risk (liquidity) |
| Volatility | Scaling exposure down when volatility rises improved risk-adjusted returns in US equities ([Harvey et al.](https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf)) | Strong for risk | Risk (base class) |

## Sector and market

| Factor | What the evidence says | Strength | Treatment |
|---|---|---|---|
| Industry peer groups | Same-industry companies share valuation and return behavior, most clearly among large firms | Strong | Peer percentiles |
| Industry momentum | About 0.43% a month from 1963 to 1995, less after adjustment ([Moskowitz and Grinblatt](https://scispace.com/pdf/do-industries-explain-momentum-191hzflc9e.pdf)); no recent replication reviewed | Moderate, dated | Context (sector strength) |
| Business-cycle rotation | Even perfect foresight of the cycle earned nothing significant after costs, 1948 to 2018 ([Molchanov and Stangl](https://acfr.aut.ac.nz/__data/assets/pdf_file/0005/294287/The-Myth-of-Sector-Rotation-non-blind.pdf)) | Not supported | Not used |
| Yield curve and credit spreads | Lead recessions at index level; not shown to predict one stock against another | Index-level only | Not used in version 0.1 |

## Positioning

| Factor | What the evidence says | Strength | Treatment |
|---|---|---|---|
| Days to cover | A better predictor than short percent of float; much weaker among large stocks ([Hong et al.](https://www.nber.org/papers/w21166.pdf)) | Moderate, small-cap | Positioning line and risk (crowding) |
| Insider purchases | More informative than sales; trades outside an insider's usual pattern carried the signal ([NBER Digest](https://www.nber.org/digest/apr11/decoding-inside-information)) | Moderate | Positioning line |
| Institutional holdings (13F) | Mild positive at short horizons that reverses after persistent buying ([Dasgupta, Prat and Verardo](https://personal.lse.ac.uk/VERARDOM/papers/InstitutionalTradePersistence_JF11.pdf)); data is up to 135 days old | Weak and late | Positioning line |
| Analyst price targets | About 38% met at 12 months, with a 15-point average overshoot ([Bradshaw, Brown and Huang](https://ideas.repec.org/a/spr/reaccs/v18y2013i4d10.1007_s11142-012-9216-5.html)) | Poor | Context, with a standing note |
| Congressional trades | No outperformance after the STOCK Act ([Belmont et al.](https://www.nber.org/papers/w26975)) | Not supported | Not used |
| Put/call ratios and unusual options activity | Unsigned ratios are weak; no rigorous evidence found for activity feeds | Not supported | Not used |

## ETFs

| Factor | What the evidence says | Strength | Treatment |
|---|---|---|---|
| Expense ratio | The best single predictor of realized tracking difference ([ETF.com](https://www.etf.com/sections/etf-basics/understanding-tracking-difference-and-tracking-error)) | Strong | ETF cost section |
| Legal structure | Sets tax treatment and issuer credit risk ([ETF.com](https://www.etf.com/sections/etf-basics/investors-field-guide-etf-structures)) | Factual | ETF structure section |
| Assets under $50 million | The common warning line for closure ([ETF.com](https://www.etf.com/sections/etf-basics/managing-avoiding-etf-closures)) | Practitioner rule | Risk (structure) |
| Fund inflows | Heavy inflows preceded weaker returns ([Brown, Davies and Ringgenberg](https://ideas.repec.org/a/oup/revfin/v25y2021i4p937-972..html)) | Moderate, contrarian | Not used in version 0.1 |
| Daily reset in geared and inverse funds | Returns over longer periods can differ sharply from the stated multiple ([SEC and FINRA](https://www.investor.gov/news-alerts/investor-alerts/sec-finra-investor-alert-leveraged-inverse-etfs)) | Factual | Reduced report, risk class 5 |

## Levels and stops

| Factor | What the evidence says | Strength | Treatment |
|---|---|---|---|
| Stop-loss rules | Cannot add return if prices follow a random walk, and help mainly where returns trend ([Kaminski and Lo](https://dspace.mit.edu/bitstream/handle/1721.1/114876/Lo_When%20Do%20Stop-Loss.pdf)) | Loss control, not return | Levels |
| Support, resistance and pivot levels | No academic evidence on their predictive value was found | Convention | Levels, labelled as planning references |
| Avoiding extended entries | Held up in the author's own testing on an earlier project, and weakened sharply in bear markets | Single private test | Suppresses the buy range |

## What was not reviewed

Covered-call and other derivative-income funds, borrow fees, gamma exposure, mutual fund flows, reverse discounted cash flow, and independent tests of vendor ratings were not sourced. Several textbook formulas were taken from general knowledge and should be checked against the data vendor's field definitions when the scripts are written.
