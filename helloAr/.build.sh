
#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
# create superuser
python manage.py createsuperuser --no-input --username admin --email jeandedieuuwizeye6@gmail.com --password password
