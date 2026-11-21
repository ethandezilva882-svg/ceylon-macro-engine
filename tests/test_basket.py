from datetime import date

from Backend.models import InflationData

GOOD = {
    "food_weight": 35, "transport_weight": 20, "housing_weight": 25,
    "healthcare_weight": 5, "education_weight": 10,
    "clothing_weight": 3, "other_weight": 2,
}
UPDATED = {
    "food_weight": 30, "transport_weight": 25, "housing_weight": 20,
    "healthcare_weight": 10, "education_weight": 8,
    "clothing_weight": 4, "other_weight": 3,
}


def test_get_basket_404_when_none(client, auth_headers):
    assert client.get("/api/basket", headers=auth_headers).status_code == 404


def test_put_basket_rejects_weights_not_summing_to_100(client, auth_headers):
    bad = {**GOOD, "food_weight": 50}  # sums to 115
    res = client.put("/api/basket", json=bad, headers=auth_headers)
    assert res.status_code == 422
    assert "115" in str(res.json())


def test_put_basket_rejects_negative_weight(client, auth_headers):
    bad = {**GOOD, "food_weight": -5}
    assert client.put("/api/basket", json=bad, headers=auth_headers).status_code == 422


def test_put_creates_then_get_returns_it(client, auth_headers):
    put = client.put("/api/basket", json=GOOD, headers=auth_headers)
    assert put.status_code == 200
    got = client.get("/api/basket", headers=auth_headers)
    assert got.status_code == 200
    assert float(got.json()["food_weight"]) == 35.0


def test_put_twice_updates_in_place(client, auth_headers):
    first = client.put("/api/basket", json=GOOD, headers=auth_headers).json()
    second = client.put("/api/basket", json=UPDATED, headers=auth_headers).json()
    assert first["id"] == second["id"]
    assert float(second["food_weight"]) == 30.0


def test_basket_requires_auth(client):
    assert client.put("/api/basket", json=GOOD).status_code == 401


def test_impact_without_inflation_data_is_honest(client, auth_headers):
    client.put("/api/basket", json=GOOD, headers=auth_headers)
    res = client.get("/api/basket/impact", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["official_inflation_pct"] is None
    assert "not yet available" in body["note"]


def test_impact_computes_headline_change(client, auth_headers, db):
    client.put("/api/basket", json=GOOD, headers=auth_headers)
    db.add(InflationData(date=date(2025, 6, 1), ccpi=100))
    db.add(InflationData(date=date(2026, 6, 1), ccpi=110))
    db.commit()
    res = client.get("/api/basket/impact?from=2025-01-01&to=2026-12-31", headers=auth_headers)
    body = res.json()
    assert body["official_inflation_pct"] == 10.0
    assert body["period_from"] == "2025-06-01"
