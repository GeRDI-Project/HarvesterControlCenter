# Harvester Control Center v1.0.0
A harvester Control Center REST api written in Django

## Technologies used
* [Django](https://www.djangoproject.com/): The web framework for perfectionists with deadlines (Django builds better web apps with less code).
* [DRF](https://www.django-rest-framework.org/): A powerful and flexible toolkit for building Web APIs


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
            $ cd hcc_py
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

* #### There are two possible Authentication-Mechanisms
    1. Basic Authentication via Username and Password
    2. Token Authentication via Auth.-Token (see below)

* #### Run It in Dev mode
    Fire up the server using this one simple command:
    ```bash
        $ python manage.py runserver
    ```

    first, create a super-user
    ```bash
        $ python manage.py createsuperuser
    ```

    You can now access the api service on your browser by using
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
        $ curl -X GET --header 'Accept: application/json' --header 'X-CSRFToken: AJcweNkQirt51Z2lg0c94FujhSNYFiu5grZLR2N4D8r1X2wrUaUlK8EOieEStFR9' --header 'Authorization: Basic [USER_TOKEN]' 'http://localhost:8000/v1/harvesters/'
    ```

* #### Deploy a Docker Container for production with nginx as buildin reverse proxy
    First build docker container
    ```bash
        $ docker build -t harvest/hccenter:1.0.0 .
    ````
    Now run that container
    ```bash
        $ docker run --name=gerdi_hcc -it -p 80:80 harvest/hccenter:1.0.0
    ```
