import os

from flask import render_template, flash, redirect, url_for, request
from werkzeug.utils import secure_filename

from app import app, db
from app.models import *
from app.forms import *
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from flask_googlemaps import *


@app.route('/')
@app.route('/index')
def index():
    artists_list = Artist.query.all()
    return \
        render_template('index.html', title='Home', artists=artists_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/artist/<name>')
def artist(name):
    info = Artist.query.filter_by(name=name).first()
    return render_template('artist.html', title="Artist Information", info=info)


@app.route('/artists')
def artists():
    artists_list = Artist.query.all()
    return render_template('Artists.html', title='FavArtists', artists=artists_list)


@app.route('/schedule')
def schedule():
    events_list = Event.query.all()
    return render_template('schedule.html', title='Schedule', events=events_list)


@app.route('/map')
def map():
        return render_template('map.html', title='Map')


@app.route('/plan')
def plan():
    return render_template('plan.html', title='Plan')


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/newArtist', methods=['GET', 'POST'])
def newArtist():

    form = CreateArtistForm()

    if form.validate_on_submit():
        a = Artist.query.filter_by(name=form.name.data).first()
        if a is not None:
            flash('Artist already exist')
        else:
            b = Artist(name=form.name.data, genre=form.genre.data, hometown=form.hometown.data, about=form.about.data,
                       twitter=form.twitter_url.data, instagram=form.instagram_url.data, spotify=form.spotify_url.data)

            flash('New Artist Created!')
            db.session.add(b)
            db.session.commit()

            f = form.photo.data
            if f:
                extension = f.filename.split(".")[-1]
                filename = str(b.id) + '.' + extension
                f.save(os.path.join(
                    app.static_folder, filename
                ))
            else:
                filename = "img_avatar1.png"

            c = Artist.query.filter_by(name=form.name.data).first()
            c.photo = filename
            db.session.commit()

            return redirect(url_for('artists'))
    return render_template('newArtist.html', title="Create Artists", form=form)


@app.route('/newPorch', methods=['GET', 'POST'])
def newPorch():

    form = CreatePorchForm()
    if form.validate_on_submit():
        v= Porch.query.filter_by(address=form.address.data).first()
        if v is not None:
            flash('Porch already exists')
        else:
            w = Porch(address=form.address.data)
            flash('New Porch Created!')
            db.session.add(w)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('newPorch.html', title="Create Porches", form=form)


@app.route('/newEvent', methods=['GET', 'POST'])
def newEvent():
    porch_list = Porch.query.all()
    locations = [(i.id, i.address) for i in porch_list]
    artists_list = Artist.query.all()
    performers = [(y.id, y.name) for y in artists_list]
    form = CreateEventForm()
    form.porch.choices = locations
    form.artist.choices = performers
    if form.validate_on_submit():
        duplicate = False
        a = Artist.query.filter_by(id=form.artist.data).first()
        p = Porch.query.filter_by(id=form.porch.data).first()
        for j in performers:
            if Event.query.filter_by(artist_id=j[0], porch_id=p.id, time=form.time.data).first():
                flash('An artist is already playing this porch at this time')
                duplicate = True

        for k in locations:
            if Event.query.filter_by(artist_id=a.id, porch_id=k[0], time=form.time.data).first():
                flash('This artist is already playing at this time')
                duplicate = True

        if not duplicate:
            x = Event(time=form.time.data, porch_id=form.porch.data, artist_id=form.artist.data)
            flash('New Event Created!')
            db.session.add(x)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('newEvent.html', title='newEvent', form=form)


app.route('/populate_db')
def populate_db():
    a1 = Artist(name='The Ithacans', genre="Indie", hometown="Ithaca, NY", twitter="https://twitter.com/ithacans",
                instagram="https://instagram.com/ithacans", spotify="https://open.spotify.com/ithacans",
                photo='img_avatar1.png')
    a2 = Artist(name='The Binghamtons', genre="Dad Rock", hometown='Binghamton',
                twitter="https://twitter.com/binghamptons", instagram="https://instagram.com/binghamptons",
                photo='img_avatar1.png')
    a3 = Artist(name="Stone Cold Miracle", genre="R&B", hometown="Ithaca, NY",
                spotify="https://open.spotify.com/cold_miracle", photo='img_avatar1.png')
    p1 = Porch(address="33 Fall Creek Street")
    p2 = Porch(address="25 Utica Street")
    p3 = Porch(address="47 Buffalo Street")
    db.session.add_all([a1, a2, a3, p1, p2, p3])
    e1 = Event(artist_id=1, porch_id=1, time="12:00-1:00")
    e2 = Event(artist_id=2, porch_id=2, time="1:00-2:00")
    e3 = Event(artist_id=3, porch_id=3, time="2:00-3:00")
    db.session.add_all([e1, e2, e3])
    db.session.commit()
    return "Database has been populated"

@app.route('/reset_db')
def reset_db():
   flash("Resetting database: deleting old data and repopulating with dummy data")
   # clear all data from all tables
   meta = db.metadata
   for table in reversed(meta.sorted_tables):
       print('Clear table {}'.format(table))
       db.session.execute(table.delete())
   db.session.commit()
   populate_db()
   return redirect(url_for('index'))