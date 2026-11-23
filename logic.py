from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class Quote:
    supplier: str
    unit_price: float        # INR
    lead_time_days: int
    valid_until: date


def is_valid(quote: Quote, today: date) -> bool:
    # Assumption: a quote is still valid ON its valid_until date
    return quote.valid_until >= today


def arrives_in_time(quote: Quote, needed_by: date, today: date) -> bool:
    # Assumption: we order today, so arrival = today + lead time
    return today + timedelta(days=quote.lead_time_days) <= needed_by


def best_quote(quotes, needed_by: date, today: date):
    """Cheapest quote that is valid AND arrives in time. None if no such quote."""
    eligible = [
        q for q in quotes
        if is_valid(q, today) and arrives_in_time(q, needed_by, today)
    ]
    if not eligible:
        return None
    # Tie-break: cheaper first, then shorter lead time
    return min(eligible, key=lambda q: (q.unit_price, q.lead_time_days))


def rfq_status(quotes, needed_by: date, today: date) -> str:
    if needed_by < today:
        return "Expired"
    if not quotes:
        return "Open"
    if any(is_valid(q, today) for q in quotes):
        return "Quoted"
    return "Expired"