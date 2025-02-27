# 使用 Python 官方轻量版基础镜像（可根据需要选择版本）
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件到容器中
COPY requirements.txt .

# 升级 pip 并安装依赖
RUN pip install --upgrade pip && pip install -r requirements.txt

# 将项目代码复制到工作目录
COPY . .

# 如果应用需要监听端口（例如使用 Flask/FastAPI），可以开放端口
# EXPOSE 8000

# 设置容器启动后运行的命令（这里假设 main.py 是入口）
CMD ["python", "main.py"]
