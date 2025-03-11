# 1. 使用 Python 3.10 作为基础镜像
FROM python:3.10-slim

RUN apt-get update && apt-get install -y build-essential

# 2. 设置工作目录
WORKDIR /app

# 3. 安装系统依赖（libgl1-mesa-glx 是 OpenCV 需要的）
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# RUN apt-get update && apt-get install -y \
#    libgl1-mesa-glx \
#    && rm -rf /var/lib/apt/lists/*
#RUN apt-get update && apt-get install -y libglib2.0-0

# 4. 复制依赖文件（如果 requirements.txt 存在）
COPY requirements.txt .

# 5. 安装 Python 依赖（推荐使用 --no-cache-dir 以减少镜像大小）
RUN pip install --no-cache-dir -r requirements.txt

# 6. 复制 Flask 应用代码
COPY . .

# 7. 暴露 Flask 运行端口
EXPOSE 5005

# 8. 运行 Flask 应用（直接用 gunicorn 以提高性能）
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5005", "app:app"]
