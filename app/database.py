import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

# Local SQLite file in project root called addresses.db
SQLALCHEMY_DB_URL = "sqlite:///./addresses.db"

engine = create_engine(
    SQLALCHEMY_DB_URL, connect_args = {"check_same_thread": False}
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