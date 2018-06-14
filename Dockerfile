# Dockerfile to create a Harvester Controlcenter Microservice
# GeRDI ControlCenter for Harvesters
# Author: Jan Frömberg (jan.froember@tu-dresden.de)

# FROM directive instructing base image to build upon
FROM python:alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# COPY startup script into container
COPY docker-entrypoint.sh /docker-entrypoint.sh

# Install Nginx (later this maybe will be outsourced to another docker container)
# Install Bash
RUN apk add -f --progress --no-cache nginx bash
# Remove the default Nginx configuration file
RUN rm -v /etc/nginx/nginx.conf
# Copy a configuration file from the current directory
ADD nginx/nginx.conf /etc/nginx/
# Append "daemon off;" to the beginning of the configuration
# RUN echo "daemon on;" >> /etc/nginx/nginx.conf


# Expose ports
#EXPOSE 8000
EXPOSE 80

# Migrate Django DB
RUN python3 manage.py migrate

# TODO: create an initial django superuser

# test nginx config and collect static files for production
RUN nginx -t && python3 manage.py collectstatic --no-input

#CMD nginx

# specifcies the command to execute to start the server running.
ENTRYPOINT ["/docker-entrypoint.sh"]
