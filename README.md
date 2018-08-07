# Harvester Control Center (HCC) v2.1.2
A Harvester Control Center GUI with REST-API written in Django

## Technologies used
* [Django](https://www.djangoproject.com/): The web framework for perfectionists with deadlines (Django builds better web apps with less code).
* [DRF](https://www.django-rest-framework.org/): A powerful and flexible toolkit for building Web APIs
* [Python3](http://www.python.org): Python is a highly flexible and versatile programming language supporting a vast of use cases like web dev, GUI dev, scientific and numeric, software dev and sys admin
* [FontAwesome](https://fontawesome.com/v4.7.0/icons/): Fontawesome Version 4.7
* [Bootstrap](https://getbootstrap.com/docs/4.1/getting-started/introduction/): Bootstrap 4

## Installation
* If you wish to run your own build, first ensure you have python globally installed in your computer. If not, you can get python [here](https://www.python.org").
* After doing this, confirm that you have installed _virtualenv_ globally as well. If not, run this:
    ```bash
        $ pip install virtualenv
    ```

* Then, Git clone this repo to your PC
    ```bash
        $ git clone https://...
    ```

* #### Dependencies
    1. Cd into the cloned repo as such:
        ```bash
            $ cd {{your_repo_path}}
        ```
    2. Create and fire up your virtual environment:
        ```bash
            $ virtualenv venv -p python3
            $ source venv/bin/activate
        ```
    3. Install the dependencies needed to run the app:
        ```bash
            $ pip install -r requirements.txt
        ```
    4. (optional) Make those migrations work
        ```bash
            $ python manage.py makemigrations
            $ python manage.py migrate
        ```

* ### Authentication-Mechanisms
   1. Basic Authentication via Username and Password
   2. Token Authentication via Auth.-Token (see below)

### Test the code
   To use Django Testing Environment fire the following command in your Terminal
   ```bash
       $ python manage.py test
   ```

### Running in dev mode
   first, create a super-user
   ```bash
      $ python manage.py createsuperuser
   ```
   Fire up the server using this one simple command:
   ```bash
       $ python manage.py runserver
   ```

   You can now access the service on your browser by using the following URLS. /docs for swagger api documentation. 
   /v1 is the HCC API endpoint. /admin is the admin-webinterface provided by django.
   ```
       http://localhost:8000/docs/
       http://localhost:8000/admin/
       http://localhost:8000/v1/
   ```
    
   A GUI is accessible on your browser by using
   ```
       http://localhost:8000/hcc/
   ```

   Get your _USER_TOKEN_ via POST-request to Resource /v1/get-token/
   ```bash
        $ curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d '{ \
            "username": "username", \
            "password": "password" \
          }' 'http://localhost:8000/v1/get-token/'
   ```

   For instance getting all harvesters (_/v1/harvesters/_) via Token-Authentication:
   ```bash
        $ curl -X GET --header 'Accept: application/json' --header 'X-CSRFToken: AJcweNkQirt51Z2lg0c94FujhSNYFiu5grZLR2N4D8r1X2wrUaUlK8EOieEStFR9' --header 'Authorization: Token [USER_TOKEN]' 'http://localhost:8000/v1/harvesters/'
   ```

## Deployment
A Docker Container for production with nginx as buildin reverse proxy.

First build the docker container...
   ```bash
       $ docker build -t harvest/hccenter:latest .
   ````
### Environment variable configuration
There are six ENV variables which could be used to configure for production use. 
Feel free to set them as needed when starting the docker container.

    name: "DEBUG" value: "False"
    name: "ALLOWED_HOSTS" value: "xxx.xxx.xxx.xxx,www.domainname.org"
    name: "USE_X_FORWARDED_HOST" value: "True"
    name: "SECURE_PROXY_SSL_HEADER" value: "HTTP_X_FORWARDED_PROTO,https"
    name: "FORCE_SCRIPT_NAME" value: "/path/to/desired/endpoint"
    name: "SECRET_KEY" value: "a 50bit string"
   
   Now run that container.
   ```bash
       $ docker run --name=gerdi_hcc -it -p 80:8080 harvest/hccenter:latest
   ```
