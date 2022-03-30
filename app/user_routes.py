from flask import jsonify
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import app
from app.models import *


@app.route('/user_profile', methods=['GET'])
@jwt_required()
def user_profile():
    if get_jwt_identity() is not None:
        identity = get_jwt_identity()
        user = User.query.filter_by(id=identity).first()
        if user:
            return jsonify({"email": user.email, "trackLocation": user.geoTrackUser}), 200
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
        db.session.add(u2a)
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
            db.session.add(user)
            db.session.commit()
            return jsonify(user.geoTrackUser)
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
