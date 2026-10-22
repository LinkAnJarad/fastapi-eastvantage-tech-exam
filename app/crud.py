from typing import List, Optional
from sqlalchemy.orm import Session
from app import models, schemas
from haversine import haversine, Unit # for calculating distance between Earth coords

def get_address(db: Session, address_id: int) -> Optional[models.Address]:
    """
    Retrieve singular address from an ID.
    """
    return db.query(models.Address).filter(models.Address.id == address_id).first()

def get_addresses(db: Session, skip: int = 0, limit: int = 64) -> List[models.Address]:
    return db.query(models.Address).offset(skip).limit(limit).all()

def create_address(db: Session, address: schemas.AddressCreate) -> models.Address:
    """
    Add a new address record to the address table.
    """
    db_address = models.Address(**address.model_dump())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

def update_address(db: Session, db_address: models.Address, update_data: schemas.AddressUpdate) -> models.Address:
    """
    Update an existing address record in the address table given an existing address.
    """

    update_fields = update_data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(db_address, key, value)

    db.commit()
    db.refresh(db_address)
    return db_address

def delete_address(db: Session, db_address: models.Address) -> None:
    """
    Delete an existing address in the address table.
    """

    db.delete(db_address)
    db.commit()

def get_addresses_within_distance(db: Session, target_lat: float, target_lon: float, max_distance_km: float) -> List[dict]:
    """
    Retrieve all addressses in the table that is within and on a given radius `max_distance_km` 
    given target coordinates `target_lat` and `target_lon`.
    """

    all_addresses = db.query(models.Address).all() # Get all addresses from the database; for larger datasets, consider pre-filtering or spatial indexing

    results = []
    target_coords = (target_lat, target_lon)

    for address in all_addresses:
        address_coords = (address.latitude, address.longitude)
        distance_from_target = haversine(target_coords, address_coords, unit=Unit.KILOMETERS) # Calculate distance in kilometers
        if distance_from_target <= max_distance_km:
            results.append(
                {
                    "address": address,
                    "distance_km": distance_from_target
                }
            )
        
    results.sort(key=lambda a: a["distance_km"]) # Sort by distance from target coordinates in ascending order
    return results
