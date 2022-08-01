from flask import Flask
from app.config import Config
from flask_migrate import Migrate
import time, subprocess, threading
import os

migrate = Migrate()

def cache_clear(f_stop):
    print('clearing cache...')
    rc = subprocess.call('/home/sema/gist_api_project/app/clear_db.sh')
    if not f_stop.is_set():
        threading.Timer(60, cache_clear, [f_stop]).start()

if os.environ.get("activate_cache", False):
    event_handler = threading.Event()
    cache_clear(event_handler)


def create_app(config_class='Config'):
    app = Flask(__name__)
    app.config.from_object(f"app.config.{config_class}")
    
    from app.extensions import db, celery
    db.init_app(app)
    migrate.init_app(app, db)

    
    from app.routes import bp

    app.register_blueprint(bp)


    celery.config_from_object(f"app.config.{config_class}")

    return app

from app import models