from datetime import date

from app.main import get_store, store
from tests.conftest import make_payload

OTHER_VIN = "WDD7654321GFEDCBA"


def body(**overrides) -> dict:
    return make_payload(**overrides).model_dump(mode="json")


def test_index_renders_empty_state(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "No certificates yet" in response.text


def test_index_lists_records(client):
    client.post("/api/coc", json=body())
    text = client.get("/").text
    assert "WDD1234567ABCDEFG" in text
    assert "Comfort S" in text


def test_create_and_read_coc(client):
    created = client.post("/api/coc", json=body())
    assert created.status_code == 201
    coc_id = created.json()["id"]
    assert client.get(f"/api/coc/{coc_id}").json()["vin"] == "WDD1234567ABCDEFG"


def test_create_duplicate_vin_conflicts(client):
    client.post("/api/coc", json=body())
    conflict = client.post("/api/coc", json=body())
    assert conflict.status_code == 409


def test_create_invalid_payload_is_rejected(client):
    payload = body()
    payload["vin"] = "TOOSHORT"
    assert client.post("/api/coc", json=payload).status_code == 422


def test_list_supports_manufacturer_filter(client):
    client.post("/api/coc", json=body())
    client.post("/api/coc", json=body(vin=OTHER_VIN, manufacturer="Lear"))
    assert len(client.get("/api/coc").json()) == 2
    assert [r["vin"] for r in client.get("/api/coc", params={"manufacturer": "Lear"}).json()] == [OTHER_VIN]


def test_read_missing_coc_returns_404(client):
    assert client.get("/api/coc/999").status_code == 404


def test_delete_coc(client):
    coc_id = client.post("/api/coc", json=body()).json()["id"]
    assert client.delete(f"/api/coc/{coc_id}").status_code == 204
    assert client.delete(f"/api/coc/{coc_id}").status_code == 404


def test_summary_with_explicit_reference(client):
    client.post("/api/coc", json=body(expires_on=date(2025, 6, 10)))
    data = client.get("/api/summary", params={"reference": "2025-06-01"}).json()
    assert data["reference"] == "2025-06-01"
    assert data["counts"]["expiring"] == 1
    assert data["expiring_soon"] == ["WDD1234567ABCDEFG"]


def test_summary_defaults_to_today(client):
    data = client.get("/api/summary").json()
    assert data["reference"] == date.today().isoformat()


def test_get_store_returns_module_store():
    assert get_store() is store
