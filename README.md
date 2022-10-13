# API - Rest
___
## Configuration
Create .env file with following parameters:
```bash
# Redis infos
REDIS_HOST='10.5.0.5'
REDIS_PORT='6379'
REDIS_PASS='password123'

# MongoDB infos
MONGO_HOST='10.5.0.6'
MONGO_PORT='27017'
MONGO_USER='admin'
MONGO_PASS='password123'
MONGO_BASE='fastapi'

#JWT infos
ACCESS_TOKEN_EXPIRES_IN='15'
REFRESH_TOKEN_EXPIRES_IN='60'
JWT_ALGORITHM='RS256'

# 1 - Generate JWT Private Key: openssl genrsa -out private.pem 2048
# 2 - Convert JWT Private Key to base64: cat private.pem | base64 | tr -d \\n
# 3 - Copy the key converted and paste on JWT_PRIVATE_KEY value
JWT_PRIVATE_KEY=''

# 1 - Generate JWT Public Kkey: openssl rsa -in private.pem -pubout > public.pem
# 2 - Convert JWT Public Key to base64: cat public.pem | base64 | tr -d \\n
# 3 - Copy the key converted and paste on JWT_PUBLIC_KEY value
JWT_PUBLIC_KEY=''

# Specify system version
SYS_VERSION='0.0.1'
```
___
## Docker Network
Create the docker network with the following command:
```bash
sudo docker network create -d bridge --subnet=10.5.0.0/24 --gateway=10.5.0.1 api_network
```
___
## Docker Containers
To run all containers, run the following command:
```bash
sudo docker-compose up -d --build
```
To run only a specific container, run any of the following command:
```bash
sudo docker-compose -f docker-compose.mongo.yml up -d --build # For run only the mongodb container
sudo docker-compose -f docker-compose.redis.yml up -d --build # For run only the redis container
sudo docker-compose -f docker-compose.api.yml up -d --build # For run only the api container
```
