import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from marketing_analytics import allocate, calculate_metrics, safe_divide


class MarketingAnalyticsTests(unittest.TestCase):
    def test_safe_divide_handles_zero(self):
        self.assertEqual(safe_divide(12, 0), 0.0)

    def test_metric_calculation(self):
        row = {
            "campaign_id": "X", "channel": "Test", "spend_eur": "1000",
            "impressions": "10000", "clicks": "500", "landing_sessions": "400",
            "engaged_sessions": "200", "qualified_leads": "20",
            "opportunities": "5", "pilot_commitments": "1",
        }
        result = calculate_metrics(row)
        self.assertEqual(result["ctr_pct"], 5.0)
        self.assertEqual(result["cost_per_opportunity_eur"], 200.0)

    def test_budget_allocation_sums_to_one_hundred(self):
        kpis = [
            {"campaign_id": "A", "channel": "A", "engagement_rate_pct": 70,
             "cost_per_qualified_lead_eur": 100, "cost_per_opportunity_eur": 500},
            {"campaign_id": "B", "channel": "B", "engagement_rate_pct": 40,
             "cost_per_qualified_lead_eur": 200, "cost_per_opportunity_eur": 800},
        ]
        sources = [{"strategic_fit": 5, "data_confidence": 5}, {"strategic_fit": 3, "data_confidence": 3}]
        scenario = {"budget_eur": 10000, "minimum_channel_share_pct": 10,
                    "maximum_channel_share_pct": 90,
                    "score_weights": {"engagement": 20, "lead_efficiency": 25,
                                      "opportunity_efficiency": 25, "strategic_fit": 20,
                                      "data_confidence": 10}}
        result = allocate(kpis, sources, scenario)
        self.assertAlmostEqual(sum(row["recommended_budget_share_pct"] for row in result), 100.0)


if __name__ == "__main__":
    unittest.main()
