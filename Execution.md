# Execution of Application

## Installation Measure
- Create Database named ArtistryOnDemand
- activate virtual env
- change database server name, username, password in ArtistryOnDemand/settings.py
- Migrate models to the database using python manage.py makemigrations
- after that use pyhton manage.py migrate
- python manage.py runserver