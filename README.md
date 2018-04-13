# Harvester Control Center
A harvester Control Center REST api written in Django

## Technologies used
* [Django](https://www.djangoproject.com/): The web framework for perfectionists with deadlines (Django builds better web apps with less code).
* [DRF](https://www.django-rest-framework.org/): A powerful and flexible toolkit for building Web APIs


## Installation
* If you wish to run your own build, first ensure you have python globally installed in your computer. If not, you can get python [here](https://www.python.org").
* After doing this, confirm that you have installed virtualenv globally as well. If not, run this:
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
    4. Make those migrations work
        ```bash
            $ python manage.py makemigrations
            $ python manage.py migrate
        ```

* #### Run It in Dev mode
    Fire up the server using this one simple command:
    ```bash
        $ python manage.py runserver
    ```
    You can now access the api service on your browser by using
    ```
        http://localhost:8000/docs/
        http://localhost:8000/admin/
        http://localhost:8000/v1/
    ```

* #### Deploy a Docker Container for production with nginx as reverse proxy buildin
    First build docker container
    ```bash
        $ docker build -t harvest/hccenter:1.0.0 .
    ````
    Now run that container
    ```bash
        $ docker run --name=gerdi_hcc -it -p 80:80 harvest/hccenter:1.0.0
    ```
