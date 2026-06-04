from fastapi import APIRouter, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

import services.customer_service as service
from models.models import CustomerCreate, CustomerUpdate, CustomerResponse
from database import get_db

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get("", response_model=list[CustomerResponse])
async def get_all():
    db: AsyncIOMotorDatabase = get_db()
    return await service.get_all_customers(db)


@router.get("/search", response_model=list[CustomerResponse])
async def search(name: str = Query(...)):
    db: AsyncIOMotorDatabase = get_db()
    return await service.get_customer_by_name(db, name)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_by_id(customer_id: str):
    db: AsyncIOMotorDatabase = get_db()
    result = await service.get_customer_by_id(db, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found.")
    return result


@router.post("", response_model=CustomerResponse, status_code=201)
async def create(payload: CustomerCreate):
    db: AsyncIOMotorDatabase = get_db()
    return await service.create_customer(db, payload)


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update(customer_id: str, payload: CustomerUpdate):
    db: AsyncIOMotorDatabase = get_db()
    result = await service.update_customer(db, customer_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found.")
    return result


@router.delete("/{customer_id}", status_code=200)
async def delete(customer_id: str):
    db: AsyncIOMotorDatabase = get_db()
    success = await service.delete_customer(db, customer_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found.")
    return {"message": f"Customer {customer_id} deleted."}
