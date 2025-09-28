from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
from datetime import datetime, timedelta
import math
import bcrypt

from .models import Car, User, RentOrder
from .schemas import CarCreate, UserCreate, RentOrderCreate

# 车辆相关CRUD

async def get_cars(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Car]:
    result = await session.execute(select(Car).offset(skip).limit(limit))
    return result.scalars().all()

async def get_car(session: AsyncSession, car_id: int) -> Optional[Car]:
    result = await session.execute(select(Car).where(Car.id == car_id))
    return result.scalar_one_or_none()

async def get_all_cars(session: AsyncSession) -> List[Car]:
    result = await session.execute(select(Car))
    return result.scalars().all()

async def create_car(session: AsyncSession, car: CarCreate) -> Car:
    db_car = Car(
        name=car.name,
        plate=car.plate,
        status=car.status,
        battery=car.battery,
        qrcode=car.qrcode
    )
    session.add(db_car)
    await session.commit()
    await session.refresh(db_car)
    return db_car

async def update_car_status(session: AsyncSession, car_id: int, status: int) -> Optional[Car]:
    result = await session.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    if car:
        car.status = status
        await session.commit()
        await session.refresh(car)
    return car

async def update_car_battery(session: AsyncSession, car_id: int, battery: int) -> Optional[Car]:
    result = await session.execute(select(Car).where(Car.id == car_id))
    car = result.scalar_one_or_none()
    if car:
        car.battery = battery
        await session.commit()
        await session.refresh(car)
    return car

# 用户相关CRUD

async def get_users(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    result = await session.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_openid(session: AsyncSession, openid: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.openid == openid))
    return result.scalar_one_or_none()

async def get_user_by_phone(session: AsyncSession, phone: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.phone == phone))
    return result.scalar_one_or_none()

# 密码哈希处理
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

async def create_user(session: AsyncSession, user: UserCreate) -> User:
    # 密码哈希处理
    hashed_password = hash_password(user.password)
    
    db_user = User(
        openid=user.openid,
        nickname=user.nickname,
        phone=user.phone,
        password=hashed_password,
        role=getattr(user, 'role', 0),  # 默认角色为游客(0)
        deposit=getattr(user, 'deposit', 0.0)  # 默认押金为0
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

# 订单相关CRUD

async def get_orders(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[RentOrder]:
    result = await session.execute(select(RentOrder).offset(skip).limit(limit))
    return result.scalars().all()

async def get_orders_by_user(session: AsyncSession, user_id: int) -> List[RentOrder]:
    result = await session.execute(select(RentOrder).where(RentOrder.user_id == user_id))
    return result.scalars().all()

async def get_order(session: AsyncSession, order_id: int) -> Optional[RentOrder]:
    result = await session.execute(select(RentOrder).where(RentOrder.id == order_id))
    return result.scalar_one_or_none()

async def create_order(session: AsyncSession, order: RentOrderCreate) -> RentOrder:
    db_order = RentOrder(
        user_id=order.user_id,
        car_id=order.car_id
    )
    session.add(db_order)
    await session.commit()
    await session.refresh(db_order)
    return db_order

async def return_car(session: AsyncSession, order_id: int) -> Optional[RentOrder]:
    result = await session.execute(select(RentOrder).where(RentOrder.id == order_id))
    order = result.scalar_one_or_none()
    
    if order and not order.end_at:
        # 计算费用
        order.end_at = datetime.now()
        duration = (order.end_at - order.start_at).total_seconds() / 60  # 转换为分钟
        order.fee = max(1.0, math.ceil(duration) * 0.5)  # 最小1元，每分钟0.5元
        
        # 更新车辆状态
        await session.execute(
            update(Car)
            .where(Car.id == order.car_id)
            .values(status=0)
        )
        
        await session.commit()
        await session.refresh(order)
    
    return order