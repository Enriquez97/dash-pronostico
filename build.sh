#!/usr/bin/env bash
# exit on error
set -o errexit
pip install --upgrade pip
#poetry install
#pip install -r requirements.txt
python -m pip install --upgrade pip
python manage.py collectstatic --no-input
python manage.py migrate
