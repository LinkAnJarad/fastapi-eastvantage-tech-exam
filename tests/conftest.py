"""
Shared pytest fixtures.

Each test runs against a throwaway SQLite database so the suite never
touches the development `addresses.db` file.
"""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

# Use temporary SQLite file for testing; uses PID to avoid collisions when running tests in parallel. Database url is stored in an env var.
_TMP_DB = os.path.join(tempfile.gettempdir(), f"addressbook_test_{os.getpid()}.db")
os.environ["ADDRESSBOOK_DATABASE_URL"] = f"sqlite:///{_TMP_DB}"

from app.database import Base, engine 
from app.main import app 


@pytest.fixture(autouse=True)
def reset_db():
    """
    Drop and recreate all tables so every test starts from a clean slate.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """
    A TestClient bound to the FastAPI app.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    """
    A direct SQLAlchemy session, for assertions that bypass the HTTP layer.
    """
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_addresses():
    """
    Valid address samples around Metro Manila.
    """
    return [
        {
            "street": "1000 EDSA",
            "barangay": "Barangay Kalusugan",
            "city": "Quezon City",
            "region": "National Capital Region",
            "postal_code": "1104",
            "latitude": 14.6091,
            "longitude": 121.0223,
        },
        {
            "street": "2000 Roxas Blvd",
            "barangay": "Barangay Malate",
            "city": "Manila",
            "region": "National Capital Region",
            "postal_code": "1004",
            "latitude": 14.5833,
            "longitude": 120.9667,
        },
        {
            "street": "3000 Bonifacio Global City",
            "barangay": "Barangay Fort Bonifacio",
            "city": "Taguig City",
            "region": "National Capital Region",
            "postal_code": "1634",
            "latitude": 14.5547,
            "longitude": 121.0450,
        },
    ]


@pytest.fixture
def sample_address_payload(sample_addresses):
    """A single valid address body, anchored in Quezon City, Philippines.

    This fixture requests another fixture, which pytest resolves before
    handing the value over.
    """
    return dict(sample_addresses[0])
