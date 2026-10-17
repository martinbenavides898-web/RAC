import unittest
from datetime import date, datetime
from unittest.mock import patch

from rac_core.race_calendar import (
    LEGACY_PLACEHOLDER_DATE,
    OFFICIAL_MARATHON_DATE_2027,
    days_until_race,
    parse_iso_date,
    today_santiago,
    training_phases,
)


class RaceCalendarTests(unittest.TestCase):
    def test_official_date_is_may_16_2027(self):
        self.assertEqual(OFFICIAL_MARATHON_DATE_2027, date(2027, 5, 16))

    def test_legacy_placeholder_is_identified(self):
        self.assertEqual(LEGACY_PLACEHOLDER_DATE, date(2027, 4, 18))

    def test_parse_iso_date_valid_and_fallback(self):
        self.assertEqual(parse_iso_date("2027-05-16"), date(2027, 5, 16))
        self.assertEqual(parse_iso_date(None), OFFICIAL_MARATHON_DATE_2027)
        self.assertEqual(parse_iso_date("not-a-date"), OFFICIAL_MARATHON_DATE_2027)

    def test_days_until_race_uses_explicit_reference_when_provided(self):
        self.assertEqual(days_until_race(date(2027, 5, 16), date(2027, 5, 1)), 15)
        self.assertEqual(days_until_race(date(2027, 5, 1), date(2027, 5, 16)), -15)

    def test_today_santiago_returns_date(self):
        self.assertIsInstance(today_santiago(), date)

    def test_phases_end_on_race_date_and_are_ordered(self):
        today = date(2026, 10, 17)
        race = date(2027, 5, 16)
        phases = training_phases(race, today)
        self.assertGreaterEqual(len(phases), 1)
        self.assertEqual(phases[-1].end_date, race)
        for previous, current in zip(phases, phases[1:]):
            self.assertEqual((current.start_date - previous.end_date).days, 1)
        self.assertEqual(phases[-1].name, "Taper / descarga final")

    def test_past_race_date_does_not_create_future_training_phases(self):
        phases = training_phases(date(2026, 10, 1), date(2026, 10, 17))
        self.assertEqual(len(phases), 1)
        self.assertEqual(phases[0].weeks, 0)


if __name__ == "__main__":
    unittest.main()
