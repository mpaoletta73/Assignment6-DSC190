import pytest
from datetime import date
from nldate.parser import parse

# Use a fixed date so relative tests are consistent
FIXED_TODAY = date(2026, 5, 20)

@pytest.mark.parametrize("input_str, expected", [
    ("December 1st, 2025", date(2025, 12, 1)),
    ("tomorrow", date(2026, 5, 21)),
    ("yesterday", date(2026, 5, 19)),
    ("2 days ago", date(2026, 5, 18)),
    ("in 3 weeks", date(2026, 6, 10)),
    ("next Tuesday", date(2026, 5, 26)),
    ("5 days before December 1st, 2025", date(2025, 11, 26)),
    ("1 year and 2 months after yesterday", date(2027, 7, 19)),
    ("Jan 1 2024", date(2024, 1, 1)),
    ("three days from now", date(2026, 5, 23)),
])
def test_parse_variants(input_str, expected):
    assert parse(input_str, today=FIXED_TODAY) == expected
