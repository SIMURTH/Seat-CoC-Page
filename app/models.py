from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SeatCoCBase(BaseModel):
    """Common fields of a seat Certificate of Conformity."""

    vin: str
    seat_model: str = Field(min_length=1)
    manufacturer: str = Field(min_length=1)
    approval_number: str = Field(min_length=1)
    issued_on: date
    expires_on: Optional[date] = None

    @field_validator("vin", mode="before")
    @classmethod
    def normalize_vin(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("vin must be a string")
        vin = value.strip().upper()
        if len(vin) != 17:
            raise ValueError("vin must be exactly 17 characters long")
        if not vin.isalnum():
            raise ValueError("vin must be alphanumeric")
        if any(char in vin for char in "IOQ"):
            raise ValueError("vin must not contain the letters I, O or Q")
        return vin

    @field_validator("seat_model", "manufacturer", "approval_number")
    @classmethod
    def strip_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("value must not be blank")
        return stripped


class SeatCoCCreate(SeatCoCBase):
    pass


class SeatCoC(SeatCoCBase):
    id: int

    def is_valid_on(self, reference: date) -> bool:
        if reference < self.issued_on:
            return False
        if self.expires_on is None:
            return True
        return reference <= self.expires_on
