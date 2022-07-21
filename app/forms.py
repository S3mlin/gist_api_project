from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    username = StringField('Username')
    pattern = StringField('Pattern')
    submit = SubmitField('Search')
#validators=[DataRequired()]