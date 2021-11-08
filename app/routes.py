import os

import pandas as pd
from flask import flash, redirect, url_for, request
from flask import jsonify
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse

from app import app
from app.forms import *
from app.models import *


@app.route('/')
@app.route('/index')
def index():
    all_artists = Artist.query.order_by(Artist.name.asc()).all()
    artists_list = []
    for artist in all_artists:
        artists_list.append(artist.to_dict())
    return jsonify(artists_list)
    # return jsonify({ "name": "Post Malone", "id": 7297, "hometown": "Grapevine, TX", "about": "Malone was born on July 4, 1995 in Syracuse, New York and moved to Grapevine, Texas at the age of 10. He started playing guitar at the age of 14 because of popular video game Guitar Hero . He later auditioned for band Crowd the Empire in 2010 but was rejected after his guitar string broke during the audition.", "photo": "https://i.scdn.co/image/93fec27f9aac86526b9010e882037afbda4e3d5f", "twitter": "https://twitter.com/postmalone", "spotify": "https://open.spotify.com/artist/246dkjvS1zLTtiykXe5h60", "instagram": "https://www.instagram.com/postmalone/", "merch": "https://shop.postmalone.com" })


@app.route('/artist/<string:slug>', methods=['GET'])
def get_slug_artist(slug):
    artist_data = Artist.query.filter_by(url_slug=slug).first_or_404()
    result = {"artist": artist_data.to_dict()}
    return jsonify(result)


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
    return jsonify({"status": True})


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
    return jsonify({"status": True})


@app.route('/artists')
def artists():
    all_artists = Artist.query.order_by(Artist.name.asc()).all()
    artists_list = []
    for artist in all_artists:
        artists_list.append(artist.to_dict())
    return jsonify(artists_list)


@app.route('/genres')
def genres():
    genres_list = ["Rock", "Musical theatre", "Soul music", "Pop music", "Folk music", "Blues", "Electronic",
                   "Dance music", "Jazz", "Country music", "Punk rock"]
    return jsonify(genres_list)


@app.route('/schedule')
def schedule():
    all_events = ArtistToPorch.query.all()
    events_list = []
    for event in all_events:
        events_list.append(event.to_dict())
    return jsonify(events_list)


@app.route('/location')
def location():
    return jsonify({"map": "TODO"})


@app.route('/plan')
def plan():
    return jsonify({"plan": "TODO"})


@app.route('/about')
def about():
    return jsonify({"about": "TODO"})


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
    return jsonify({"status": True})


@app.route('/newPorch', methods=['GET', 'POST'])
def newPorch():
    form = CreatePorchForm()
    if form.validate_on_submit():
        v = Porch.query.filter_by(address=form.address.data).first()
        if v is not None:
            flash('Porch already exists')
        else:
            w = Porch(address=form.address.data)
            flash('New Porch Created!')
            db.session.add(w)
            db.session.commit()
            return redirect(url_for('index'))
    return jsonify({"status": True})


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
            if ArtistToPorch.query.filter_by(artist_id=j[0], porch_id=p.id, time=form.time.data).first():
                flash('An artist is already playing this porch at this time')
                duplicate = True

        for k in locations:
            if ArtistToPorch.query.filter_by(artist_id=a.id, porch_id=k[0], time=form.time.data).first():
                flash('This artist is already playing at this time')
                duplicate = True

        if not duplicate:
            x = ArtistToPorch(time=form.time.data, porch_id=form.porch.data, artist_id=form.artist.data)
            flash('New Event Created!')
            db.session.add(x)
            db.session.commit()
            return redirect(url_for('index'))
    return jsonify({"status": True})


@app.route('/populate_db')
def populate_db():
    flash("Populating database with Porchfest data")

    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()
    df = pd.read_csv('data/2019PerformerSchedule.csv', index_col=0, sep=',')
    # Add porches
    porches = df['Porch Address'].unique()
    for i in range(porches.shape[0]):
        porch = Porch(address=porches[i])
        db.session.add(porch)
        db.session.commit()
    # Add artists
    for i in range(df.shape[0]):
        row = df.iloc[i]
        artist = Artist(name=row['Name'], about=row['Description'])
        db.session.add(artist)
        db.session.commit()
    # Add events
    for i in range(df.shape[0]):
        row = df.iloc[i]
        artist = db.session.query(Artist).filter_by(name=row['Name']).first()
        porch = db.session.query(Porch).filter_by(address=row['Porch Address']).first()
        timing = int(row['Assigned Timeslot'].split('-')[0])
        if not timing == 12:
            timing += 12
        time = datetime(2019, 9, 22, timing)
        event = ArtistToPorch(time=time, artist_id=artist.id, porch_id=porch.id)
        db.session.add(event)
        db.session.commit()
    return jsonify({"status": True})


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
    return jsonify({"status": True})


@app.route('/artist_info_all_add')
def add_five_artist():
    #Clear the current tables of data 
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()

    flash("Adding five artists with all data to the database...")

    porches = ['105 Farm St', '106 2nd St', '130 Linn St', '202 E Falls St', '204 E Yates St']
    for i in range(5):
        porch = Porch(address=porches[i])
        db.session.add(porch)
        db.session.commit()
    artist_name = ["BTS", "Taylor Swift", "Drake", "The Weeknd", "Billie Eilish"]
    hometown = ["Seoul, South Korea", "West Reading, Pennsylvania","Toronto, Ontario, Canada", "Toronto, Ontario, Canada", "Los Angeles, California"]
    about = ["BTS, also known as the Bangtan Boys, is a South Korean boy band that was formed in 2010 and debuted in 2013 under Big Hit Entertainment.",
             "Taylor Alison Swift is an American singer-songwriter. Her narrative songwriting, which is often inspired by her personal life, has received widespread media coverage and critical praise.",
             "Aubrey Drake Graham is a Canadian rapper, singer, songwriter, and actor. ",
             "Abel Makkonen Tesfaye, known professionally as the Weeknd, is a Canadian singer, songwriter, and record producer.",
             "Billie Eilish Pirate Baird O'Connell is an American singer and songwriter."
             ]
    photo_url = ["https://upload.wikimedia.org/wikipedia/commons/4/4f/BTS_for_Dispatch_White_Day_Special%2C_27_February_2019_01.jpg",
             "https://variety.com/wp-content/uploads/2020/01/taylor-swift-variety-cover-5-16x9-1000.jpg?w=681&h=383&crop=1",
             "https://media.pitchfork.com/photos/612903e10a693361be8082cb/16:9/w_2480,h_1395,c_limit/Drake.jpg",
             "https://akns-images.eonline.com/eol_images/Entire_Site/2021330/rs_634x1024-210430163026-634-the-weeknd.jpg?fit=around%7C634:1024&output-quality=90&crop=634:1024;center,top",
             "https://media.allure.com/photos/605247e1bddfa641546fa160/1:1/w_2264,h_2264,c_limit/billie%20eilish.jpg"
            ]
    twitter_url = ["https://twitter.com/bts_bighit?lang=en",
                   "https://twitter.com/taylorswift13?lang=en",
                   "https://twitter.com/drake",
                   "https://twitter.com/theweeknd",
                   "https://twitter.com/billieeilish"
            ]
    spotify_url = ["https://open.spotify.com/artist/3Nrfpe0tUJi4K4DXYWgMUX",
               "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02",
                "https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4",
                 "https://open.spotify.com/artist/1Xyo4u8uXC1ZmMpatF05PJ",
                 "https://open.spotify.com/artist/6qqNVTkY8uBg9cP3Jd7DAH"
            ]
    instagram_url = ["https://www.instagram.com/bts.bighitofficial/?hl=en",
                     "https://www.instagram.com/taylorswift/",
                     "https://www.instagram.com/champagnepapi/",
                     "https://www.instagram.com/theweeknd/",
                     "https://www.instagram.com/billieeilish/?hl=en"
            ]
    merch_url = ["https://btsmerchshop.org/",
                 "https://www.taylorswift.com/",
                 "https://drakerelated.com/",
                 "https://www.theweeknd.com/",
                "https://store.billieeilish.com/"
            ]
    #Add artists
    for i in range(5):
        artist = Artist(name=artist_name[i],hometown=hometown[i], about=about[i],photo=photo_url[i],
                        twitter=twitter_url[i],spotify=spotify_url[i], instagram=instagram_url[i],
                        merch=merch_url[i])
        db.session.add(artist)
        db.session.commit()

    #Add events
    for i in range(5):
        artist = db.session.query(Artist).filter_by(name=artist_name[i]).first()
        porch = db.session.query(Porch).filter_by(address=porches[i]).first()
        time = datetime(2019, 9, 22, random.randint(1,12))
        event = ArtistToPorch(time=time, artist_id=artist.id, porch_id=porch.id)
        db.session.add(event)
        db.session.commit()
    #Add genres
    # for i in range(5):
    #     artist = db.session.query(Artist).filter_by(name=artist_name[i]).first()
    return jsonify({"status": True})

