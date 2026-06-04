from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.models import CustomerCreate, CustomerUpdate, CustomerResponse, AccountResponse


def _account_doc_to_response(doc: dict) -> AccountResponse:
    return AccountResponse(
        id=str(doc["_id"]),
        account_number=doc["account_number"],
        account_type=doc["account_type"],
        balance=float(doc["balance"]),
        customer_id=str(doc["customer_id"]),
    )


async def _customer_doc_to_response(db, doc: dict) -> CustomerResponse:
    customer_id = doc["_id"]
    accounts_cursor = db.accounts.find({"customer_id": customer_id})
    accounts = [_account_doc_to_response(a) async for a in accounts_cursor]
    return CustomerResponse(
        id=str(customer_id),
        name=doc["name"],
        email=doc["email"],
        accounts=accounts,
    )


async def get_all_customers(db: AsyncIOMotorDatabase):
    cursor = db.customers.find()
    return [await _customer_doc_to_response(db, doc) async for doc in cursor]


async def get_customer_by_id(db: AsyncIOMotorDatabase, customer_id: str):
    try:
        oid = ObjectId(customer_id)
    except InvalidId:
        return None
    doc = await db.customers.find_one({"_id": oid})
    if not doc:
        return None
    return await _customer_doc_to_response(db, doc)


async def get_customer_by_name(db: AsyncIOMotorDatabase, name: str):
    cursor = db.customers.find({"name": {"$regex": name, "$options": "i"}})
    return [await _customer_doc_to_response(db, doc) async for doc in cursor]


async def create_customer(db: AsyncIOMotorDatabase, payload: CustomerCreate):
    doc = {"name": payload.name, "email": payload.email}
    result = await db.customers.insert_one(doc)
    doc["_id"] = result.inserted_id
    return await _customer_doc_to_response(db, doc)


async def update_customer(db: AsyncIOMotorDatabase, customer_id: str, payload: CustomerUpdate):
    try:
        oid = ObjectId(customer_id)
    except InvalidId:
        return None
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        doc = await db.customers.find_one({"_id": oid})
        return await _customer_doc_to_response(db, doc) if doc else None
    result = await db.customers.find_one_and_update(
        {"_id": oid},
        {"$set": updates},
        return_document=True,
    )
    if not result:
        return None
    return await _customer_doc_to_response(db, result)


async def delete_customer(db: AsyncIOMotorDatabase, customer_id: str):
    try:
        oid = ObjectId(customer_id)
    except InvalidId:
        return False
    # Delete associated accounts first
    await db.accounts.delete_many({"customer_id": oid})
    result = await db.customers.delete_one({"_id": oid})
    return result.deleted_count > 0
