# Conversational_Agents

## Microservices

### 1. Conversation

Run:
```
cd conversation
docker build -t conversation .
```


### 2. Deepface



3. Database -- Weaviate

We could choose Weaviate or Mongo DB as our database

- Open Docker and run this command in terminal:
```
docker pull semitechnologies/weaviate:latest
```

run:
```
docker run -d \
  -p 8080:8080 \
  --name weaviate \
  semitechnologies/weaviate:latest

```


### 4. Database -- MongoDB

We could choose Weaviate or Mongo DB as our database

**Login the database**
```bash
docker exec -it mongo mongosh -u admin -p password --authenticationDatabase admin
```

**View information in the database**
```bash
use conversations

db.users.find().pretty()
```


### Docker usage tips

Using Docker to enter a container
```bash
docker exec -it <container_id_or_name> /bin/bash
```


5. Frontend



6. Backend