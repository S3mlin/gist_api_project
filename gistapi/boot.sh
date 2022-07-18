#!/bin/bash

source gistapivenv/bin/activate
flask db upgrade
exec gunicorn -b :5000 --access-logfile - --error-logfile - gistapi:app