from datetime import date
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from app.models import SeatCoC, SeatCoCCreate
from app.services import certificate_status, expiring_soon, summarize
from app.store import CoCStore, DuplicateCoCError

app = FastAPI(title="Seat CoC Page")
store = CoCStore()


def get_store() -> CoCStore:
    return store


@app.get("/", response_class=HTMLResponse)
def index(db: CoCStore = Depends(get_store)) -> str:
    today = date.today()
    rows = "".join(
        f"<tr><td>{r.vin}</td><td>{r.seat_model}</td><td>{r.manufacturer}</td>"
        f"<td>{certificate_status(r, today)}</td></tr>"
        for r in db.list()
    )
    if not rows:
        rows = '<tr><td colspan="4">No certificates yet</td></tr>'
    return (
        "<html><head><title>Seat CoC</title></head><body>"
        "<h1>Seat Certificates of Conformity</h1>"
        "<table><thead><tr><th>VIN</th><th>Seat model</th>"
        "<th>Manufacturer</th><th>Status</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></body></html>"
    )


@app.get("/api/coc", response_model=List[SeatCoC])
def list_coc(
    manufacturer: Optional[str] = Query(default=None),
    db: CoCStore = Depends(get_store),
) -> List[SeatCoC]:
    return db.list(manufacturer)


@app.post("/api/coc", response_model=SeatCoC, status_code=201)
def create_coc(payload: SeatCoCCreate, db: CoCStore = Depends(get_store)) -> SeatCoC:
    try:
        return db.add(payload)
    except DuplicateCoCError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/api/coc/{coc_id}", response_model=SeatCoC)
def read_coc(coc_id: int, db: CoCStore = Depends(get_store)) -> SeatCoC:
    record = db.get(coc_id)
    if record is None:
        raise HTTPException(status_code=404, detail="CoC not found")
    return record


@app.delete("/api/coc/{coc_id}", status_code=204)
def delete_coc(coc_id: int, db: CoCStore = Depends(get_store)) -> None:
    if not db.delete(coc_id):
        raise HTTPException(status_code=404, detail="CoC not found")


@app.get("/api/summary")
def read_summary(
    reference: Optional[date] = Query(default=None),
    db: CoCStore = Depends(get_store),
) -> dict:
    today = reference or date.today()
    return {
        "reference": today.isoformat(),
        "counts": summarize(db, today),
        "expiring_soon": [r.vin for r in expiring_soon(db, today)],
    }
