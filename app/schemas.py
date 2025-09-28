from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 车辆模型
default_car_battery = 100
default_car_status = 0

class CarBase(BaseModel):
    name: str
    plate: str
    status: int = Field(default=default_car_status)
    battery: int = Field(default=default_car_battery)
    qrcode: Optional[str] = None

class CarCreate(CarBase):
    pass

class Car(CarBase):
    id: int
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 用户模型
default_user_role = 0
default_user_deposit = 0.0

class UserBase(BaseModel):
    openid: Optional[str] = None
    nickname: Optional[str] = None
    phone: Optional[str] = None
    role: int = Field(default=default_user_role)
    deposit: float = Field(default=default_user_deposit)

class UserCreate(UserBase):
    phone: str
    password: str

class UserLogin(BaseModel):
    phone: str
    password: str

class User(UserBase):
    id: int
    
    class Config:
        orm_mode = True

# 订单模型
class RentOrderBase(BaseModel):
    user_id: int
    car_id: int

class RentOrderCreate(RentOrderBase):
    pass

class RentOrder(RentOrderBase):
    id: int
    start_at: datetime
    end_at: Optional[datetime] = None
    fee: Optional[float] = None
    
    class Config:
        orm_mode = True

# 租车响应
class RentResponse(BaseModel):
    order_id: int
    start_at: datetime

# 还车响应
class ReturnResponse(BaseModel):
    order_id: int
    end_at: datetime
    fee: float

# WebSocket状态推送
class CarStatusUpdate(BaseModel):
    car_id: int
    battery: int
    status: int