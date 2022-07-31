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


# @celery.task(bind=True)
# def button_test(self, test):
#     self.update_state(state='PENDING')
#     print(test)
#     time.sleep(5)
#     self.update_state(state='COMPLETE')
#     return test 

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
    if request.method == 'GET':
        return render_template('index.html', title='Home',form=form)
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
        button_test.delay(test)
        flash('Sending text to {0}'.format(test))
    else:
        send_async_text.apply_async(args=[test], countdown=60)
        flash('Text will be sent to {0} in one minute'.format(test))
    return render_template('index.html', title='Home',form=form)


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


# @bp.route('/longtask', methods=['POST'])
# def longtask():
#     received_data = request.values
#     variable = received_data.get('parameter')
#     print(variable)
#     task = button_test.apply_async(args=[variable])
#     return jsonify({'Location': url_for('bp.taskstatus', task_id=task.id), 'task_id': task.id}), 202

# @bp.route('/status/<task_id>')
# def taskstatus(task_id):
#     task = button_test.AsyncResult(task_id)
#     response = {
#         'state': task.state
#     }
#     return jsonify(response)
