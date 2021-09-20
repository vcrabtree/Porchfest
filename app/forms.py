from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, DateField, \
    SelectField, SelectMultipleField, TimeField, RadioField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import URLField, DateField
from wtforms.validators import DataRequired, url, ValidationError, Email, EqualTo, InputRequired, Length
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class CreateArtistForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    genre = StringField('Genre', validators=[DataRequired()])
    hometown = StringField('Hometown', validators=[DataRequired()])
    about = TextAreaField('Description', validators=[DataRequired()])
    twitter_url = StringField('Twitter')
    instagram_url = StringField('Instagram')
    spotify_url = StringField('Spotify')

    photo = FileField(validators=[FileAllowed(['jpg', 'png'], 'Images only!')])

    submit = SubmitField('Create Artist')

    def validate_twitter_url(self, twitter_url):
        if len(twitter_url.data) > 0 and ("https://twitter.com" not in twitter_url()):
            raise ValidationError('Not a valid Twitter URL. Must start with "https://twitter.com".')

    def validate_instagram_url(self, instagram_url):
        if len(instagram_url.data) > 0 and ("https://instagram.com" not in instagram_url()):
            raise ValidationError('Not a valid Instagram URL. Must start with "https://instagram.com".')

    def validate_spotify_url(self, spotify_url):
       if len(spotify_url.data) > 0 and ("https://open.spotify.com" not in spotify_url()):
           raise ValidationError('Not a valid Spotify URL. Must start with "https://open.spotify.com".')


class CreatePorchForm(FlaskForm):
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Create Venue')


class CreateEventForm(FlaskForm):
    time = RadioField('Performance Time', choices=[('11:00-12:00', '11:00AM-12:00PM'),
                                                   ('12:00-1:00', '12:00PM-1:00PM'),
                                                   ('1:00-2:00', '1:00PM-2:00PM'),
                                                   ('2:00-3:00', '2:00PM-3:00PM'),
                                                   ('3:00-4:00', '3:00PM-4:00PM'),
                                                   ('4:00-5:00', '4:00PM-5:00PM')])
    porch = SelectField('Location', coerce=int)
    artist = SelectField('Artist', coerce=int)
    submit = SubmitField('Create New Event')
