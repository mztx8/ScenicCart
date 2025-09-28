from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from .db import engine
from .models import Base
from .api import cars, orders, ws, users

# 创建应用启动时的生命周期上下文管理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 启动WebSocket状态更新任务
    await ws.start_status_update_task()
    
    # 应用运行中
    yield
    
    # 应用关闭时清理
    await engine.dispose()

# 创建FastAPI应用实例
app = FastAPI(
    title="景区共享观光车实时租还管理系统",
    description="基于Python+FastAPI的景区共享观光车实时租还管理系统",
    version="1.0.0",
    lifespan=lifespan
)

# WebSocket路由
@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    """WebSocket连接，用于实时获取车辆状态"""
    # 连接客户端并获取连接ID
    connection_id = await ws.manager.connect(websocket)
    try:
        # 保持连接，处理可能的客户端消息
        while True:
            # 接收客户端消息（可选，这里不做处理）
            data = await websocket.receive_text()
            print(f"接收到消息: {data}")
    except WebSocketDisconnect:
        # 客户端断开连接时处理
        ws.manager.disconnect(connection_id)
        print(f"客户端断开连接: {connection_id}")

# 注册API路由
app.include_router(cars.router)
app.include_router(orders.router)
app.include_router(users.router)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 根路由，重定向到静态文件首页
@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")