# WebPR backend

This is Backend on Python 3.4/Django 1.9/Postgres/Redis for webpr project.


## Description

The WebPR software fulfills a critical need for the high risk credit card processors of the world to gain visibility to the online sentiment of each of their merchants, helping them proactively manage their portfolio and providing them with key decision support tools. This solution solves many issues confronting merchants, processors and banks, including alerting the processing company to merchants who are intentionally taking money from their customers without providing a legitimate product or service in return. For a merchant or its processing company, it’s nearly impossible to know what people are saying about a merchant online without searching hundreds of sites on a daily basis to ascertain the sentiment of your mentions and responding to the negative ones to diffuse the situation and prevent legal action for recourse or criminal proceedings.


## Config

Change DATABASES settings in config file (default is ``config/settings.local.py``). Make sure the circuit and Postgres database is created. Also make sure that Redis is installed too.

Run ``manage.py migrate`` for applying migrations to database (it just create
tables and fill in initial data).

Run ``manage.py createsuperuser`` for creating first user (superuser) with full
access to admin UI (/admin/).

Default file storage is file system, change the setting if you need AWS hosting for mediafiles (uploaded users avatars and etc.)

## Running locally

Run ``manage.py runserver`` for running local development server.
