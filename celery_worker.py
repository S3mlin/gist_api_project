from app.extensions import celery # noqa
from app import create_app


app = create_app('Config')
app.app_context().push()
