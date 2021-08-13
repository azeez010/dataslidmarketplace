from flask_wtf import FlaskForm
from models import User
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Email
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
import re

class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    phone = StringField('phone', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField("Sign up")
    
    def validate_password(self, password):
        if len(password.data) < 7 or len(password.data) > 15:
            raise ValidationError("password must be greater 7 and less than 15")
    
    def validate_phone(self, phone):
        all_number = len(re.findall("[0-9]", phone.data))
        if len(phone.data) != all_number:
            raise ValidationError("Phone must be digits or numbers")

        if len(phone.data) != 11:
            raise ValidationError("Phone must be 11 digits")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("E-mail already exists")


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField("Log in")
    
class RequestForm(FlaskForm):
    request = TextAreaField('Make requests', validators=[DataRequired()])
    submit = SubmitField("Submit")
    
class TestimonyForm(FlaskForm):
    testimony = TextAreaField('Testimony', validators=[DataRequired()])
    submit = SubmitField("Submit")

class passwordResetForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if not user:
            raise ValidationError("E-mail doesn't exist, create an account instead")

class passwordReset(FlaskForm):
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Submit")

    def validate_password(self, password):
        if len(password.data) < 7 or len(password.data) > 15:
            raise ValidationError("password must be greater 7 and less than 15")
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("E-mail already exists")