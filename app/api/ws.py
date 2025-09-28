from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import asyncio

from .. import crud
from ..db import get_session

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        # 为新连接分配一个临时ID
        connection_id = len(self.active_connections) + 1
        self.active_connections[connection_id] = websocket
        return connection_id
    
    def disconnect(self, connection_id: int):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
    
    async def send_personal_message(self, message: dict, connection_id: int):
        if connection_id in self.active_connections:
            await self.active_connections[connection_id].send_json(message)
    
    async def broadcast(self, message: dict):
        """广播消息给所有连接的客户端"""
        # 创建一个发送任务列表
        tasks = []
        for connection in self.active_connections.values():
            # 添加发送消息的任务
            tasks.append(connection.send_json(message))
        
        # 并发执行所有发送任务
        if tasks:
            try:
                await asyncio.gather(*tasks)
            except Exception as e:
                print(f"广播消息时出错: {e}")

# 创建连接管理器实例
manager = ConnectionManager()

# 从app.db导入sessionmaker
from app.db import async_session

# 模拟车辆状态更新任务
async def car_status_update_task():
    """定期更新车辆状态并广播给所有连接的客户端"""
    while True:
        try:
            # 获取数据库会话
            async with async_session() as session:
                # 获取所有车辆
                cars = await crud.get_all_cars(session)
                # 构建状态更新消息
                status_updates = []
                for car in cars:
                    status_updates.append({
                        "car_id": car.id,
                        "battery": car.battery,
                        "status": car.status
                    })
                # 广播状态更新
                await manager.broadcast(status_updates)
        except Exception as e:
            print(f"获取车辆状态时出错: {e}")
        
        # 每秒更新一次
        await asyncio.sleep(1)

# 启动状态更新任务
async def start_status_update_task():
    """启动车辆状态更新任务"""
    asyncio.create_task(car_status_update_task())