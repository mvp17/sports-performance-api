# sports-performance-api
#### Projecte Treball Final de Grau
#### Sports Performance Software Management

# Heroku
#### Procfile
#### heroku create
#### git push heroku master
#### heroku run bash
#### python manage.py migrate // migrations pushed to remote repo

# DB Migrations
#### python manage.py makemigrations
#### python manage.py migrate
#### // push migrations files to repo
#### // never migrations folder empty (__init__.py)

# Docker
## DockerFile
#### docker build . // test it builds correctly

## docker-compose
#### docker-compose build
#### docker-compose up
#### docker-compose run web python manage.py migrate
#### docker-compose run web python manage.py createsuperuser
