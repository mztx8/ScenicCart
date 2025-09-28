from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .. import crud, schemas, models
from ..db import get_session

router = APIRouter(
    prefix="/cars",
    tags=["cars"],
)

@router.get("/", response_model=List[schemas.Car])
async def read_cars(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    """获取车辆列表"""
    cars = await crud.get_cars(session, skip=skip, limit=limit)
    return cars

@router.get("/{car_id}", response_model=schemas.Car)
async def read_car(car_id: int, session: AsyncSession = Depends(get_session)):
    """获取单个车辆详情"""
    db_car = await crud.get_car(session, car_id=car_id)
    if db_car is None:
        raise HTTPException(status_code=404, detail="车辆不存在")
    return db_car

@router.post("/", response_model=schemas.Car)
async def create_car(car: schemas.CarCreate, session: AsyncSession = Depends(get_session)):
    """创建新车辆"""
    return await crud.create_car(session=session, car=car)

@router.put("/{car_id}/status", response_model=schemas.Car)
async def update_car_status(car_id: int, status: int, session: AsyncSession = Depends(get_session)):
    """更新车辆状态"""
    db_car = await crud.update_car_status(session=session, car_id=car_id, status=status)
    if db_car is None:
        raise HTTPException(status_code=404, detail="车辆不存在")
    return db_car

@router.put("/{car_id}/battery", response_model=schemas.Car)
async def update_car_battery(car_id: int, battery: int, session: AsyncSession = Depends(get_session)):
    """更新车辆电量"""
    # 验证电量范围
    if battery < 0 or battery > 100:
        raise HTTPException(status_code=400, detail="电量必须在0-100之间")
    
    db_car = await crud.update_car_battery(session=session, car_id=car_id, battery=battery)
    if db_car is None:
        raise HTTPException(status_code=404, detail="车辆不存在")
    return db_car