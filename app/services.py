from datetime import date, timedelta
from typing import Dict, List

from app.models import SeatCoC
from app.store import CoCStore

EXPIRY_WARNING_DAYS = 30


def certificate_status(record: SeatCoC, reference: date) -> str:
    """Return "pending", "expired", "expiring" or "valid" for a record."""
    if reference < record.issued_on:
        return "pending"
    if record.expires_on is None:
        return "valid"
    if reference > record.expires_on:
        return "expired"
    if (record.expires_on - reference).days <= EXPIRY_WARNING_DAYS:
        return "expiring"
    return "valid"


def expiring_soon(store: CoCStore, reference: date, days: int = EXPIRY_WARNING_DAYS) -> List[SeatCoC]:
    """Records that expire within `days` of the reference date (not yet expired)."""
    if days < 0:
        raise ValueError("days must not be negative")
    horizon = reference + timedelta(days=days)
    return [
        record
        for record in store.list()
        if record.expires_on is not None
        and record.issued_on <= reference
        and reference <= record.expires_on <= horizon
    ]


def summarize(store: CoCStore, reference: date) -> Dict[str, int]:
    """Count records per status."""
    summary = {"valid": 0, "expiring": 0, "expired": 0, "pending": 0}
    for record in store.list():
        summary[certificate_status(record, reference)] += 1
    return summary
