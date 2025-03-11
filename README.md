# Conversational Agents

This repository contains the group project for the TU Delft DSAIT4065 (previously CS4270) Conversational Agents course. The project implements a psychological doctor agent system powered by conversational AI technologies.

## Table of Contents

- [Conversational Agents](#conversational-agents)
  - [Table of Contents](#table-of-contents)
  - [1. Prerequisites](#1-prerequisites)
  - [2. Setup Instructions](#2-setup-instructions)
    - [2.1 Environment Variables Setup](#21-environment-variables-setup)
    - [2.2 Facial Emotion Detection Setup](#22-facial-emotion-detection-setup)
      - [2.2.1 Option 1: Using venv](#221-option-1-using-venv)
      - [2.2.2 Option 2: Using Conda](#222-option-2-using-conda)
    - [2.3 Docker Deployment](#23-docker-deployment)
  - [3. Administration](#3-administration)
    - [3.1 MongoDB Management](#31-mongodb-management)
  - [4. Troubleshooting](#4-troubleshooting)
    - [4.1 Docker Commands](#41-docker-commands)

## 1. Prerequisites

- **Docker and Docker Compose**
- **Python 3.10 or higher** (for local deployment)
- **OpenAI API key** (for conversation capabilities)

## 2. Setup Instructions

### 2.1 Environment Variables Setup

Create a `.env` file in the `./conversation` directory based on the provided `./conversation/.env.default` template.

### 2.2 Facial Emotion Detection Setup

> **Note:** Since camera access is challenging within Docker containers, this service runs ***locally*** with Docker mapping localhost to internal container hosts through `extra_hosts`.

To set up the facial emotion detection component, follow one of the options below:

#### 2.2.1 Option 1: Using venv

1. Create a Python virtual environment:

   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:

   - **For Windows:**

     ```bash
     venv\Scripts\activate
     ```

   - **For macOS/Linux:**

     ```bash
     source venv/bin/activate
     ```

3. Install the required dependencies:

   ```bash
   pip install -r deepface/requirements.txt
   ```

4. Run the facial emotion detection service:

   ```bash
   python deepface/app.py
   ```

#### 2.2.2 Option 2: Using Conda

1. Create a Conda environment with Python 3.10:

   ```bash
   conda create -n emotion_detection python=3.10
   conda activate emotion_detection
   ```

2. Install the required dependencies:

   ```bash
   pip install -r deepface/requirements.txt
   ```

3. Run the facial emotion detection service:

   ```bash
   python deepface/app.py
   ```

### 2.3 Docker Deployment

1. Start all services (MongoDB and conversation) using Docker Compose:

   ```bash
   docker-compose up -d
   ```

   To rebuild images when changes are made:

   ```bash
   docker-compose up -d --build
   ```

2. Once deployed, access the conversation service at: [http://localhost:7860](http://localhost:7860)

## 3. Administration

### 3.1 MongoDB Management

1. Connect to the MongoDB database:

   ```bash
   docker exec -it mongo mongosh -u admin -p password --authenticationDatabase admin
   ```

2. View conversation data:

   ```bash
   use conversations
   db.users.find().pretty()
   ```

## 4. Troubleshooting

### 4.1 Docker Commands

Common Docker commands for troubleshooting:

- Access container shell:

  ```bash
  docker exec -it <container_id_or_name> /bin/bash
  ```

- View container logs:

  ```bash
  docker logs <container_id_or_name>
  ```

- Restart services:

  ```bash
  docker-compose restart
  ```

- View logs for all services:

  ```bash
  docker-compose logs -f
  ```

- View logs for a specific service:

  ```bash
  docker-compose logs -f <service_name>
  ```