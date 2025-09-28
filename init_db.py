import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.models import Base, Car, User
from app.crud import hash_password

# 数据库连接URL
DATABASE_URL = "sqlite+aiosqlite:///./scenic.db"

async def init_db():
    # 创建异步引擎
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    # 创建会话工厂
    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # 创建数据库表
    async with engine.begin() as conn:
        # 删除现有表（如果存在）
        await conn.run_sync(Base.metadata.drop_all)
        # 创建新表
        await conn.run_sync(Base.metadata.create_all)
    
    # 添加初始数据
    async with async_session() as session:
        # 创建2个用户：一个普通用户，一个管理员
        user1 = User(
            nickname="普通用户",
            phone="13800138001",
            password=hash_password("123456"),  # 密码：123456
            role=0,  # 0游客
            deposit=100.0
        )
        
        user2 = User(
            nickname="管理员",
            phone="13800138002",
            password=hash_password("admin123"),  # 密码：admin123
            role=2,  # 2管理员
            deposit=0.0
        )
        
        session.add_all([user1, user2])
        await session.commit()
        
        # 创建20辆观光车
        cars = []
        # 杭州景区列表
        scenic_spots = ['西湖', '良渚', '西溪', '灵隐', '宋城']
        
        for i in range(1, 21):
            # 模拟不同的电量和状态
            battery = 100 if i % 3 != 0 else 70 if i % 3 == 1 else 40
            status = 0 if i % 5 != 0 else 2  # 每5辆车中有一辆在维修
            
            # 为不同景区分配不同的编号前缀
            spot_index = (i - 1) % len(scenic_spots)
            spot_name = scenic_spots[spot_index]
            # 为不同景区分配不同的编号格式
            prefix = 1 if spot_name == '西湖' else 2 if spot_name == '良渚' else 3 if spot_name == '西溪' else 4 if spot_name == '灵隐' else 5
            car_number = f"{prefix:02d}{i % 100:02d}"
            
            car = Car(
                name=f"{spot_name}{car_number}",
                plate=f"SC{i:04d}",  # 车牌格式：SC0001, SC0002...
                status=status,
                battery=battery,
                qrcode=f"http://localhost:8000/static/rent.html?id={i}"
            )
            cars.append(car)
        
        session.add_all(cars)
        await session.commit()
    
    print("数据库初始化完成：创建了20辆观光车和2个用户")
    
    # 关闭引擎
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())