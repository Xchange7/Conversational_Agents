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

ENV OPENAI_API_KEY=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
ENV TOKENIZERS_PARALLELISM=false
ENV MONGO_URI=mongodb://admin:password@mongo:27017/


CMD ["python", "app.py"]
