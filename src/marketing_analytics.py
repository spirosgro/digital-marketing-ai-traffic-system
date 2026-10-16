from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def calculate_metrics(row: dict) -> dict:
    n = {key: float(row[key]) for key in [
        "spend_eur", "impressions", "clicks", "landing_sessions", "engaged_sessions",
        "qualified_leads", "opportunities", "pilot_commitments"
    ]}
    return {
        "campaign_id": row["campaign_id"],
        "channel": row["channel"],
        "ctr_pct": round(100 * safe_divide(n["clicks"], n["impressions"]), 2),
        "engagement_rate_pct": round(100 * safe_divide(n["engaged_sessions"], n["landing_sessions"]), 2),
        "lead_conversion_pct": round(100 * safe_divide(n["qualified_leads"], n["landing_sessions"]), 2),
        "opportunity_conversion_pct": round(100 * safe_divide(n["opportunities"], n["qualified_leads"]), 2),
        "pilot_conversion_pct": round(100 * safe_divide(n["pilot_commitments"], n["opportunities"]), 2),
        "cost_per_qualified_lead_eur": round(safe_divide(n["spend_eur"], n["qualified_leads"]), 2),
        "cost_per_opportunity_eur": round(safe_divide(n["spend_eur"], n["opportunities"]), 2),
        "cost_per_pilot_eur": round(safe_divide(n["spend_eur"], n["pilot_commitments"]), 2),
    }


def allocate(rows: list[dict], source_rows: list[dict], scenario: dict) -> list[dict]:
    max_cpl = max(row["cost_per_qualified_lead_eur"] for row in rows)
    max_cpo = max(row["cost_per_opportunity_eur"] for row in rows)
    weights = scenario["score_weights"]
    output = []
    for row, source in zip(rows, source_rows):
        engagement = min(row["engagement_rate_pct"] / 75.0, 1.0) * weights["engagement"]
        lead_efficiency = (1 - row["cost_per_qualified_lead_eur"] / max_cpl) * weights["lead_efficiency"]
        opportunity_efficiency = (1 - row["cost_per_opportunity_eur"] / max_cpo) * weights["opportunity_efficiency"]
        strategic = float(source["strategic_fit"]) / 5 * weights["strategic_fit"]
        confidence = float(source["data_confidence"]) / 5 * weights["data_confidence"]
        output.append({**row, "score": round(engagement + lead_efficiency + opportunity_efficiency + strategic + confidence, 2)})
    total = sum(row["score"] for row in output)
    low = scenario["minimum_channel_share_pct"]
    high = scenario["maximum_channel_share_pct"]
    for row in output:
        row["recommended_budget_share_pct"] = round(max(low, min(high, row["score"] / total * 100)), 1)
    delta = round(100 - sum(row["recommended_budget_share_pct"] for row in output), 1)
    best = max(output, key=lambda row: row["score"])
    best["recommended_budget_share_pct"] = round(best["recommended_budget_share_pct"] + delta, 1)
    for row in output:
        row["recommended_budget_eur"] = round(scenario["budget_eur"] * row["recommended_budget_share_pct"] / 100, 2)
        row["decision_status"] = "human review required"
    return sorted(output, key=lambda row: row["score"], reverse=True)


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row[key] for key in fields} for row in rows)


def build_outputs() -> tuple[list[dict], list[dict]]:
    source = read_csv(ROOT / "data" / "synthetic-campaign-performance.csv")
    scenario = json.loads((ROOT / "config" / "scenario.json").read_text(encoding="utf-8"))
    kpis = [calculate_metrics(row) for row in source]
    recommendations = allocate(kpis, source, scenario)
    return kpis, recommendations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    kpis, recommendations = build_outputs()
    kpi_fields = list(kpis[0])
    rec_fields = ["campaign_id", "channel", "score", "recommended_budget_share_pct", "recommended_budget_eur", "decision_status"]
    if args.check:
        expected_kpis = read_csv(ROOT / "output" / "channel-kpis.csv")
        expected_recs = read_csv(ROOT / "output" / "budget-recommendations.csv")
        if expected_kpis != [{key: str(row[key]) for key in kpi_fields} for row in kpis]:
            raise SystemExit("channel-kpis.csv is stale")
        if expected_recs != [{key: str(row[key]) for key in rec_fields} for row in recommendations]:
            raise SystemExit("budget-recommendations.csv is stale")
        print("Analytics outputs are current.")
        return 0
    write_csv(ROOT / "output" / "channel-kpis.csv", kpis, kpi_fields)
    write_csv(ROOT / "output" / "budget-recommendations.csv", recommendations, rec_fields)
    print("Wrote analytics outputs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
