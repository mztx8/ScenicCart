from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 创建异步引擎
engine = create_async_engine("sqlite+aiosqlite:///./scenic.db", echo=True)

# 创建会话工厂
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 依赖项：获取数据库会话
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session