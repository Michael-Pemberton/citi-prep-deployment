import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "bankdb")

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    global client, db
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    # Create unique indexes
    await db.customers.create_index("email", unique=True)
    await db.accounts.create_index("account_number", unique=True)


async def close_db():
    global client
    if client:
        client.close()


def get_db():
    return db
