from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
import time, subprocess, threading


def cache_clear(f_stop):
    print('clearing cache...')
    rc = subprocess.call('/home/sema/gistapi/clear_db.sh')
    if not f_stop.is_set():
        threading.Timer(60, cache_clear, [f_stop]).start()

event_handler = threading.Event()
cache_clear(event_handler)


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models