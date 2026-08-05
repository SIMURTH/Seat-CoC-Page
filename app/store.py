from typing import Dict, List, Optional

from app.models import SeatCoC, SeatCoCCreate


class DuplicateCoCError(Exception):
    """Raised when a CoC already exists for a VIN."""


class CoCStore:
    """In-memory storage for seat CoC records."""

    def __init__(self) -> None:
        self._items: Dict[int, SeatCoC] = {}
        self._next_id = 1

    def add(self, payload: SeatCoCCreate) -> SeatCoC:
        if self.get_by_vin(payload.vin) is not None:
            raise DuplicateCoCError(f"CoC already exists for VIN {payload.vin}")
        record = SeatCoC(id=self._next_id, **payload.model_dump())
        self._items[record.id] = record
        self._next_id += 1
        return record

    def get(self, coc_id: int) -> Optional[SeatCoC]:
        return self._items.get(coc_id)

    def get_by_vin(self, vin: str) -> Optional[SeatCoC]:
        target = vin.strip().upper()
        for record in self._items.values():
            if record.vin == target:
                return record
        return None

    def list(self, manufacturer: Optional[str] = None) -> List[SeatCoC]:
        records = sorted(self._items.values(), key=lambda item: item.id)
        if manufacturer is None:
            return records
        needle = manufacturer.strip().lower()
        return [r for r in records if r.manufacturer.lower() == needle]

    def delete(self, coc_id: int) -> bool:
        return self._items.pop(coc_id, None) is not None

    def clear(self) -> None:
        self._items.clear()
        self._next_id = 1
