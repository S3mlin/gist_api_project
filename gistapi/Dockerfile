FROM python:slim

RUN useradd gistapi

WORKDIR /home/gistapi

COPY requirements.txt requirements.txt
RUN python -m venv gistapivenv
RUN gistapivenv/bin/pip install -r requirements.txt
RUN gistapivenv/bin/pip install gunicorn pymysql cryptography

COPY app app
COPY migrations migrations
COPY gistapi.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP gistapi.py

RUN chown -R gistapi:gistapi ./
USER gistapi

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]