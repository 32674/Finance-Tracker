from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import extract
app = FastAPI()
from datetime import datetime, timedelta

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()

    if existing:
        return {"detail": "User already exists"}

    new_user = models.User(email=user.email, password=user.password)
    db.add(new_user)
    db.commit()

    return {"message": "Register successful"}

@app.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if '@' in user.email:
        user_data = db.query(models.User).filter(
            models.User.email == user.email,
            models.User.password == user.password
        ).first()
    else:
        return {"detail": "Invalid email format"}

    if not user_data:
        return {"detail": "Invalid credentials"}

    return {"message": "Login successful", "user_id": user_data.id}

@app.post("/add-expense")
def add_expense(exp: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    db.add(models.Expense(**exp.dict()))
    db.commit()
    return {"message": "Expense added successfully"}

@app.post("/add-income")
def add_income(inc: schemas.IncomeCreate, db: Session = Depends(get_db)):
    db.add(models.Income(**inc.dict()))
    db.commit()
    return {"message": "Income added successfully"}


@app.post("/set-budget")
def set_budget(bud: schemas.BudgetCreate, db: Session = Depends(get_db)):

    existing = db.query(models.Budget).filter(
        models.Budget.user_id == bud.user_id,
        models.Budget.category == bud.category
    ).first()

    if existing:
        existing.amount = bud.amount
        existing.month = bud.month
    else:
        db.add(models.Budget(**bud.dict()))

    db.commit()
    return {"message": "Budget saved successfully"}


@app.get("/dashboard/{user_id}/{month}")
def dashboard(user_id: int, month: int, db: Session = Depends(get_db)):

    income = db.query(func.sum(models.Income.amount)).filter(
        models.Income.user_id == user_id,
        extract('month', models.Income.date) == month
    ).scalar() or 0

    expense = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == user_id,
        extract('month', models.Expense.date) == month
    ).scalar() or 0

    return {
        "income": income,
        "expense": expense,
        "savings": income - expense
    }

@app.get("/transactions/{user_id}")
def transactions(user_id: int, db: Session = Depends(get_db)):
    return {
        "expenses": db.query(models.Expense).filter(models.Expense.user_id == user_id).all(),
        "income": db.query(models.Income).filter(models.Income.user_id == user_id).all()
    }

@app.get("/budget/{user_id}")
def budget(user_id: int, db: Session = Depends(get_db)):
    budgets = db.query(models.Budget).filter(models.Budget.user_id == user_id).all()
    result = []

    for b in budgets:
        spent = db.query(func.sum(models.Expense.amount)).filter(
            models.Expense.user_id == user_id,
            models.Expense.category == b.category,
            extract("month", models.Expense.date) == b.month
        ).scalar() or 0

        percent = (spent / b.amount) * 100 if b.amount else 0

        result.append({
            "category": b.category,
            "amount": b.amount,  # ✅ ADD THIS
            "spent": spent,
            "remaining": b.amount - spent,
            "percent": round(percent, 2)
        })

    return result
@app.delete("/delete/{type}/{id}")
def delete_transaction(type: str, id: int, db: Session = Depends(get_db)):
    if type == "Expense":
        item = db.query(models.Expense).filter(models.Expense.id == id).first()
    else:
        item = db.query(models.Income).filter(models.Income.id == id).first()

    if item:
        db.delete(item)
        db.commit()

    return {"message": "Deleted successfully"}