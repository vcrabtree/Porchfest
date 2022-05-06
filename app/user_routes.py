from flask import jsonify, render_template, redirect, current_app
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from threading import Thread
from app import app, mail
from app.models import *
import jwt
from flask_mail import Message
from app.models import User


@app.route('/user_profile', methods=['GET'])
@jwt_required()
def user_profile():
    if get_jwt_identity() is not None:
        identity = get_jwt_identity()
        user = User.query.filter_by(id=identity).first()
        if user:
            return jsonify({"email": user.email, "trackLocation": user.geoTrackUser, "blurSetting": user.blurSetting}), 200
    return jsonify(None)


@app.route('/get_user_saved_artists', methods=['GET'])
@jwt_required()
def get_saved_artists():
    u2artists = UserToArtist.query.filter_by(user_id=get_jwt_identity(), favorite=True).all()
    fav_artists = []
    if u2artists is not None:
        for artist in u2artists:
            fav_artists.append(Artist.query.filter_by(id=artist.artist_id).first().to_dict())
        return jsonify(fav_artists)
    else:
        return None


@app.route('/update_user_to_artist', methods=['GET', 'POST'])
@jwt_required()
def update_user_to_artist():
    info = request.json
    artist_id = info.get('artist_id')
    if get_jwt_identity() is not None:
        u2a = UserToArtist.query.filter_by(user_id=get_jwt_identity(), artist_id=artist_id).first()
        if u2a is None:
            u2a = UserToArtist(
                user_id=get_jwt_identity(),
                artist_id=artist_id,
                favorite=True
            )
            db.session.add(u2a)
            db.session.commit()
        elif not u2a.favorite:
            u2a.favorite = True
        else:
            u2a.favorite = False
        db.session.commit()
        return jsonify(u2a.favorite)
    return jsonify(None)


@app.route('/update_user_geo_tracking', methods=['GET'])
@jwt_required()
def update_user_geo_tracking():
    if get_jwt_identity() is not None:
        identity = get_jwt_identity()
        user = User.query.filter_by(id=identity).first()
        if user:
            if user.geoTrackUser:
                user.geoTrackUser = False
            else:
                user.geoTrackUser = True
            db.session.commit()
            return jsonify(user.geoTrackUser)
        return jsonify(None)


@app.route('/update_user_blur_setting', methods=['GET'])
@jwt_required()
def update_user_blur_setting():
    if get_jwt_identity() is not None:
        identity = get_jwt_identity()
        user = User.query.filter_by(id=identity).first()
        if user:
            if user.blurSetting:
                user.blurSetting = False
            else:
                user.blurSetting = True
            db.session.commit()
            return jsonify(user.blurSetting)
        return jsonify(None)


@app.route('/delete_user', methods=['POST'])
@jwt_required()
def delete_user():
    if get_jwt_identity() is not None:
        identity = get_jwt_identity()
        user_to_delete = User.query.filter_by(id=identity).first()
        if user_to_delete is not None:
            try:
                u2a = UserToArtist.query.filter_by(user_id=identity).all()
                for artist in u2a:
                    db.session.delete(artist)
                db.session.delete(user_to_delete)

                db.session.commit()
                print("user deleted")
            except:
                print("User could not be deleted")
    return jsonify(None)


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(app, msg)).start()


@app.route('/send_password_reset', methods=['GET', 'POST'])
def reset_password_email():
    info = request.json
    email = info.get('email')

    user = User.query.filter_by(email=email).first()
    if user:
        token = user.get_reset_token()
        send_email("Porchfest password reset", current_app.config['MAIL_USERNAME'], [email], None,
                   render_template('reset_email.html', route=current_app.config['EMAIL_SERVER'], user=user, token=token))
        return jsonify("Email sent"), 200
    else:
        return jsonify("Email not found"), 404


@app.route('/password_reset/<token>', methods=['POST', 'GET'])
def reset_password(token):
    error = None
    user = None
    try:
        username = jwt.decode(token, "secret", algorithms=["HS256"])['reset_password']
        if username:
            user = User.query.filter_by(username=username).first()
    except Exception as e:
        error = 'session token has expired, request to reset again'

    if request.method == 'POST':
        new_password = request.form['new_password']
        if len(new_password) >= 5 and user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            return redirect(current_app.config['ENVIRONMENT'] + "login")
        else:
            error = 'Password needs to be at least 5 characters'

    return render_template('reset_password.html', error=error)
