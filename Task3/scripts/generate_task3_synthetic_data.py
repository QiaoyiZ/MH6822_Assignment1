import csv
import random
from pathlib import Path


random.seed(6822)

OUT = Path("Task3_synthetic_transactions.csv")

countries = [
    "United States",
    "Singapore",
    "United Kingdom",
    "Hong Kong",
    "Malaysia",
    "Indonesia",
    "UAE",
    "Switzerland",
    "Panama",
    "British Virgin Islands",
]

high_risk_countries = {"Panama", "British Virgin Islands", "UAE"}
currencies = ["USD", "SGD", "GBP", "HKD", "EUR"]
customer_types = ["individual", "small_business", "corporate", "private_banking"]
risk_levels = ["low", "medium", "high"]


def weighted_choice(items):
    values, weights = zip(*items)
    return random.choices(values, weights=weights, k=1)[0]


def bool_by_prob(prob):
    return random.random() < prob


def amount_for_customer(customer_type, risk_level):
    base = {
        "individual": (250, 25000),
        "small_business": (1000, 90000),
        "corporate": (5000, 450000),
        "private_banking": (10000, 650000),
    }[customer_type]
    amount = random.uniform(*base)
    if risk_level == "high":
        amount *= random.uniform(1.1, 1.8)
    if bool_by_prob(0.06):
        # Structuring-like values just below common round thresholds.
        amount = random.choice([9200, 9500, 9800, 9900, 19500, 19800])
    return round(amount, 2)


def sanctions_score(origin, destination, risk_level):
    score = random.betavariate(1.5, 8)
    if origin in high_risk_countries or destination in high_risk_countries:
        score += random.uniform(0.12, 0.35)
    if risk_level == "high":
        score += random.uniform(0.08, 0.22)
    if bool_by_prob(0.04):
        score += random.uniform(0.35, 0.55)
    return round(min(score, 0.99), 3)


def suspicious_pattern(row):
    pattern_score = 0
    if row["customer_risk_level"] == "high":
        pattern_score += 1
    if row["destination_country"] in high_risk_countries or row["origin_country"] in high_risk_countries:
        pattern_score += 1
    if float(row["sanctions_match_score"]) >= 0.75:
        pattern_score += 2
    if row["new_counterparty"] == "Y":
        pattern_score += 1
    if row["beneficial_owner_complete"] == "N":
        pattern_score += 1
    if row["wire_transfer_info_complete"] == "N":
        pattern_score += 1
    if row["structuring_like_pattern"] == "Y":
        pattern_score += 2
    if int(row["transaction_frequency_7d"]) >= 8:
        pattern_score += 1
    return "Y" if pattern_score >= 4 or bool_by_prob(0.015) else "N"


rows = []
for i in range(1, 1001):
    customer_type = weighted_choice(
        [
            ("individual", 42),
            ("small_business", 25),
            ("corporate", 23),
            ("private_banking", 10),
        ]
    )
    risk_level = weighted_choice([("low", 45), ("medium", 38), ("high", 17)])
    origin = weighted_choice(
        [
            ("United States", 28),
            ("Singapore", 30),
            ("United Kingdom", 8),
            ("Hong Kong", 9),
            ("Malaysia", 8),
            ("Indonesia", 6),
            ("UAE", 4),
            ("Switzerland", 3),
            ("Panama", 2),
            ("British Virgin Islands", 2),
        ]
    )
    destination = weighted_choice(
        [
            ("United States", 27),
            ("Singapore", 29),
            ("United Kingdom", 8),
            ("Hong Kong", 9),
            ("Malaysia", 8),
            ("Indonesia", 6),
            ("UAE", 5),
            ("Switzerland", 3),
            ("Panama", 3),
            ("British Virgin Islands", 2),
        ]
    )
    while destination == origin:
        destination = random.choice(countries)

    currency = weighted_choice([("USD", 42), ("SGD", 28), ("GBP", 8), ("HKD", 9), ("EUR", 13)])
    amount = amount_for_customer(customer_type, risk_level)
    freq = max(1, int(random.gauss(3, 2)))
    if risk_level == "high":
        freq += random.randint(0, 5)

    bo_complete_prob = {"low": 0.97, "medium": 0.91, "high": 0.78}[risk_level]
    wire_complete_prob = {"low": 0.98, "medium": 0.94, "high": 0.84}[risk_level]

    row = {
        "transaction_id": f"TXN{i:04d}",
        "transaction_amount": amount,
        "currency": currency,
        "origin_country": origin,
        "destination_country": destination,
        "customer_risk_level": risk_level,
        "customer_type": customer_type,
        "sanctions_match_score": sanctions_score(origin, destination, risk_level),
        "new_counterparty": "Y" if bool_by_prob({"low": 0.12, "medium": 0.22, "high": 0.36}[risk_level]) else "N",
        "transaction_frequency_7d": freq,
        "beneficial_owner_complete": "Y" if bool_by_prob(bo_complete_prob) else "N",
        "wire_transfer_info_complete": "Y" if bool_by_prob(wire_complete_prob) else "N",
        "structuring_like_pattern": "Y" if amount in [9200, 9500, 9800, 9900, 19500, 19800] else "N",
    }
    row["known_suspicious_pattern"] = suspicious_pattern(row)
    rows.append(row)


with OUT.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {OUT} with {len(rows)} rows")
