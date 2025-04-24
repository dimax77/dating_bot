# app/utils/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, FileField, DateField, SubmitField
from wtforms.validators import DataRequired, Length

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    birthdate = DateField('Birthdate', format='%Y-%m-%d', validators=[DataRequired()])
    country = StringField('Country')
    city = StringField('City')
    interests = TextAreaField('Interests')
    about = TextAreaField('About')
    photo = FileField('Upload your photo')
    submit = SubmitField('Create Profile')
