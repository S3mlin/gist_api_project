from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    pattern = StringField('Pattern', validators=[DataRequired()])
    submit = SubmitField('Search')
