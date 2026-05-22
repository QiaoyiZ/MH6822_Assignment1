# Task 3 Quantitative Analysis Summary

This analysis applies two jurisdiction-specific AML alert configurations to the same synthetic transaction dataset. US mode gives greater weight to sanctions match score, USD transactions, structuring-like patterns, and US nexus indicators. Singapore mode gives greater weight to customer due diligence, beneficial ownership completeness, wire transfer information completeness, customer risk level, and STRO review indicators.

## Baseline results

| Metric | US mode | Singapore mode |
|---|---:|---:|
| Alert count | 79 | 107 |
| Alert rate | 7.9% | 10.7% |
| False-positive proxy count | 53 | 80 |
| False-positive proxy rate among alerts | 67.1% | 74.8% |
| Known suspicious patterns captured | 26/49 | 27/49 |
| High-risk capture rate | 53.1% | 55.1% |
| Manual review workload | 59.2 hours | 80.2 hours |
| Average score | 19.1 | 15.4 |

## Sensitivity analysis 1: US sanctions threshold lowered from 0.75 to 0.65

- US alert count changes from 79 to 88 (+9).
- US false-positive proxy count changes from 53 to 62 (+9).
- Singapore mode is unchanged in this scenario because this sensitivity test changes the US sanctions threshold only.

## After US sanctions threshold sensitivity

| Metric | US mode | Singapore mode |
|---|---:|---:|
| Alert count | 88 | 107 |
| Alert rate | 8.8% | 10.7% |
| False-positive proxy count | 62 | 80 |
| False-positive proxy rate among alerts | 70.5% | 74.8% |
| Known suspicious patterns captured | 26/49 | 27/49 |
| High-risk capture rate | 53.1% | 55.1% |
| Manual review workload | 66.0 hours | 80.2 hours |
| Average score | 19.4 | 15.4 |

## Sensitivity analysis 2: high-risk-country exposure increased by 100 transactions

- US alert count changes from 79 to 86 (+7).
- Singapore alert count changes from 107 to 116 (+9).
- US high-risk capture rate changes from 53.1% to 53.1%.
- Singapore high-risk capture rate changes from 55.1% to 55.1%.

## After high-risk-country exposure shift

| Metric | US mode | Singapore mode |
|---|---:|---:|
| Alert count | 86 | 116 |
| Alert rate | 8.6% | 11.6% |
| False-positive proxy count | 60 | 89 |
| False-positive proxy rate among alerts | 69.8% | 76.7% |
| Known suspicious patterns captured | 26/49 | 27/49 |
| High-risk capture rate | 53.1% | 55.1% |
| Manual review workload | 64.5 hours | 87.0 hours |
| Average score | 19.7 | 16.9 |

## Interpretation

The two configurations produce different alert volumes and different operational burdens because they encode different regulatory emphases. US mode is more sensitive to sanctions and US nexus indicators, while Singapore mode is more sensitive to CDD-related weaknesses such as incomplete beneficial ownership and wire transfer information. The point of the tool is not to declare one jurisdiction stricter. The point is to show how jurisdictional choices become measurable differences in alerting, workload, and escalation logic.
