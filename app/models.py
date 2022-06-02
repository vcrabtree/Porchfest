from slugify import slugify

from app import db, login, jwt
from flask_login import UserMixin
from datetime import datetime, time
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    access_token = db.Column(db.String(512), index=True, unique=True)
    refresh_token = db.Column(db.String(512), index=True, unique=True)
    geoTrackUser = db.Column(db.Boolean, default=False)
    blurSetting = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'geoTrackingUser': self.geoTrackUser,
            'blurSetting': self.blurSetting,
        }

        if include_email:
            data['email'] = self.email
        return data

    def get_reset_token(self):
        print()
        return jwt.encode({'reset_password': self.username, 'exp': datetime.utcnow() + timedelta(seconds=500)},
                          "secret", algorithm="HS256")


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
    photo = db.Column(db.String(1022))
    website = db.Column(db.String(128))
    spotify = db.Column(db.String(128))
    facebook = db.Column(db.String(128))
    url_slug = db.Column(db.String(128), index=True, unique=True)

    def to_dict(self):
        data = {
            'name': self.name,
            'id': self.id,
            'hometown': self.hometown,
            'about': self.about,
            'photo': self.photo,
            'website': self.website,
            'spotify': self.spotify,
            'facebook': self.facebook,
            'url_slug': self.url_slug
        }
        artist_events = []
        events = Porch.query.join(ArtistToPorch) \
            .filter(ArtistToPorch.artist_id == self.id)
        for event in events:
            artist_events.append(event.to_dict())
        data['events'] = artist_events
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
        """
        Takes an artist, generates a url_slug and commits to db
        :param artist: an Artist object from the Artist table
        :return: None (but commits to Artist.url_slug)
        """
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
    longitude = db.Column(db.Float, index=True)
    latitude = db.Column(db.Float, index=True)
    time = db.Column(db.DateTime)

    def to_dict(self):
        data = {
            'id': self.id,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'time': self.time
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
            'name': self.name,
            'slug': self.url_slug
        }
        return data

    def __init__(self, **kwargs):
        super(Genre, self).__init__(**kwargs)
        self.slug_genre()

    def slug_genre(self):
        """
        Takes a genre, generates a url_slug and commits to db
        :param genre: a genre object from the Genre table
        :return: None (but commits to Genre.url_slug)
        """
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
