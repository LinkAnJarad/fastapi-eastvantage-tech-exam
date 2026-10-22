import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

# Local SQLite file in project root called addresses.db.
# Overridable via the ADDRESSBOOK_DATABASE_URL env var (used by the test suite
# to run against a throwaway database).
SQLALCHEMY_DB_URL = os.getenv(
    "ADDRESSBOOK_DATABASE_URL",
    "sqlite:///./addresses.db",
)

engine = create_engine(
    SQLALCHEMY_DB_URL,
    # SQLite only: the sync endpoints run in FastAPI's threadpool, so the
    # connection must be usable from a different thread than the one that
    # opened it. Other backends do not accept this argument.
    connect_args={"check_same_thread": False}
    if SQLALCHEMY_DB_URL.startswith("sqlite")
    else {},
)

SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind=engine
)

Base = declarative_base()



def get_db():
    """
    Generator to yield a db session for a request
    then making sure to close the session after it completes.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()