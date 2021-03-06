from flask_wtf.file import FileField
from app import db, login
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Artist(db.Model):
    name = db.Column(db.String(64), index=True, unique=True)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hometown = db.Column(db.String(64), index=True)
    genre = db.Column(db.String(64), index=True)
    about = db.Column(db.String(128))
    photo = db.Column(db.String(64))
    twitter = db.Column(db.String(128))
    spotify = db.Column(db.String(128))
    instagram = db.Column(db.String(128))
    merch = db.Column(db.String(128), unique=True)
    #content = db.Column(db.String(128), unique=True)
    events = db.relationship('Event', backref='artist', lazy='dynamic')


class Porch(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.String(64), index=True)
    events = db.relationship('Event', backref='porch', lazy='dynamic')

class Event(db.Model):
    id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    porch_id = db.Column(db.Integer, db.ForeignKey('porch.id'))
    time = db.Column(db.String(64))
