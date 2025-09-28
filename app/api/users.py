from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import jwt
from typing import Optional

from ..db import get_session
from ..schemas import UserCreate, UserLogin, User
from ..crud import create_user as crud_create_user
from ..crud import get_user_by_phone, verify_password
from ..models import User as UserModel

router = APIRouter(prefix="/users", tags=["users"])

# 临时密钥，实际应用中应使用环境变量
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

# 创建访问令牌
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone: str = payload.get("sub")
        if phone is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_phone(session, phone)
    if user is None:
        raise credentials_exception
    return user

# 用户注册
@router.post("/register", response_model=User)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    db_user = await get_user_by_phone(session, phone=user.phone)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="该手机号已被注册"
        )
    return await crud_create_user(session=session, user=user)

# 用户登录
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user = await get_user_by_phone(session, phone=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.phone, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "role": user.role}

# 获取当前用户信息
@router.get("/me", response_model=User)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    return current_user