import random

from flask_wtf.file import FileField
from slugify import slugify

from app import db, login
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class PorchfestTable(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), index=True)
    state = db.Column(db.String(128))
    time = db.Column(db.DateTime)


class UserToArtist(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), index=True)
    favorite = db.Column(db.Boolean, default=True)

    user = db.relationship("User", backref="artists")
    artist = db.relationship("Artist", backref="users")


class ArtistToGenre(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), index=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), index=True)

    artist = db.relationship("Artist", backref="genres")
    genre = db.relationship("Genre", backref="artists")

    def to_dict(self):
        data = {
            'id': self.id,
            'artist_id': self.artist_id,
            'genre_id': self.genre_id,
        }
        return data


class Artist(db.Model):
    name = db.Column(db.String(128), index=True, unique=True)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hometown = db.Column(db.String(64), index=True)
    about = db.Column(db.String(255))
    photo = db.Column(db.String(255))
    website = db.Column(db.String(128))
    spotify = db.Column(db.String(128))
    youtube = db.Column(db.String(128))
    facebook = db.Column(db.String(128))
    instagram = db.Column(db.String(128))
    more = db.Column(db.String(128))
    url_slug = db.Column(db.String(128), index=True, unique=True)

    # content = db.Column(db.String(128), unique=True)

    def to_dict(self):
        data = {
            'name': self.name,
            'id': self.id,
            'hometown': self.hometown,
            'about': self.about,
            'photo': self.photo,
            'website': self.website,
            'spotify': self.spotify,
            'youtube': self.youtube,
            'facebook': self.facebook,
            'instagram': self.instagram,
            'url_slug': self.url_slug
        }
        artist_events = []
        events = Porch.query.join(ArtistToPorch) \
            .filter(ArtistToPorch.artist_id == self.id)
        for event in events:
            artist_events.append(event.to_dict())
        data['events'] = artist_events

        # genres = ["Rock", "Musical theatre", "Soul music", "Pop music", "Folk music", "Blues", "Electronic "
        #                 "dance music","Jazz", "Country music", "Punk rock"]
        # num = random.randint(1,6)
        # data['genre'] = random.sample(genres, num)
        artist_genres = []
        genres = Genre.query.join(ArtistToGenre) \
            .filter(ArtistToGenre.artist_id == self.id)
        for genre in genres:
            artist_genres.append(genre.name)
        data['genre'] = artist_genres

        return data

    def __init__(self, **kwargs):
        super(Artist, self).__init__(**kwargs)
        self.slug_artist()

    def slug_artist(self):
        '''
        Takes an artist, generates a url_slug and commits to db
        :param artist: an Artist object from the Artist table
        :return: None (but commits to Artist.url_slug)
        '''
        slug_base = slugify(self.name)

        # ensure the slug is unique
        slug = slug_base[:120]
        index = 2
        while Artist.query.filter(Artist.url_slug == slug).count() != 0:
            slug = slug_base + "-" + str(index)
            index = index + 1

        # commit unique slug to db
        self.url_slug = slug
        db.session.add(self)
        db.session.commit()


class Porch(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.String(64), index=True)

    # events = db.relationship('Event', backref='porch', lazy='dynamic')

    def to_dict(self, simplified=True):
        data = {
            'id': self.id,
            'address': self.address,  # TODO add added column to database
        }
        return data


class ArtistToPorch(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    porch_id = db.Column(db.Integer, db.ForeignKey('porch.id'))
    time = db.Column(db.DateTime)

    def to_dict(self):
        data = {
            'id': self.id,
            'time': self.time
        }

        artist = Artist.query.filter(Artist.id == self.artist_id).first()
        data['artist'] = artist.to_dict()
        porch = Porch.query.filter(Porch.id == self.porch_id).first()
        data['porch'] = porch.to_dict()

        return data


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), index=True, unique=True)
    url_slug = db.Column(db.String(128), index=True, unique=True)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name
        }
        return data

    def __init__(self, **kwargs):
        super(Genre, self).__init__(**kwargs)
        self.slug_genre()

    def slug_genre(self):
        '''
        Takes a genre, generates a url_slug and commits to db
        :param genre: a genre object from the Genre table
        :return: None (but commits to Genre.url_slug)
        '''
        slug_base = slugify(self.name)

        # ensure the slug is unique
        slug = slug_base[:120]
        index = 2
        while Genre.query.filter(Genre.url_slug == slug).count() != 0:
            slug = slug_base + "-" + str(index)
            index = index + 1

        # commit unique slug to db
        self.url_slug = slug
        db.session.add(self)
        db.session.commit()
