FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update --fix-missing -qy
RUN apt-get install python3 python3-pip libglib2.0-0 libjpeg-dev libpng-dev libtiff-dev libsm6 libxext6   -qy 
RUN mkdir -p /usr/src/app

COPY . /usr/src/app/


# set work directory
WORKDIR /usr/src/app

# install dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements/requirements-testing.txt

EXPOSE 8000


