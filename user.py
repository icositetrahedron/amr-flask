from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import db

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        users = db.get_db().execute(
            'SELECT id FROM users WHERE username = ?',
            (username.data,)
        ).fetchall()
        if len(users) > 0:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        emails = db.get_db().execute(
            'SELECT id FROM users WHERE email = ?',
            (email.data,)
        ).fetchall()
        if len(emails) > 0:
            raise ValidationError('Please use a different email address.')
