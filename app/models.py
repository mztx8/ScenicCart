from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

# 创建基础模型类
Base = declarative_base()

class Car(Base):
    __tablename__ = "car"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    plate = Column(String, unique=True)
    status = Column(Integer, default=0)  # 0可租 1已租 2维修
    battery = Column(Integer, default=100)  # 电量%
    qrcode = Column(String)  # /rent/{id} 完整URL
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # 建立与订单的关系
    orders = relationship("RentOrder", back_populates="car")

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String, unique=True)
    nickname = Column(String)
    phone = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Integer, default=0)  # 0游客 1运维 2管理员
    deposit = Column(Float, default=0)
    
    # 建立与订单的关系
    orders = relationship("RentOrder", back_populates="user")

class RentOrder(Base):
    __tablename__ = "rent_order"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    car_id = Column(Integer, ForeignKey("car.id"))
    start_at = Column(DateTime, default=func.current_timestamp())
    end_at = Column(DateTime)
    fee = Column(Float)  # 分钟*单价
    
    # 建立与用户和车辆的关系
    user = relationship("User", back_populates="orders")
    car = relationship("Car", back_populates="orders")