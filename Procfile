release: python debugabackend/manage.py migrate
web: gunicorn --chdir debugabackend debugabackend.wsgi:application --log-file -
