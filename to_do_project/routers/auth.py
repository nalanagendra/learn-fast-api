from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from models import Users
from passlib.context import CryptContext
from starlette import status
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from database import SessionLocal
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

router = APIRouter(
  prefix="/auth",
  tags=['auth']
)

SECRET_KEY = 'u&Kf9#Zb7@pX$Lq3mT!vR1sW^jNd8AqB3Hc!mU4@Zr9#Ep$kYw7^tLn2@MbFgXsVnF!9tQ@7#DwLz%Yb&VxCmU$3HqRpJ1eWp$3K#zYw1@NcFt9^VmLXqRb6!UdA2EgPh^N@7mLf$KwX1!RpTzCq9AV3#Ey6Db8s'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class Create_User_Request(BaseModel):
  email: str = Field(min_length=4, max_length=40)
  username: str = Field(min_length=4, max_length=40)
  first_name: str = Field(min_length=4, max_length=40)
  last_name: str = Field(min_length=4, max_length=40)
  password: str = Field(min_length=4, max_length=20)
  role: str = Field(min_length=4, max_length=20)
  
class Token(BaseModel):
  access_token: str
  token_type: str
  
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db):
  user = db.query(Users).filter(Users.username == username).first()
  if not user:
    return False
  
  if not bcrypt_context.verify(password, user.hashed_password):
    return False
  
  return user


def create_access_token(username: str, user_id: int, user_role:str, expires_delta: timedelta):
  encode = {'sub': username, 'id': user_id, 'user_role': user_role}
  expires = datetime.now(timezone.utc) + expires_delta
  encode.update({'exp': expires})
  return jwt.encode(encode, SECRET_KEY, ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
  try:
    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    username: str = payload.get('sub')
    user_id: int = payload.get('id')
    user_role: str = payload.get('user_role')
    
    if username is None or user_id is None:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
    
    return {'username': username, 'user_id': user_id, 'user_role': user_role}
  
  except JWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
  


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: Create_User_Request):
  create_user_model = Users(
    email = create_user_request.email,
    username = create_user_request.username,
    first_name = create_user_request.first_name,
    last_name = create_user_request.last_name,
    hashed_password = bcrypt_context.hash(create_user_request.password),
    is_active = True,
    role = create_user_request.role
  )
  
  db.add(create_user_model)
  db.commit()

@router.post('/token', response_model=Token)
async def login_for_access_token(
  form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
  db: db_dependency,
):
  user = authenticate_user(form_data.username, form_data.password, db)
  
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
  
  token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
  return {
    'access_token': token,
    'token_type': 'bearer'
  }
