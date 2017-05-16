# Synopsis
This is Backend on Python 3.4 / Django 1.9 for webpr project

# Description
The WebPR software fulfills a critical need for the high risk credit card processors of the world to 

gain visibility to the online sentiment of each of their merchants, helping them proactively manage 

their portfolio and providing them with key decision support tools. This solution solves many issues 

confronting merchants, processors and banks, including alerting the processing company to 

merchants who are intentionally taking money from their customers without providing a legitimate 

product or service in return. For a merchant or its processing company, it’s nearly impossible to 

know what people are saying about a merchant online without searching hundreds of sites on a 

daily basis to ascertain the sentiment of your mentions and responding to the negative ones to 

diffuse the situation and prevent legal action for recourse or criminal proceedings.

UI Invision:
https://projects.invisionapp.com/share/D84LWD7NQ#/screens/122616452

Google Drive:
https://drive.google.com/drive/u/1/folders/0B7T_slwBYYzEVEFvYW4wUVlFOUk

API keys for external services stored in DB

ERD diagram:
https://www.lucidchart.com/documents/edit/933bb618-cde2-44de-a75a-aa73224aaba8#?=undefined

There is also documentation inside docs folder of the repo that you can generate using mkdocs utility

# Setup 

Install docker first. Setup latest docker and run it as service on system start
Download the following docker images and start them

```
[user]$ docker images
REPOSITORY                  TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
docker.io/mdillon/postgis   latest              cd6320a6d4fd        2 weeks ago         431.7 MB
docker.io/redis             latest              2f2578ff984f        2 weeks ago         109.2 MB
docker.io/rabbitmq          3-management        acdc7859ca01        4 days ago          182.9 MB
```

so simply do
```
$ sudo docker pull docker.io/mdillon/postgis
$ sudo docker pull docker.io/redis
```

then
```
$ docker run --name postgis -p 5432:5432 -e POSTGRES_PASSWORD=manager -d mdillon/postgis
$ docker run -d --name redis -p 6379:6379 redis
$ docker run -d --hostname rmq --name rabbitmq -p 15672:15672 -p 5672:5672 -e RABBITMQ_DEFAULT_USER=root -e RABBITMQ_DEFAULT_PASS=manager rabbitmq:3-management
```

then add few aliases in your ~/.bashrc
```
alias docker='sudo docker'
alias rmq='sudo docker start rabbitmq'
alias postgis='sudo docker start postgis'
alias psql='psql -h postgres -U postgres'
alias redis='sudo docker start redis'
```

then
```
$ source ~/.bashrc
```

and then simply start your postgres + postgis (9.4/2.1), redis 3.0.2 and rabbitMQ via
```
$ postgis
$ redis
$ rmq
```

type "docker ps" and you should see 3 containers running, also
```
netstat -tulnp 
```

this should give you a list of open ports and you should see there 5432, 6379 and 15672/5672 listed there

## Modify /etc/hosts

add in your /etc/hosts lines
```
127.0.0.1 rabbitmq
127.0.0.1 postgres
127.0.0.1 redis
```

so they can point to your instances of docker services (rabbitmq, postgres, redis you installed earlier)


# Development Environment for webpr

We support two ways of developing projects - within virtualenv and docker based with the help of docker-compose

## Local Install (VirtualEnv based approach)

You need to make sure you have python3 installed. 

```
$ virtualenv-3.4 .venv/[project]
```

On Windows
```
SET DJANGO_SETTINGS_MODULE=app.config.local
```

On Linux
```
EXPORT DJANGO_SETTINGS_MODULE=config.settings.local
source .venv/project/bin/activate
```

There are few OS-level packages we need

We're using PIL so we need jpeg encoders
http://stackoverflow.com/questions/8915296/python-image-library-fails-with-message-decoder-jpeg-not-available-pil

(activate virtualenv first)

on centos/fedora:
```
virtualenv-3.4 _venv/[project]
source _venv/[project]/bin/activate
pip uninstall pillow
yum install install libpng-devel
yum install install libjpg-devel
pip install pillow --upgrade
```

on ubuntu:
```
virtualenv-3.4 _venv/[project]
source _venv/[project]/bin/activate
pip uninstall pillow
apt-get install libjpeg-dev
apt-get install libfreetype6-dev
apt-get install zlib1g-dev
apt-get install libpng12-dev
pip install pillow --upgrade
```

## DB Setup

If you're on windows and need psycopg package installed use this pre-compiled version:
http://stickpeople.com/projects/python/win-psycopg/

```
createuser -U postgres -h postgres -P -s -e  webpr_user
createdb -U [project]_user -h postgres  webpr_dev
psql -U postgres -h postgres -c "ALTER USER webpr_user WITH PASSWORD 'manager';"
psql -U postgres
postgres=# GRANT ALL PRIVILEGES ON DATABASE webpr_dev TO webpr_user;
postgres=# \CONNECT webpr_dev;
postgres=# CREATE EXTENSION postgis;
```

Don't forget to install postgis extension inside dockerized postgres otherwise you will be getting errors like this one:

```
django.core.exceptions.ImproperlyConfigured: Cannot determine PostGIS version for database "webpr_dev".
GeoDjango requires at least PostGIS version 1.5. Was the database created from a spatial database template?
```

## Launch

Once everything above is done, issue the following final commands
```
python manage.py makekigrations
python manage.py migrate
python manage.py createsuperuser    # admin / manager
```

## DB Migrations
(during deployment with Jenkins happen automatically).

On your Local env pls do:

```
python manage.py makemigrations --name changed_my_model your_app_label
python manage.py migrate
bower install --allow-root --config.interactive=false
python manage.py collectstatic --noinput
```

## Setup config/settings/local.py

If you want a different local config, that is different from development, you can create local.py using local.template file

## Docker Install 

TODO: Roman Gorbil to add documentation here

# Generating tokens for existing users

```
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

for user in User.objects.all():
    Token.objects.get_or_create(user=user)
    ```
    
# Generate documentation

Project-related documentation is located at ```docs```

To live-preview docs run:
```mkdocs serve```

It will start web-server at 127.0.0.1:8000.
You can edit documentation with no need to rebuild docs after each change - mkdocs will do it automatically. (Similar to ```python manage.py runserver```).

For building docs as html, run:
```mkdocs build```


# Tests

Describe and show how to run the tests with code examples.
activate virtualenv then:
coverage run --source='.' manage.py test myapp

Use factory_boy to simulate DB Entities
https://factoryboy.readthedocs.org/en/latest/recipes.html
https://github.com/rbarrois/factory_boy


# Debugging with Shell Scripts

Can be done like this

```
import sendgrid, django
from django.core.management import *
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from app import settings
from tasks.models import *
from users.models import *

django.setup()
#  put your code to debug here ...
```











