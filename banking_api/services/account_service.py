from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.models import AccountCreate, AccountUpdate, AccountResponse


def _doc_to_response(doc: dict) -> AccountResponse:
    return AccountResponse(
        id=str(doc["_id"]),
        account_number=doc["account_number"],
        account_type=doc["account_type"],
        balance=float(doc["balance"]),
        customer_id=str(doc["customer_id"]),
    )


async def get_all_accounts(db: AsyncIOMotorDatabase):
    cursor = db.accounts.find()
    return [_doc_to_response(doc) async for doc in cursor]


async def get_account_by_id(db: AsyncIOMotorDatabase, account_id: str):
    try:
        oid = ObjectId(account_id)
    except InvalidId:
        return None
    doc = await db.accounts.find_one({"_id": oid})
    return _doc_to_response(doc) if doc else None


async def get_account_by_name(db: AsyncIOMotorDatabase, name: str):
    # Find customers matching name, then find their accounts
    customer_cursor = db.customers.find({"name": {"$regex": name, "$options": "i"}})
    customer_ids = [doc["_id"] async for doc in customer_cursor]
    if not customer_ids:
        return []
    cursor = db.accounts.find({"customer_id": {"$in": customer_ids}})
    return [_doc_to_response(doc) async for doc in cursor]


async def create_account(db: AsyncIOMotorDatabase, payload: AccountCreate):
    try:
        customer_oid = ObjectId(payload.customer_id)
    except InvalidId:
        return None
    customer = await db.customers.find_one({"_id": customer_oid})
    if not customer:
        return None
    doc = {
        "account_number": payload.account_number,
        "account_type": payload.account_type,
        "balance": payload.balance,
        "customer_id": customer_oid,
    }
    result = await db.accounts.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_response(doc)


async def update_account(db: AsyncIOMotorDatabase, account_id: str, payload: AccountUpdate):
    try:
        oid = ObjectId(account_id)
    except InvalidId:
        return None
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        doc = await db.accounts.find_one({"_id": oid})
        return _doc_to_response(doc) if doc else None
    result = await db.accounts.find_one_and_update(
        {"_id": oid},
        {"$set": updates},
        return_document=True,
    )
    return _doc_to_response(result) if result else None


async def delete_account(db: AsyncIOMotorDatabase, account_id: str):
    try:
        oid = ObjectId(account_id)
    except InvalidId:
        return False
    result = await db.accounts.delete_one({"_id": oid})
    return result.deleted_count > 0
