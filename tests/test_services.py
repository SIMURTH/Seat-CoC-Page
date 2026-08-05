from datetime import date

import pytest

from app.models import SeatCoC
from app.services import certificate_status, expiring_soon, summarize
from tests.conftest import REFERENCE, make_payload

VINS = ["WDD1234567ABCDEF1", "WDD1234567ABCDEF2", "WDD1234567ABCDEF3", "WDD1234567ABCDEF4"]


def record(**overrides) -> SeatCoC:
    return SeatCoC(id=1, **make_payload(**overrides).model_dump())


@pytest.mark.parametrize(
    "overrides,expected",
    [
        ({"issued_on": date(2025, 7, 1), "expires_on": date(2026, 1, 1)}, "pending"),
        ({"expires_on": None}, "valid"),
        ({"expires_on": date(2025, 5, 31)}, "expired"),
        ({"expires_on": date(2025, 6, 1)}, "expiring"),
        ({"expires_on": date(2025, 7, 1)}, "expiring"),
        ({"expires_on": date(2025, 7, 2)}, "valid"),
    ],
)
def test_certificate_status(overrides, expected):
    assert certificate_status(record(**overrides), REFERENCE) == expected


def test_expiring_soon_selects_only_records_inside_horizon(store):
    store.add(make_payload(vin=VINS[0], expires_on=date(2025, 6, 15)))
    store.add(make_payload(vin=VINS[1], expires_on=date(2025, 12, 1)))
    store.add(make_payload(vin=VINS[2], expires_on=date(2025, 5, 1)))
    store.add(make_payload(vin=VINS[3], expires_on=None))
    assert [r.vin for r in expiring_soon(store, REFERENCE)] == [VINS[0]]


def test_expiring_soon_ignores_not_yet_issued(store):
    store.add(make_payload(vin=VINS[0], issued_on=date(2025, 6, 10), expires_on=date(2025, 6, 20)))
    assert expiring_soon(store, REFERENCE) == []


def test_expiring_soon_honours_custom_window(store):
    store.add(make_payload(vin=VINS[0], expires_on=date(2025, 8, 1)))
    assert expiring_soon(store, REFERENCE, days=90)
    assert expiring_soon(store, REFERENCE, days=0) == []


def test_expiring_soon_rejects_negative_days(store):
    with pytest.raises(ValueError, match="negative"):
        expiring_soon(store, REFERENCE, days=-1)


def test_summarize_counts_each_status(store):
    store.add(make_payload(vin=VINS[0], expires_on=None))
    store.add(make_payload(vin=VINS[1], expires_on=date(2025, 6, 10)))
    store.add(make_payload(vin=VINS[2], expires_on=date(2025, 1, 5)))
    store.add(make_payload(vin=VINS[3], issued_on=date(2025, 9, 1), expires_on=date(2026, 9, 1)))
    assert summarize(store, REFERENCE) == {"valid": 1, "expiring": 1, "expired": 1, "pending": 1}


def test_summarize_empty_store(store):
    assert summarize(store, REFERENCE) == {"valid": 0, "expiring": 0, "expired": 0, "pending": 0}
