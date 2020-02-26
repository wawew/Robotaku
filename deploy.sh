#!/bin/bash

eval "$(ssh-agent -s)" &&
ssh-add -k ~/.ssh/id_rsa &&
cd /var/www/robotaku-backend
git checkout release
git pull

source ~/.docker-profile
echo "$DOCKERHUB_PASS" | docker login --username $DOCKERHUB_USER --password-stdin
docker stop robotaku-backend
docker container prune -f
docker rmi wiflash/robotaku-container:be-latest
docker image prune -f
sudo lsof -t -i tcp:5000 | sudo xargs kill -9
docker run -d --name robotaku-backend -p 5000:5000 wiflash/robotaku-container:be-latest
