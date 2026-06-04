from fastapi import APIRouter, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

import services.account_service as account_service
from models.models import AccountCreate, AccountUpdate, AccountResponse
from database import get_db

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


@router.get("", response_model=list[AccountResponse])
async def get_all_accounts():
    db: AsyncIOMotorDatabase = get_db()
    return await account_service.get_all_accounts(db)


@router.get("/search", response_model=list[AccountResponse])
async def get_account_by_name(name: str = Query(...)):
    db: AsyncIOMotorDatabase = get_db()
    return await account_service.get_account_by_name(db, name)


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account_by_id(account_id: str):
    db: AsyncIOMotorDatabase = get_db()
    result = await account_service.get_account_by_id(db, account_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found.")
    return result


@router.post("", response_model=AccountResponse, status_code=201)
async def create_account(payload: AccountCreate):
    db: AsyncIOMotorDatabase = get_db()
    result = await account_service.create_account(db, payload)
    if not result:
        raise HTTPException(status_code=404, detail=f"Customer {payload.customer_id} not found.")
    return result


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(account_id: str, payload: AccountUpdate):
    db: AsyncIOMotorDatabase = get_db()
    result = await account_service.update_account(db, account_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found.")
    return result


@router.delete("/{account_id}", status_code=200)
async def delete_account(account_id: str):
    db: AsyncIOMotorDatabase = get_db()
    success = await account_service.delete_account(db, account_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found.")
    return {"message": f"Account {account_id} deleted."}
