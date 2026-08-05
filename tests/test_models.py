from datetime import date

import pytest
from pydantic import ValidationError

from app.models import SeatCoC
from tests.conftest import make_payload


def test_vin_is_normalized_to_uppercase():
    assert make_payload(vin=" wdd1234567abcdefg ").vin == "WDD1234567ABCDEFG"


@pytest.mark.parametrize("vin", ["WDD1234567ABCDEFI", "WDD1234567ABCDEFO", "WDD1234567ABCDEFQ"])
def test_vin_rejects_forbidden_letters(vin):
    with pytest.raises(ValidationError, match="I, O or Q"):
        make_payload(vin=vin)


def test_vin_rejects_non_alphanumeric():
    with pytest.raises(ValidationError, match="alphanumeric"):
        make_payload(vin="WDD-234567ABCDEFG")


def test_vin_rejects_non_string():
    with pytest.raises(ValidationError, match="must be a string"):
        make_payload(vin=12345678901234567)


@pytest.mark.parametrize("length_vin", ["SHORT", "WDD1234567ABCDEFGH"])
def test_vin_length_is_enforced(length_vin):
    with pytest.raises(ValidationError, match="17 characters"):
        make_payload(vin=length_vin)


def test_text_fields_are_stripped():
    payload = make_payload(seat_model="  Comfort S  ", manufacturer=" Recaro ")
    assert payload.seat_model == "Comfort S"
    assert payload.manufacturer == "Recaro"


def test_blank_text_field_is_rejected():
    with pytest.raises(ValidationError, match="must not be blank"):
        make_payload(seat_model="   ")


@pytest.mark.parametrize(
    "reference,expected",
    [
        (date(2024, 12, 31), False),
        (date(2025, 1, 1), True),
        (date(2025, 6, 1), True),
        (date(2026, 1, 1), True),
        (date(2026, 1, 2), False),
    ],
)
def test_is_valid_on(reference, expected):
    record = SeatCoC(id=1, **make_payload().model_dump())
    assert record.is_valid_on(reference) is expected


def test_is_valid_on_without_expiry_never_expires():
    record = SeatCoC(id=1, **make_payload(expires_on=None).model_dump())
    assert record.is_valid_on(date(2099, 1, 1)) is True
