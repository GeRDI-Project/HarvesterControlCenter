# Dockerfile to create a Harevster Controlcenter Dockercontainer aka Microservice
# GeRDI ControlCenter Docker-Image for Harvesters
# Author: Jan Frömberg (jan.froember@tu-dresden.de)

FROM python:latest
ENV PYTHONUNBUFFERED 1  
RUN mkdir /code  
WORKDIR /code  
ADD requirements.txt /code/  
RUN pip install -r requirements.txt 
ADD . /code/