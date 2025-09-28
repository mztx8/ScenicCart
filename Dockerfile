# 使用官方Python镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建Nginx配置文件
RUN rm /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/conf.d/

# 确保Nginx可以访问静态文件
RUN chown -R www-data:www-data /app/static

# 暴露端口
EXPOSE 80

# 启动脚本
COPY start.sh .
RUN chmod +x start.sh

# 运行启动脚本
CMD ["/app/start.sh"]