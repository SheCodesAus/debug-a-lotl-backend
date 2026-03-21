release: python debugabackend/manage.py migrate
web: gunicorn --pythonpath debugabackend debugabackend.wsgi --log-file -