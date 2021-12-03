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
    u = User(username='susan', email='susan@example.com')
    db.session.add(u)
    db.session.commit()
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


@app.route('/artists', methods=['GET', 'POST'])
def artists():
    sort_type = request.json['type']
    if sort_type == 'alphabetical':
        all_artists = Artist.query.order_by(Artist.name.asc()).all()
        artists_list = []
        for artist in all_artists:
            artists_list.append(artist.to_dict())
        return jsonify(artists_list)
    else:
        genre_artist_results = []
        all_genres = Genre.query.order_by(Genre.name.asc()).all()
        all_artists = Artist.query.order_by(Artist.name.asc()).all()
        count = 0
        for genre in all_genres:
            genre_artists = {genre.name: [], "slug": genre.url_slug}
            artist_to_genre_info = ArtistToGenre.query.filter_by(genre_id=genre.id).all()
            for artist_to_genre in artist_to_genre_info:
                for artist in all_artists:
                    if artist.id == artist_to_genre.artist_id:
                        if count < 3:
                            genre_artists[genre.name].append(artist.to_dict())
                            count += 1
            count = 0
            genre_artist_results.append(genre_artists)
        return jsonify(genre_artist_results)


@app.route('/genres')
def genres():
    all_genres = Genre.query.order_by(Genre.name.asc()).all()
    genre_list = []
    for genre in all_genres:
        genre_list.append(genre.to_dict())
    return jsonify(genre_list)


@app.route('/genre/<string:slug>', methods=['GET'])
def get_slug_genre(slug):
    genre_artist_results = []
    genre_data = Genre.query.filter_by(url_slug=slug).first_or_404()
    all_artists = Artist.query.order_by(Artist.name.asc()).all()
    genre_artists = {genre_data.name: []}
    artist_to_genre_info = ArtistToGenre.query.filter_by(genre_id=genre_data.id).all()
    for artist_to_genre in artist_to_genre_info:
        for artist in all_artists:
            if artist.id == artist_to_genre.artist_id:
                genre_artists[genre_data.name].append(artist.to_dict())
    genre_artist_results.append(genre_artists)
    return jsonify(genre_artist_results)

@app.route('/update_user_to_artist', methods=['POST'])
#Needs to be to a spec user
def update_user_to_artist():
    info = request.json
    artist_id = info.get('artist_id')
    # user_id = info.get('user_id')

    # u2a = UserToArtist.query.filter_by(user_id=user_id, artist_id=artist_id).first()
    u2a = UserToArtist.query.filter_by(user_id=2, artist_id=artist_id).first()
    if u2a is None:
        u2a = UserToArtist(
            user_id=2,
            artist_id=artist_id,
            favorite=True
        )
        db.session.add(u2a)
        db.session.commit()
    elif not u2a.favorite:
        u2a.favorite = True
        db.session.commit()
    else:
        u2a.favorite = False
    db.session.commit()
    print(artist_id)
    return jsonify({"status": True})


@app.route('/get_saved_artists', methods=['GET', 'POST'])
def get_saved_artists():
    u2artists = UserToArtist.query.filter_by(user_id=2, favorite=True).all()
    fav_artists = []
    for artist in u2artists:
        fav_artists.append(Artist.query.filter_by(id=artist.artist_id).first().to_dict())
    print(fav_artists)
    return jsonify(fav_artists)

#def get_user_favorite_artists:


@app.route('/schedule')
def schedule():
    all_events = ArtistToPorch.query.all()
    events_list = []
    for event in all_events:
        events_list.append(event.to_dict())
    return jsonify(events_list)


@app.route('/search', methods=['GET', 'POST'])
def search():
    search_input = request.json['entry']

    exact_artist = Artist.query.filter(Artist.name == search_input).limit(4).all()

    if len(exact_artist) < 4:
        more_artists = Artist.query.filter(Artist.name.like("%" + search_input + "%")).limit(
            4 - len(exact_artist)).all()
    else:
        more_artists = None

    if exact_artist:
        artist_like = exact_artist
        if more_artists:
            # checks to see if exact artist matches any similar artists
            same = 0
            for artist in more_artists:
                for a in exact_artist:
                    if artist == a:
                        same = 1
                if same == 0:
                    artist_like.append(artist)
    elif more_artists:
        artist_like = more_artists
    else:
        artist_like = []

    artist_search_results = []
    for i in range(0, len(artist_like)):
        artist_data = artist_like[i].to_dict()
        artist_search_results.append({"artist": artist_data})

    exact_genre = Genre.query.filter(Genre.name == search_input).limit(4).all()

    if len(exact_genre) < 4:
        more_genres = Genre.query.filter(Genre.name.like("%" + search_input + "%")).limit(
            4 - len(exact_genre)).all()
    else:
        more_genres = None

    if exact_genre:
        genre_like = exact_genre
        if more_genres:
            # checks to see if exact genre matches any similar genres
            same = 0
            for genre in more_genres:
                for g in exact_genre:
                    if genre == g:
                        same = 1
                if same == 0:
                    genre_like.append(genre)
    elif more_genres:
        genre_like = more_genres
    else:
        genre_like = []

    genre_search_results = []
    for i in range(0, len(genre_like)):
        genre_data = genre_like[i].to_dict()
        genre_search_results.append({"genre": genre_data})

    return jsonify({"artists": artist_search_results, "genres": genre_search_results})


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


    genres = ["Rock", "Musical theatre", "Soul music", "Pop music", "Folk music", "Blues", "Electronic "
            "dance music","Jazz", "Country music", "Punk rock"]
    for genre in genres:
        genre = Genre(name=genre)
        db.session.add(genre)
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
    website_url = ["https://btsmerchshop.org/",
                 "https://www.taylorswift.com/",
                 "https://drakerelated.com/",
                 "https://www.theweeknd.com/",
                "https://store.billieeilish.com/"
            ]
    youtube_url = ["https://www.youtube.com/channel/UCLkAepWjdylmXSltofFvsYQ",
               "https://www.youtube.com/c/TaylorSwift",
                "https://www.youtube.com/user/DrakeOfficial",
                "https://www.youtube.com/channel/UC0WP5P-ufpRfjbNrmOWwLBQ",
                "https://www.youtube.com/channel/UCiGm_E4ZwYSHV3bcW1pnSeQ"
            ]
    facebook_url = ["https://www.facebook.com/bangtan.official",
                "https://www.facebook.com/TaylorSwift",
                "https://www.facebook.com/Drake",
                "https://www.facebook.com/theweeknd",
                "https://www.facebook.com/billieeilish"
           ]
    more_url = ["https://www.tiktok.com/@bts_official_bighit?lang=en",
                "https://music.apple.com/us/artist/taylor-swift/159260351",
                "https://en.wikipedia.org/wiki/Drake_(musician)"]
    #Add artists
    for i in range(5):
        artist = Artist(name=artist_name[i],hometown=hometown[i], about=about[i],photo=photo_url[i],
                        spotify=spotify_url[i], instagram=instagram_url[i],
                        website=website_url[i], youtube=youtube_url[i], facebook=facebook_url[i])
        db.session.add(artist)
        db.session.commit()

    #Add eventToArtists
    for i in range(5):
        artist = db.session.query(Artist).filter_by(name=artist_name[i]).first()
        porch = db.session.query(Porch).filter_by(address=porches[i]).first()
        time = datetime(2019, 9, 22, random.randint(1,12))
        event = ArtistToPorch(time=time, artist_id=artist.id, porch_id=porch.id)
        db.session.add(event)
        db.session.commit()

    #Add genresToArtists
    genres_from_db = db.session.query(Genre).all()
    for i in range(5):
        num = random.randint(1, 6)
        randGenre = random.sample(genres_from_db, num)
        artist = db.session.query(Artist).filter_by(name=artist_name[i]).first()
        for i in range(num):
            genreToArtist = ArtistToGenre(artist_id=artist.id, genre_id=randGenre[i].id)
            db.session.add(genreToArtist)
            db.session.commit()
    #Add 'more' urls
    for i in range(3):
        artist = db.session.query(Artist).filter_by(name=artist_name[i]).first()
        artist.more = more_url[i]
        db.session.commit()
    return jsonify({"status": True})

