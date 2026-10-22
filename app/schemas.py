from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class AddressBase(BaseModel):
    """
    Schema for read/write on the address table.
    """

    street: str = Field(..., min_length=1, max_length=255, examples=["1000 EDSA"])
    barangay: str = Field(..., min_length=1, max_length=255, examples=["Barangay Kalusugan"])
    city: str = Field(..., min_length=1, max_length=255, examples=["Quezon City"])
    region: str = Field(..., min_length=1, max_length=255, examples=["National Capital Region"])
    postal_code: str = Field(..., min_length=1, max_length=20, examples=["1104"])

    # Coordinates validation
    latitude: float = Field(..., ge=-90.0, le=90.0,
        description = "Latitude should be between -90 and 90.",
        examples = [45.0033]
    )

    longitude: float = Field(..., ge=-180.0, le=180.0,
        description = "Longitude should be between -180 and 180.",
        examples = [110.0033]
    )

class AddressCreate(AddressBase):
    """
    Schema for creating new addresses
    """
    pass

class AddressResponse(AddressBase):
    """
    Schema for returned addresses; includes the db primary key.
    """
    id: int

    model_config = ConfigDict(from_attributes=True)

class AddressUpdate(BaseModel):
    """
    Schema for updating addresses, all fields optional.
    """
    street: Optional[str] = Field(None, min_length=1, max_length=255, examples=["1000 EDSA"])
    barangay: Optional[str] = Field(None, min_length=1, max_length=255, examples=["Barangay Kalusugan"])
    city: Optional[str] = Field(None, min_length=1, max_length=255, examples=["Quezon City"])
    region: Optional[str] = Field(None, min_length=1, max_length=255, examples=["National Capital Region"])
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20, examples=["1104"])

    # Coordinates validation
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0,
        description = "Latitude should be between -90 and 90.",
        examples = [45.0033]
    )

    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0,
        description = "Longitude should be between -180 and 180.",
        examples = [110.0033]
    )

class AddressWithDistance(AddressResponse):
    """
    Schema for addresses when searching via proximity.
    """
    distance_km: float = Field(..., description="Distance in kilometers from search coordinates")
