# Dockerfile to create a Harvester Controlcenter Microservice
# GeRDI ControlCenter for Harvesters
# Author: Jan Frömberg (jan.froemberg@tu-dresden.de)

# FROM directive instructing base image to build upon
FROM python:alpine
LABEL author="Jan Frömberg <jan.froemberg@tu-dresden.de>"
LABEL project="GeRDI Project"
LABEL version="4.0.0"

WORKDIR /usr/src/app

RUN mkdir /usr/src/app/log && touch /usr/src/app/log/debug.log && touch /usr/src/app/log/info.log

COPY requirements.txt ./

RUN pip install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

COPY . .

# COPY startup script into container
COPY docker-entrypoint.sh /docker-entrypoint.sh

# Install Nginx (later this maybe will be outsourced to another docker container)
RUN apk update && apk upgrade
RUN apk add -f --progress --no-cache nginx
# Remove the default Nginx configuration file
RUN rm -v /etc/nginx/nginx.conf
# Copy a configuration file from the current directory
ADD nginx/nginx.conf /etc/nginx/
# Append "daemon off;" to the beginning of the configuration
# RUN echo "daemon on;" >> /etc/nginx/nginx.conf

# Expose ports
EXPOSE 80

# test nginx config and collect static files for production
RUN nginx -t && python3 manage.py collectstatic --no-input
#RUN python3 manage.py collectstatic --no-input

#CMD nginx

# specifcies the command to execute to start the server running.
ENTRYPOINT ["/docker-entrypoint.sh"]
