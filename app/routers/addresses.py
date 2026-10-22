import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/addresses",
    tags=["addresses"],
)


@router.get("/", response_model=List[schemas.AddressResponse])
def read_addresses(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(64, ge=1, description="Pagination limit"),
    db: Session = Depends(get_db)
):
    """
    Retrieve addresses with pagination support. Default limit is 64.
    """
    addresses = crud.get_addresses(db, skip=skip, limit=limit)
    return addresses

@router.get("/nearby", response_model=List[schemas.AddressWithDistance])
def get_nearby_addresses(
    target_lat: float = Query(..., ge=-90.0, le=90.0, description="Target latitude"),
    target_lon: float = Query(..., ge=-180.0, le=180.0, description="Target longitude"),
    max_distance_km: float = Query(..., gt=0.0, description="Max radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Retrieve addresses within a given distance of target latitude and longitude
    and their Haversine distance to the target latitude and longitude
    """

    logger.info(
        "Searching addresses within %.2f km of lat: %.4f, lon: %.4f",
        max_distance_km, target_lat, target_lon
    )

    nearby_addresses = crud.get_addresses_within_distance(
        db, target_lat=target_lat, target_lon=target_lon, 
        max_distance_km=max_distance_km
    )

    # Format to response model of `schemas.AddressWithDistance`. 
    # The `get_addresses_within_distance` function returns a list of dicts with the address and distance as keys,
    # so we need to convert it to the response model.
    response = []
    for item in nearby_addresses:
        address = item["address"]
        response.append(
            schemas.AddressWithDistance(
                id=address.id,
                street=address.street,
                barangay=address.barangay,
                city=address.city,
                region=address.region,
                postal_code=address.postal_code,
                latitude=address.latitude,
                longitude=address.longitude,
                distance_km=item["distance_km"]
            )
        )

    return response

@router.get("/{address_id}", response_model=schemas.AddressResponse)
def read_address(address_id: int, db: Session = Depends(get_db)):
    """
    Fetch a singular address by its ID.
    """

    fetched_address = crud.get_address(db, address_id=address_id)

    if not fetched_address:
        logger.warning("Attempting to fetch Address with ID %d not found", address_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID {address_id} not found."
        )
    return fetched_address

@router.patch("/{address_id}", response_model=schemas.AddressResponse)
def update_address(address_id: int, update_data: schemas.AddressUpdate, db: Session = Depends(get_db)):
    """
    Update an existing address by its ID.
    """

    existing_address = crud.get_address(db, address_id=address_id)

    if not existing_address:
        logger.warning("Attempting to update Address with ID %d not found", address_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID {address_id} not found."
        )

    logger.info("Updating address with ID %d", address_id)

    updated_address = crud.update_address(
        db, db_address=existing_address, update_data=update_data
    )

    return updated_address

@router.post("/", response_model=schemas.AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(address: schemas.AddressCreate, db: Session = Depends(get_db)):
    """
    Create a new address and insert it into the address table.
    """

    logger.info("Creating a new address with fields: %s, %s, %s, %s, %s", address.street, address.barangay, address.city, address.region, address.postal_code)

    new_address = crud.create_address(db, address=address)

    return new_address


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(address_id: int, db: Session = Depends(get_db)):
    """
    Delete an existing address by its ID.
    """

    existing_address = crud.get_address(db, address_id=address_id)

    if not existing_address:
        logger.warning("Attempting to delete Address with ID %d not found", address_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with ID {address_id} not found."
        )

    logger.info("Deleting address with ID %d", address_id)

    crud.delete_address(db, db_address=existing_address)
    
    return None

    