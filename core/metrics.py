from collections import defaultdict
from prometheus_client import Counter

decision_metrics = defaultdict(int)

def record_decision(approved: bool):
    if approved:
        decision_metrics["approved"] += 1
    else:
        decision_metrics["denied"] += 1

decision_counter = Counter(
    "financial_decsions_total",
    "Total financial decisions"
)

decision_denied = Counter(
    "financial_decision_denied",
    "Denied decisions"
)