import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LINKS_PER_PAGE = 5
    broker_url = 'redis://localhost:6379/0'
    result_backend = 'redis://localhost:6379/0'
    DB_EXPERATION_TIME = 120
