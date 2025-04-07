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

# Expose Streamlit port (8501 is the default Streamlit port)
EXPOSE 8501

ENV TOKENIZERS_PARALLELISM=false
ENV MONGO_URI=mongodb://admin:password@mongo:27017/

# Run Streamlit application instead of app.py
CMD ["streamlit", "run", "new_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
