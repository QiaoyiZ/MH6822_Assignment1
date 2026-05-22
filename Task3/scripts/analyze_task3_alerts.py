import csv
from pathlib import Path


IN = Path("Task3_synthetic_transactions.csv")
OUT_SCORED = Path("Task3_scored_transactions.csv")
OUT_SUMMARY = Path("Task3_analysis_summary.md")

HIGH_RISK_COUNTRIES = {"Panama", "British Virgin Islands", "UAE"}


def yes(value):
    return value == "Y"


def amount(row):
    return float(row["transaction_amount"])


def sanctions(row):
    return float(row["sanctions_match_score"])


def us_nexus(row):
    return (
        row["currency"] == "USD"
        or row["origin_country"] == "United States"
        or row["destination_country"] == "United States"
    )


def high_risk_country(row):
    return row["origin_country"] in HIGH_RISK_COUNTRIES or row["destination_country"] in HIGH_RISK_COUNTRIES


def us_score(row, sanctions_threshold=0.75):
    score = 0
    reasons = []

    if sanctions(row) >= sanctions_threshold:
        score += 45
        reasons.append("high sanctions match score")
    elif sanctions(row) >= 0.55:
        score += 25
        reasons.append("elevated sanctions match score")

    if row["currency"] == "USD":
        score += 12
        reasons.append("USD transaction")

    if row["origin_country"] == "United States" or row["destination_country"] == "United States":
        score += 10
        reasons.append("US nexus")

    if yes(row["structuring_like_pattern"]):
        score += 30
        reasons.append("structuring-like pattern")

    if row["customer_risk_level"] == "high":
        score += 12
        reasons.append("high-risk customer")

    if high_risk_country(row):
        score += 8
        reasons.append("high-risk country exposure")

    if yes(row["new_counterparty"]) and amount(row) >= 50000:
        score += 8
        reasons.append("large transaction with new counterparty")

    alert = score >= 45
    return score, alert, "; ".join(reasons) if reasons else "no major US trigger"


def sg_score(row):
    score = 0
    reasons = []

    if row["customer_risk_level"] == "high":
        score += 20
        reasons.append("high-risk customer")

    if row["beneficial_owner_complete"] == "N":
        score += 28
        reasons.append("beneficial ownership incomplete")

    if row["wire_transfer_info_complete"] == "N":
        score += 25
        reasons.append("wire transfer information incomplete")

    if yes(row["new_counterparty"]):
        score += 10
        reasons.append("new counterparty")

    if int(row["transaction_frequency_7d"]) >= 8:
        score += 12
        reasons.append("unusual transaction frequency")

    if high_risk_country(row):
        score += 15
        reasons.append("high-risk country exposure")

    if amount(row) >= 100000 and row["customer_risk_level"] != "low":
        score += 10
        reasons.append("large transaction inconsistent with customer risk")

    if sanctions(row) >= 0.75:
        score += 15
        reasons.append("high sanctions match score")

    alert = score >= 45
    return score, alert, "; ".join(reasons) if reasons else "no major Singapore trigger"


def metrics(rows, score_prefix):
    alert_key = f"{score_prefix}_alert"
    score_key = f"{score_prefix}_score"
    alerts = [r for r in rows if r[alert_key] == "Y"]
    suspicious = [r for r in rows if r["known_suspicious_pattern"] == "Y"]
    false_positive_proxy = [
        r for r in alerts if r["known_suspicious_pattern"] == "N"
    ]
    captured = [
        r for r in suspicious if r[alert_key] == "Y"
    ]
    return {
        "transactions": len(rows),
        "alerts": len(alerts),
        "alert_rate": len(alerts) / len(rows),
        "false_positive_proxy": len(false_positive_proxy),
        "false_positive_proxy_rate_among_alerts": len(false_positive_proxy) / len(alerts) if alerts else 0,
        "known_suspicious": len(suspicious),
        "known_suspicious_captured": len(captured),
        "high_risk_capture_rate": len(captured) / len(suspicious) if suspicious else 0,
        "manual_review_hours": len(alerts) * 0.75,
        "average_score": sum(float(r[score_key]) for r in rows) / len(rows),
    }


def apply_scoring(rows, us_sanctions_threshold=0.75):
    scored = []
    for row in rows:
        row = dict(row)
        u_score, u_alert, u_reasons = us_score(row, us_sanctions_threshold)
        s_score, s_alert, s_reasons = sg_score(row)
        row["us_score"] = str(u_score)
        row["us_alert"] = "Y" if u_alert else "N"
        row["us_reasons"] = u_reasons
        row["sg_score"] = str(s_score)
        row["sg_alert"] = "Y" if s_alert else "N"
        row["sg_reasons"] = s_reasons
        scored.append(row)
    return scored


def clone_with_more_high_risk_country(rows, count=100):
    adjusted = [dict(r) for r in rows]
    candidates = [
        r for r in adjusted
        if r["origin_country"] not in HIGH_RISK_COUNTRIES
        and r["destination_country"] not in HIGH_RISK_COUNTRIES
    ]
    for idx, row in enumerate(candidates[:count]):
        if idx % 2 == 0:
            row["destination_country"] = "Panama"
        else:
            row["origin_country"] = "UAE"
        current = float(row["sanctions_match_score"])
        row["sanctions_match_score"] = str(round(min(0.99, current + 0.12), 3))
    return adjusted


def pct(value):
    return f"{value * 100:.1f}%"


def metric_table(title, us, sg):
    rows = [
        ("Alert count", str(us["alerts"]), str(sg["alerts"])),
        ("Alert rate", pct(us["alert_rate"]), pct(sg["alert_rate"])),
        ("False-positive proxy count", str(us["false_positive_proxy"]), str(sg["false_positive_proxy"])),
        ("False-positive proxy rate among alerts", pct(us["false_positive_proxy_rate_among_alerts"]), pct(sg["false_positive_proxy_rate_among_alerts"])),
        ("Known suspicious patterns captured", f'{us["known_suspicious_captured"]}/{us["known_suspicious"]}', f'{sg["known_suspicious_captured"]}/{sg["known_suspicious"]}'),
        ("High-risk capture rate", pct(us["high_risk_capture_rate"]), pct(sg["high_risk_capture_rate"])),
        ("Manual review workload", f'{us["manual_review_hours"]:.1f} hours', f'{sg["manual_review_hours"]:.1f} hours'),
        ("Average score", f'{us["average_score"]:.1f}', f'{sg["average_score"]:.1f}'),
    ]
    out = [f"## {title}", "", "| Metric | US mode | Singapore mode |", "|---|---:|---:|"]
    out += [f"| {a} | {b} | {c} |" for a, b, c in rows]
    out.append("")
    return "\n".join(out)


def main():
    with IN.open() as f:
        rows = list(csv.DictReader(f))

    scored = apply_scoring(rows)
    us = metrics(scored, "us")
    sg = metrics(scored, "sg")

    lowered_sanctions = apply_scoring(rows, us_sanctions_threshold=0.65)
    us_low = metrics(lowered_sanctions, "us")
    sg_low = metrics(lowered_sanctions, "sg")

    high_risk_shift = apply_scoring(clone_with_more_high_risk_country(rows, count=100))
    us_shift = metrics(high_risk_shift, "us")
    sg_shift = metrics(high_risk_shift, "sg")

    with OUT_SCORED.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(scored[0].keys()))
        writer.writeheader()
        writer.writerows(scored)

    summary = [
        "# Task 3 Quantitative Analysis Summary",
        "",
        "This analysis applies two jurisdiction-specific AML alert configurations to the same synthetic transaction dataset. US mode gives greater weight to sanctions match score, USD transactions, structuring-like patterns, and US nexus indicators. Singapore mode gives greater weight to customer due diligence, beneficial ownership completeness, wire transfer information completeness, customer risk level, and STRO review indicators.",
        "",
        metric_table("Baseline results", us, sg),
        "## Sensitivity analysis 1: US sanctions threshold lowered from 0.75 to 0.65",
        "",
        f"- US alert count changes from {us['alerts']} to {us_low['alerts']} ({us_low['alerts'] - us['alerts']:+d}).",
        f"- US false-positive proxy count changes from {us['false_positive_proxy']} to {us_low['false_positive_proxy']} ({us_low['false_positive_proxy'] - us['false_positive_proxy']:+d}).",
        "- Singapore mode is unchanged in this scenario because this sensitivity test changes the US sanctions threshold only.",
        "",
        metric_table("After US sanctions threshold sensitivity", us_low, sg_low),
        "## Sensitivity analysis 2: high-risk-country exposure increased by 100 transactions",
        "",
        f"- US alert count changes from {us['alerts']} to {us_shift['alerts']} ({us_shift['alerts'] - us['alerts']:+d}).",
        f"- Singapore alert count changes from {sg['alerts']} to {sg_shift['alerts']} ({sg_shift['alerts'] - sg['alerts']:+d}).",
        f"- US high-risk capture rate changes from {pct(us['high_risk_capture_rate'])} to {pct(us_shift['high_risk_capture_rate'])}.",
        f"- Singapore high-risk capture rate changes from {pct(sg['high_risk_capture_rate'])} to {pct(sg_shift['high_risk_capture_rate'])}.",
        "",
        metric_table("After high-risk-country exposure shift", us_shift, sg_shift),
        "## Interpretation",
        "",
        "The two configurations produce different alert volumes and different operational burdens because they encode different regulatory emphases. US mode is more sensitive to sanctions and US nexus indicators, while Singapore mode is more sensitive to CDD-related weaknesses such as incomplete beneficial ownership and wire transfer information. The point of the tool is not to declare one jurisdiction stricter. The point is to show how jurisdictional choices become measurable differences in alerting, workload, and escalation logic.",
        "",
    ]
    OUT_SUMMARY.write_text("\n".join(summary))
    print(f"Wrote {OUT_SCORED}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Baseline US alerts: {us['alerts']} ({pct(us['alert_rate'])})")
    print(f"Baseline SG alerts: {sg['alerts']} ({pct(sg['alert_rate'])})")


if __name__ == "__main__":
    main()
