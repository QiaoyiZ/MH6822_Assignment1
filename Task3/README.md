# Task 3: Jurisdiction-Aware AML Alert Calibration Tool

This folder contains the Task 3 quantitative component for the MH6822 Regulatory Technology assignment.

## Project context

- Regulated entity: Citibank, N.A. / Citi Singapore
- Domain: AML/KYC and suspicious transaction monitoring
- Jurisdictions compared: United States and Singapore
- Assignment option: Option C, Analytical Design with Quantitative Component

## Folder contents

- `data/Task3_synthetic_transactions.csv`: synthetic transaction dataset used for the analysis.
- `scripts/generate_task3_synthetic_data.py`: script used to generate the synthetic dataset.
- `scripts/analyze_task3_alerts.py`: script that applies US and Singapore alert-scoring configurations.
- `results/Task3_scored_transactions.csv`: dataset with US and Singapore scores, alerts, and alert reasons.
- `results/Task3_analysis_summary.md`: summary of baseline metrics and sensitivity analysis.

## How to reproduce the analysis

Run the scripts from the Task 3 folder root:

```bash
python scripts/generate_task3_synthetic_data.py
python scripts/analyze_task3_alerts.py
```

The analysis compares alert rate, false-positive proxy rate, manual review workload, and high-risk capture rate under US and Singapore configurations.
