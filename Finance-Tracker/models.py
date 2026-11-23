from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(100))

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    amount = Column(Float)
    category = Column(String(50))
    date = Column(Date)
    description = Column(String(200))

class Income(Base):
    __tablename__ = "income"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    amount = Column(Float)
    source = Column(String(50))
    frequency = Column(String(20))
    date = Column(Date)
    description = Column(String(200))

class Budget(Base):
    __tablename__ = "budget"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    category = Column(String(50))
    month = Column(String(20))
    amount = Column(Float)