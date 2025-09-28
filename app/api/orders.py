from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .. import crud, schemas, models
from ..db import get_session
from .users import get_current_user
from ..models import Car, RentOrder

router = APIRouter(
    prefix="",
    tags=["orders"],
)

# 注意：这个版本使用自定义的事务管理，避免与CRUD函数中的commit冲突
@router.post("/rent/{car_id}", response_model=schemas.RentResponse)
async def rent_car(car_id: int, current_user: models.User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """租车接口"""
    try:
        # 检查车辆是否存在且可租
        car = await session.get(Car, car_id)
        if not car or car.status != 0:
            raise HTTPException(status_code=400, detail="车辆不可租")
        
                # 更新车辆状态
        car.status = 1
        
        # 创建订单
        db_order = RentOrder(
            user_id=current_user.id,
            car_id=car_id
        )
        session.add(db_order)
        
        # 提交事务
        await session.commit()
        
        return {
            "order_id": db_order.id,
            "start_at": db_order.start_at
        }
    except Exception as e:
        # 如果是HTTPException，直接抛出
        if isinstance(e, HTTPException):
            raise e
        # 其他错误返回500
        raise HTTPException(status_code=500, detail=f"租车过程中发生错误: {str(e)}")

@router.post("/return/{order_id}", response_model=schemas.ReturnResponse)
async def return_car(order_id: int, current_user: models.User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """还车接口"""
    # 检查订单是否属于当前用户
    order = await crud.get_order(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 管理员可以归还任何订单，普通用户只能归还自己的订单
    if current_user.role != 2 and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限归还他人订单")
    
    if order.end_at:
        raise HTTPException(status_code=400, detail="订单已经完成")
    
    # 处理还车
    order = await crud.return_car(session, order_id)
    
    return {
        "order_id": order.id,
        "end_at": order.end_at,
        "fee": order.fee
    }

@router.get("/orders", response_model=List[schemas.RentOrder])
async def read_orders(current_user: models.User = Depends(get_current_user), skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    """获取订单列表"""
    # 管理员可以查看所有订单，普通用户只能查看自己的订单
    if current_user.role == 2:
        orders = await crud.get_orders(session, skip=skip, limit=limit)
    else:
        orders = await crud.get_orders_by_user(session, user_id=current_user.id)
    return orders

@router.get("/orders/{order_id}", response_model=schemas.RentOrder)
async def read_order(order_id: int, current_user: models.User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """获取单个订单详情"""
    order = await crud.get_order(session, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 管理员可以查看所有订单详情，普通用户只能查看自己的订单详情
    if current_user.role != 2 and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限查看他人订单")
    
    return order