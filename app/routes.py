import requests, re
from flask import Blueprint, render_template, flash, jsonify, request, url_for, redirect, session, current_app
from app.extensions import db, celery
from app.forms import SearchForm
from app.models import Link, User
from sqlalchemy_utils.functions import database_exists
import random
import time
import datetime


bp = Blueprint("bp", __name__)


@celery.task
def send_async_text(test):
    with current_app.app_context():
        return test

@celery.task(bind=True)
def long_task(self):
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                            random.choice(adjective),
                                            random.choice(noun))
        self.update_state(state='PROGRESS',
                        meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task Completed!',
            'result': 42}


@bp.route('/ping')
def ping():
    return 'pong'


def gists_for_user():
    form = SearchForm()
    gists_url = 'https://api.github.com/users/{}/gists'.format(
                    form.username.data)
    response = requests.get(gists_url)
    return response.json()


@bp.route('/api/v1/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    approved = []
    if form.validate_on_submit():
        form_data = [form.username.data, form.pattern.data]
        session['form_data_transfer'] = form_data
        if database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            if User.query.filter_by(username = form.username.data).count() == 1 and\
                Link.query.filter_by(pattern = form.pattern.data).count() > 0:
                return redirect(url_for('bp.results'))
        if database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
            if User.query.filter_by(username = form.username.data).count() == 1:
                user = User.query.filter_by(username = form.username.data)
                gists = gists_for_user()
                for gist in gists:
                    if 'message' in gist:
                        flash('Your usage of this site has been set on a cooldown...')
                        return render_template('index.html', title='Home', form=form)
                    x = gist['html_url']
                    contents = requests.get(gist['url']).json()
                    for content in contents['files'].items():
                        for data in content:
                            if 'content' in data:
                                if re.search(form.pattern.data, data['content'], re.IGNORECASE) and x not in approved:
                                    approved.append(x)
                                    gist_link = Link(link=x, user_id=str(user[0]), pattern=form.pattern.data)
                                    db.session.add(gist_link)
                db.session.commit()
                approved.clear()
                return redirect(url_for('bp.results'))
        user = User(username=form.username.data)
        db.session.add(user)
        db.session.commit()
        gists = gists_for_user()
        for gist in gists:
            if 'message' in gist:
                flash('Your usage of this site has been set on a cooldown...')
                return render_template('index.html', title='Home', form=form)
            x = gist['html_url']
            contents = requests.get(gist['url']).json()
            for content in contents['files'].items():
                for data in content:
                    if 'content' in data:
                        if re.search(form.pattern.data, data['content'], re.IGNORECASE) and x not in approved:
                            approved.append(x)
                            gist_link = Link(link=x, user_id=user.id, pattern=form.pattern.data)
                            db.session.add(gist_link)
        db.session.commit()
        approved.clear()
        return redirect(url_for('bp.results'))
    test = request.form['test']
    session['test'] = test
    if request.form['submit'] == 'Send':
        send_async_text.delay(test)
        flash('Sending text to {0}'.format(test))
    else:
        send_async_text.apply_async(args=[text_sample], countdown=60)
        flash('Text will be sent to {0} in one minute'.format(test))
    return render_template('index.html', title='Home',form=form, test=session.get('test'))


@bp.route('/api/v1/search/results', methods=['GET', 'POST'])
def results():
    transfered_data = session.get('form_data_transfer')
    flash(transfered_data)
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username = transfered_data[0])
    pagination = Link.query.filter_by( user_id=str(user[0]), pattern=transfered_data[1] ).paginate(
        page, app.config['LINKS_PER_PAGE'], False)
    next_url = url_for('bp.results', page=pagination.next_num) \
        if pagination.has_next else None
    prev_url = url_for('bp.results', page=pagination.prev_num) \
        if pagination.has_prev else None
    return render_template('results.html', pagination=pagination, next_url=next_url, prev_url=prev_url,
                            transfered_data=transfered_data)


@bp.route('/longtask', methods=['POST'])
def longtask():
    task = long_task.apply_async()
    return jsonify({'Location': url_for('bp.taskstatus', task_id=task.id)}), 202


@bp.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        end = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        end = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            end['result'] = task.info['result']
    else:
        end = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info)
        }
    return jsonify(end)
