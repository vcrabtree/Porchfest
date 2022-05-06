import re
from flask import jsonify
from flask import redirect, url_for, request
from flask_jwt_extended import jwt_required, create_refresh_token, get_jwt_identity, create_access_token
from flask_login import logout_user
from app import app
from app.models import *


@app.route("/login", methods=["POST"])
def login():
    auth = request.json
    if not auth or not auth.get('email') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return jsonify(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )
    user = User.query \
        .filter_by(email=auth.get('email')) \
        .first()
    if not user:
        # returns 401 if user does not exist
        return jsonify(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )

    if check_password_hash(user.password_hash, auth.get('password')):
        return generateToken(user.id), 201
    else:
        return jsonify('Password or email incorrect'), 202


@app.route('/signup', methods=['POST'])
def signup():
    # creates a dictionary of the form data
    info = request.json
    # regexEmail and regPassword to check if the email and password are in the correct format
    regexEmail = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # gets name, email and password
    email = info.get('email')
    password = info.get('password')
    if not re.fullmatch(regexEmail, email) and len(password) < 5:
        return jsonify('Email or password is not in a valid format', 202)

    # checking for existing user
    user = User.query \
        .filter_by(email=email) \
        .first()
    if not user:
        username = str(email).split('@')
        user = User(
            username=username[0],
            email=email,
            password_hash=generate_password_hash(password),
            geoTrackUser=info.get('geo_Tracking'),
            blurSetting='true'

        )
        db.session.add(user)
        db.session.commit()

        return generateToken(user.id), 201
    else:
        # returns 202 if user already exists
        return jsonify('User already exists. Please Log in.', 202)


def generateToken(userID):
    user = User.query.filter_by(id=userID).first()
    access_token = create_access_token(identity=user.id, fresh=True)
    refresh_token = create_refresh_token(identity=user.id)
    user.access_token = access_token
    user.refresh_token = refresh_token
    db.session.commit()
    return jsonify({'access_token': access_token, 'refresh_token': refresh_token})


# refresh tokens to access this route.
@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    user = User.query.filter_by(id=identity).first()
    user.access_token = access_token
    db.session.commit()
    return jsonify(access_token=access_token)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
