from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Address(Base):
    """
    Base database model for storing addresses + coordinates.
    Based on Philippine address conventions.
    """
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    barangay: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(255), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)

    # Coordinates
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self):
        return f"Address(id={self.id}, street='{self.street}', barangay='{self.barangay}', city='{self.city}', region='{self.region}', postal_code='{self.postal_code}', latitude={self.latitude}, longitude={self.longitude})"

    
