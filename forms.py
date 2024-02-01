from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=10)])
    password = PasswordField('Password', validators=[Length(max=30)])
    password2 = PasswordField('Reenter Password', validators=[EqualTo('password')])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Register')

class GameForm(FlaskForm):
    friend_username = StringField('Username of existing player', validators=[DataRequired()])
    submit = SubmitField('New Game')

class FriendForm(FlaskForm):
    friend_username = StringField('Friend Username:', validators=[DataRequired()])
    submit = SubmitField('Send Request')