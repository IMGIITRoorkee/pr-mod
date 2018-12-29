# Using the base docker:dind image 
FROM docker:dind

# Install docker-compose
RUN apk update
RUN apk upgrade
RUN apk add python python-dev py-pip build-base
RUN pip install docker-compose

# Install git, curl (basic utilities)
RUN apk add curl git unzip wget