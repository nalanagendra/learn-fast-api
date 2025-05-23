from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Users
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from .auth import get_current_user

router = APIRouter(
  prefix="/user",
  tags=['user']
)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class ChangePasswordRequest(BaseModel):
  old_password: str = Field(min_length=4, max_length=20)
  new_password: str = Field(min_length=4, max_length=20)
  
class ChangePhoneNumber(BaseModel):
  phone_number: str = Field(min_length=12, max_length=20)
  


@router.get('/me', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication failed')
  
  user_model = db.query(Users).filter(Users.id == user.get('user_id')).first()
  return {
    "id": user_model.id,
    "username": user_model.username,
    "first_name": user_model.first_name,
    "last_name": user_model.last_name,
    "email": user_model.email,
    "role": user_model.role,
    "phone_number": user_model.phone_number,
  }

@router.post('/change_password', status_code=status.HTTP_204_NO_CONTENT)
async def update_password(user: user_dependency, db: db_dependency, request: ChangePasswordRequest):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication failed')
  
  user_model = db.query(Users).filter(Users.id == user.get('user_id')).first()

  if not bcrypt_context.verify(request.old_password, user_model.hashed_password):
    raise HTTPException(status_code=401, detail='Error on password change')
  
  user_model.hashed_password = bcrypt_context.hash(request.new_password)
  db.add(user_model)
  db.commit()


@router.post('/phone_number', status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(user: user_dependency, db: db_dependency, request: ChangePhoneNumber):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication failed')
  
  user_model = db.query(Users).filter(Users.id == user.get('user_id')).first()
  
  user_model.phone_number = request.phone_number
  db.add(user_model)
  db.commit()
