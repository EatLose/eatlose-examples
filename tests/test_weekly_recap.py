import json
import unittest
from pathlib import Path

from examples.weekly_recap import weekly_recap


class WeeklyRecapTests(unittest.TestCase):
    def setUp(self):
        source = Path(__file__).resolve().parents[1] / "examples" / "sample-week.json"
        self.diary = json.loads(source.read_text(encoding="utf-8"))

    def test_public_week(self):
        result = weekly_recap(self.diary)
        self.assertEqual(result["confirmed_meals"], 14)
        self.assertEqual(result["logged_days"], 6)
        self.assertEqual(result["days_with_protein_estimate"], 6)
        self.assertEqual(result["mean_estimated_protein_g_per_day_with_estimate"], 71.3)

    def test_zero_counts_as_known_and_unknown_protein_is_excluded(self):
        self.diary["nutrition_days"] = [
            {"meal_count": 1, "estimated_protein_g": 0},
            {"meal_count": 2, "estimated_protein_g": None},
            {"meal_count": 1, "estimated_protein_g": 30},
        ]
        result = weekly_recap(self.diary)
        self.assertEqual(result["confirmed_meals"], 4)
        self.assertEqual(result["logged_days"], 3)
        self.assertEqual(result["days_with_protein_estimate"], 2)
        self.assertEqual(result["mean_estimated_protein_g_per_day_with_estimate"], 15.0)

    def test_empty_and_all_unknown_weeks(self):
        for days in ([], [{"meal_count": 1, "estimated_protein_g": None}]):
            with self.subTest(days=days):
                self.diary["nutrition_days"] = days
                result = weekly_recap(self.diary)
                self.assertEqual(result["days_with_protein_estimate"], 0)
                self.assertIsNone(result["mean_estimated_protein_g_per_day_with_estimate"])
