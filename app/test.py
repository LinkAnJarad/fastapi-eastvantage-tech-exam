from app.database import get_db, Base, engine
from app import models, schemas

Base.metadata.create_all(bind=engine)

db = next(get_db())
# Add sample entries to address table if it is empty
# sample1 = models.Address(
#     street="1000 EDSA",
#     barangay="Barangay Kalusugan",
#     city="Quezon City",
#     region="National Capital Region",
#     postal_code="1104",
#     latitude=14.6091,
#     longitude=121.0223
# )

# sample2 = models.Address(
#     street="2000 Roxas Blvd",
#     barangay="Barangay Malate",
#     city="Manila",
#     region="National Capital Region",
#     postal_code="1004",
#     latitude=14.5833,
#     longitude=120.9667
# )

# sample3 = models.Address(
#     street="3000 Bonifacio Global City",
#     barangay="Barangay Fort Bonifacio",
#     city="Taguig City",
#     region="National Capital Region",
#     postal_code="1634",
#     latitude=14.5547,
#     longitude=121.0450
# )

# sample4 = models.Address(
#     street="4000 Ayala Avenue",
#     barangay="Barangay San Lorenzo",
#     city="Makati City",
#     region="National Capital Region",
#     postal_code="1226",
#     latitude=14.5547,
#     longitude=121.0244
# )

# sample5 = models.Address(
#     street="5000 Quezon Avenue",
#     barangay="Barangay Paligsahan",
#     city="Quezon City",
#     region="National Capital Region",
#     postal_code="1103",
#     latitude=14.6391,
#     longitude=121.0294
# )

# db.add_all([sample1, sample2, sample3, sample4, sample5])
# db.commit()


# Test routes

from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routers import addresses

app = FastAPI()
app.include_router(addresses.router)

client = TestClient(app)

# Test get nearby addresses route
def test_get_nearby_addresses():
    response = client.get(
        "/addresses/nearby",
        params={
            "target_lat": 14.6091,
            "target_lon": 121.0223,
            "max_distance_km": 5.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for item in data:
        assert "id" in item
        assert "street" in item
        assert "barangay" in item
        assert "city" in item
        assert "region" in item
        assert "postal_code" in item
        assert "latitude" in item
        assert "longitude" in item
        assert "distance_km" in item
    print("Nearby addresses in order of proximity to target coordinates:")
    for item in data:
        print(f"Address ID: {item['id']}, Street: {item['street']}, Distance: {item['distance_km']:.2f} km")
        

test_get_nearby_addresses()