from pydantic import BaseModel
from datetime import date

class ExpenseCreate(BaseModel):
    user_id: int
    amount: float
    category: str
    date: date
    description: str

class IncomeCreate(BaseModel):
    user_id: int
    amount: float
    source: str
    frequency: str
    date: date
    description: str

class BudgetCreate(BaseModel):
    user_id: int
    category: str
    month: int
    amount: float

class UserCreate(BaseModel):
    email: str
    password: str