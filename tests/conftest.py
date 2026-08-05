from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_store
from app.models import SeatCoCCreate
from app.store import CoCStore

REFERENCE = date(2025, 6, 1)


def make_payload(vin: str = "WDD1234567ABCDEFG", **overrides) -> SeatCoCCreate:
    data = {
        "vin": vin,
        "seat_model": "Comfort S",
        "manufacturer": "Recaro",
        "approval_number": "E1-17R-0001",
        "issued_on": date(2025, 1, 1),
        "expires_on": date(2026, 1, 1),
    }
    data.update(overrides)
    return SeatCoCCreate(**data)


@pytest.fixture
def store() -> CoCStore:
    return CoCStore()


@pytest.fixture
def client(store: CoCStore):
    app.dependency_overrides[get_store] = lambda: store
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
