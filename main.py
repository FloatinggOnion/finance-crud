from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
from models import Transaction, Base
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origin = [
    'http://localhost:5173',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TransactionBase(BaseModel):
    amount: float
    category: str
    description: str
    is_income: bool
    date: str


class TransactionModel(TransactionBase):
    id: int

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

Base.metadata.create_all(bind=engine)


@app.post('/transactions/', response_model=TransactionModel)
async def create_transaction(transaction: TransactionBase, db: db_dependency):
    print(transaction.model_dump())
    db_transaction = Transaction(**transaction.model_dump())
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction


@app.get('/transactions/', response_model=list[TransactionModel])
async def get_transactions(db: db_dependency, skip: int=0, limit: int=100):
    transactions = db.query(Transaction).offset(skip).limit(limit).all()

    return transactions


@app.delete('/transactions/{id}')
async def delete_transactions(db: db_dependency, id: int):
    transaction = db.query(Transaction).filter(Transaction.id == id)
    transaction.delete()

    db.commit()

    return {"message": "All transactions deleted"}