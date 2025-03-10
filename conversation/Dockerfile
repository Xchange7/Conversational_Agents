# Use Python official lightweight base image (version can be selected as needed)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies, including FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file to container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code to working directory
COPY . .

# If the application needs to listen to ports (e.g., using Flask/FastAPI), expose ports
# EXPOSE 8000
EXPOSE 7860

ENV OPENAI_API_KEY=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
ENV TOKENIZERS_PARALLELISM=false
ENV MONGO_URI=mongodb://admin:password@mongo:27017/

CMD ["python", "app.py"]
