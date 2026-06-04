from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class AccountType(str, Enum):
    Savings = "Savings"
    Checking = "Checking"


# --- Request / Response Models ---

class AccountCreate(BaseModel):
    account_number: str
    account_type: AccountType
    balance: float
    customer_id: str  # MongoDB ObjectId as string


class AccountUpdate(BaseModel):
    account_number: Optional[str] = None
    account_type: Optional[AccountType] = None
    balance: Optional[float] = None


class AccountResponse(BaseModel):
    id: str
    account_number: str
    account_type: AccountType
    balance: float
    customer_id: str


class CustomerCreate(BaseModel):
    name: str
    email: str


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class CustomerResponse(BaseModel):
    id: str
    name: str
    email: str
    accounts: List[AccountResponse] = []
