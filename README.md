# Conversational Agents

A psychological doctor agent system using conversational AI.

## Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local deployment)
- OpenAI API key

## Setup Instructions

### Environment Variables Setup

1. Create a `.env` file based on the `.env.default` template
2. Update the `OPENAI_API_KEY` value in `conversation/Dockerfile` with your personal API key

## Deployment Options

### Option 1: Full Docker Deployment (Recommended)

1. Start all services with Docker Compose:

   ```bash
   docker-compose up -d
   ```

   If you want to rebuild the images:

   ```bash
   docker-compose up -d --build
   ```

2. Access the conversation service: [http://localhost:7860](http://localhost:7860)

### Option 2: Hybrid Deployment

For MongoDB in Docker and conversation service running locally:

1. Start only the MongoDB service:

   ```bash
   docker-compose up -d mongo
   ```

2. Set up the conversation service locally:

   a. Install Python dependencies:

   ```bash
   cd conversation
   pip install -r requirements.txt
   ```

   b. Install FFmpeg (required for speech processing):
      - Download from [FFmpeg's official site](https://ffmpeg.org/download.html)
      - Add FFmpeg to your system PATH

   c. Run the application:

   ```bash
   python app.py
   ```

3. Access the conversation service: [http://localhost:7860](http://localhost:7860)

## Facial Emotion Detection

First we need another virtual environment.

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# MacOS
source venv/bin/activate
```

Install necessary libs.
```bash
pip install -r requirements.txt
```

Because it is really hard for Docker Container to Use Camera, we can only start this service by 

```bash
python deepface/app.py
```

and we use docker extra_hosts to mapping localhost to docker internal hosts.

## Administration

### MongoDB Management

Connect to the MongoDB instance:

```bash
docker exec -it mongo mongosh -u admin -p password --authenticationDatabase admin
```

View data in the conversations database:

```bash
use conversations
db.users.find().pretty()
```

## Troubleshooting

### Docker Commands

Access a container shell:

```bash
docker exec -it <container_id_or_name> /bin/bash
```

View container logs:

```bash
docker logs <container_id_or_name>
```

Restart services:

```bash
docker-compose restart
```

View the logs of all services:

```bash
docker-compose logs -f
```

View the logs of a specific service:

```bash
docker-compose logs -f <service_name>
```
