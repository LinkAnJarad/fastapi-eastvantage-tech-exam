"""
End-to-end tests for the Address Book API.

The suite covers CRUD, validation, error handling and the proximity search.
"""

import pytest




# Health

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# Create

def _create(client, payload):
    """
    Helper func: POST an address and return the decoded JSON body.
    """
    response = client.post("/addresses/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()

def test_create_address(client, sample_address_payload):
    body = _create(client, sample_address_payload)

    assert body["id"] == 1
    for field in (
        "street",
        "barangay",
        "city",
        "region",
        "postal_code",
        "latitude",
        "longitude",
    ):
        assert body[field] == sample_address_payload[field]


def test_create_address_persists_to_database(client, sample_address_payload, db_session):
    from app import models

    _create(client, sample_address_payload)

    stored = db_session.query(models.Address).one()
    assert stored.street == sample_address_payload["street"]
    assert stored.latitude == sample_address_payload["latitude"]


# Validation

@pytest.mark.parametrize(
    "field, value",
    [
        ("street", ""),
        ("barangay", ""),
        ("city", ""),
        ("region", ""),
        ("postal_code", ""),
        ("latitude", 90.1),
        ("latitude", -90.1),
        ("longitude", 180.1),
        ("longitude", -180.1),
    ],
)
def test_create_address_rejects_invalid_values(client, sample_address_payload, field, value):
    sample_address_payload[field] = value

    response = client.post("/addresses/", json=sample_address_payload)

    assert response.status_code == 422
    assert field in response.text


@pytest.mark.parametrize("field", ["street", "barangay", "city", "region", "postal_code",
                                  "latitude", "longitude"])
def test_create_address_requires_all_fields(client, sample_address_payload, field):
    del sample_address_payload[field]

    response = client.post("/addresses/", json=sample_address_payload)

    assert response.status_code == 422


# Read

def test_list_addresses(client, sample_addresses):
    for payload in sample_addresses:
        _create(client, payload)

    response = client.get("/addresses/")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_list_addresses_pagination(client, sample_addresses):
    for payload in sample_addresses:
        _create(client, payload)

    response = client.get("/addresses/", params={"skip": 1, "limit": 1})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_address_by_id(client, sample_address_payload):
    created = _create(client, sample_address_payload)

    response = client.get(f"/addresses/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_address_not_found(client):
    response = client.get("/addresses/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# Update

def test_update_address(client, sample_address_payload):
    created = _create(client, sample_address_payload)

    response = client.patch(
        f"/addresses/{created['id']}",
        json={"street": "1001 EDSA", "latitude": 14.61, "longitude": 121.03},
    )

    assert response.status_code == 200
    assert response.json()["street"] == "1001 EDSA"
    assert response.json()["latitude"] == 14.61
    # Untouched fields keep their original value.
    assert response.json()["city"] == sample_address_payload["city"]


def test_update_address_not_found(client):
    response = client.patch("/addresses/999", json={"street": "Nowhere"})
    assert response.status_code == 404


def test_update_address_validates_coordinates(client, sample_address_payload):
    created = _create(client, sample_address_payload)

    response = client.patch(f"/addresses/{created['id']}", json={"latitude": 95.0})

    assert response.status_code == 422

def test_update_address_empty_body_changes_nothing(client, sample_address_payload):
    created = _create(client, sample_address_payload)

    response = client.patch(f"/addresses/{created['id']}", json={})

    assert response.status_code == 200
    assert response.json() == created


# Delete

def test_delete_address(client, sample_address_payload):
    created = _create(client, sample_address_payload)

    response = client.delete(f"/addresses/{created['id']}")
    assert response.status_code == 204

    # The row is gone.
    assert client.get(f"/addresses/{created['id']}").status_code == 404
    assert client.get("/addresses/").json() == []


def test_delete_address_not_found(client):
    response = client.delete("/addresses/999")
    assert response.status_code == 404


# Nearby search

def test_get_nearby_addresses(client, sample_addresses):
    for payload in sample_addresses:
        _create(client, payload)

    response = client.get(
        "/addresses/nearby",
        params={
            "target_lat": 14.6091,
            "target_lon": 121.0223,
            "max_distance_km": 10.0,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    for item in data:
        assert "distance_km" in item
        assert item["distance_km"] <= 10.0

    # Results are sorted by distance, closest first.
    distances = [item["distance_km"] for item in data]
    assert distances == sorted(distances)
    assert data[0]["street"] == "1000 EDSA"
    assert data[0]["distance_km"] == pytest.approx(0.0, abs=0.01)


def test_get_nearby_addresses_respects_the_radius(client, sample_addresses):
    """
    A tighter radius excludes the addresses that sit just outside it.
    """
    for payload in sample_addresses:
        _create(client, payload)

    response = client.get(
        "/addresses/nearby",
        params={
            "target_lat": 14.6091,
            "target_lon": 121.0223,
            "max_distance_km": 1.0,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["street"] == "1000 EDSA"


def test_get_nearby_addresses_excludes_far_away(client, sample_addresses):
    for payload in sample_addresses:
        _create(client, payload)

    # A target far away from Metro Manila.
    response = client.get(
        "/addresses/nearby",
        params={
            "target_lat": 1.0,
            "target_lon": 1.0,
            "max_distance_km": 10.0,
        },
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_nearby_addresses_requires_parameters(client):
    """
    A nearby search requires all three parameters.
    """
    response = client.get("/addresses/nearby", params={"target_lat": 14.6091})
    assert response.status_code == 422


def test_get_nearby_addresses_rejects_invalid_coordinates(client):
    response = client.get(
        "/addresses/nearby",
        params={
            "target_lat": 100.0,
            "target_lon": 121.0,
            "max_distance_km": 5.0,
        },
    )
    assert response.status_code == 422


def test_get_nearby_addresses_rejects_non_positive_radius(client):
    response = client.get(
        "/addresses/nearby",
        params={
            "target_lat": 14.6091,
            "target_lon": 121.0223,
            "max_distance_km": 0.0,
        },
    )
    assert response.status_code == 422
