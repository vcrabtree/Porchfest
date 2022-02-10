from flask import jsonify, g, redirect
from app import db
from app.api import bp
from app.api.auth import basic_auth
from app.api.auth import token_auth


@bp.route('/tokens', methods=['POST', 'GET'])
@basic_auth.login_required
def get_token():
    token = g.current_user.get_token()
    db.session.commit()
    # uri = "http://localhost:5000/"
    # url = uri + "/?token=" + token
    url = "http://localhost:5000/api/test"
    print('\n Redirect URL with Token:  ' + url + '\n')
    return redirect(url)

    #return jsonify({'token': token})


@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204
