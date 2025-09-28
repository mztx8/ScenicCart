#!/bin/bash

# 启动Nginx
service nginx start

# 初始化数据库（如果需要）
python init_db.py

# 启动FastAPI应用
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4