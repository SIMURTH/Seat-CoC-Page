import pytest

from app.store import DuplicateCoCError
from tests.conftest import make_payload

OTHER_VIN = "WDD7654321GFEDCBA"


def test_add_assigns_incrementing_ids(store):
    first = store.add(make_payload())
    second = store.add(make_payload(vin=OTHER_VIN))
    assert (first.id, second.id) == (1, 2)


def test_add_rejects_duplicate_vin(store):
    store.add(make_payload())
    with pytest.raises(DuplicateCoCError):
        store.add(make_payload(vin="wdd1234567abcdefg"))


def test_get_returns_none_for_unknown_id(store):
    assert store.get(42) is None


def test_get_by_vin_is_case_insensitive(store):
    record = store.add(make_payload())
    assert store.get_by_vin(" wdd1234567abcdefg ") == record
    assert store.get_by_vin(OTHER_VIN) is None


def test_list_filters_by_manufacturer(store):
    store.add(make_payload())
    store.add(make_payload(vin=OTHER_VIN, manufacturer="Lear"))
    assert [r.manufacturer for r in store.list()] == ["Recaro", "Lear"]
    assert [r.vin for r in store.list(" lear ")] == [OTHER_VIN]
    assert store.list("Unknown") == []


def test_delete_removes_record_once(store):
    record = store.add(make_payload())
    assert store.delete(record.id) is True
    assert store.delete(record.id) is False
    assert store.get(record.id) is None


def test_clear_resets_ids(store):
    store.add(make_payload())
    store.clear()
    assert store.list() == []
    assert store.add(make_payload()).id == 1
