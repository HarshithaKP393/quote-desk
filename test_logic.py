from datetime import date
from logic import Quote, best_quote, rfq_status

TODAY = date(2026, 11, 23)
NEEDED = date(2026, 12, 10)   # 17 days away


def q(name, price, lead, valid):
    return Quote(name, price, lead, valid)


def test_cheapest_valid_on_time_wins():
    quotes = [
        q("A", 100, 5, date(2026, 12, 31)),
        q("B", 80, 5, date(2026, 12, 31)),
    ]
    assert best_quote(quotes, NEEDED, TODAY).supplier == "B"


def test_cheaper_but_late_quote_is_skipped():
    quotes = [
        q("Cheap but slow", 50, 30, date(2026, 12, 31)),   # arrives too late
        q("Fast", 90, 10, date(2026, 12, 31)),
    ]
    assert best_quote(quotes, NEEDED, TODAY).supplier == "Fast"


def test_expired_quote_is_skipped():
    quotes = [
        q("Expired", 10, 5, date(2026, 11, 1)),
        q("Valid", 90, 5, date(2026, 12, 31)),
    ]
    assert best_quote(quotes, NEEDED, TODAY).supplier == "Valid"


def test_no_eligible_quote_returns_none():
    quotes = [q("Late", 50, 30, date(2026, 12, 31))]
    assert best_quote(quotes, NEEDED, TODAY) is None


def test_status_rules():
    assert rfq_status([], NEEDED, TODAY) == "Open"
    assert rfq_status([q("A", 1, 1, date(2026, 12, 31))], NEEDED, TODAY) == "Quoted"
    assert rfq_status([q("A", 1, 1, date(2026, 11, 1))], NEEDED, TODAY) == "Expired"
    assert rfq_status([], date(2026, 11, 1), TODAY) == "Expired"