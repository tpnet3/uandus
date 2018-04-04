import json
from flask import Blueprint, flash, render_template, url_for, session, request, jsonify, redirect
from flask_oauthlib.client import OAuth, OAuthResponse

from flask_login import LoginManager, login_user, logout_user, current_user
from app import oauth, lm
from app.models.user_models import User
from app import db, uandus_client, CLIENT_ID, CLIENT_SECRET


# When using a Flask app factory we must use a blueprint to avoid needing 'app' for '@app.route'
oauth_blueprint = Blueprint('oauth', __name__, template_folder='templates')


remote = oauth.remote_app(
    'remote',
    consumer_key=CLIENT_ID,
    consumer_secret=CLIENT_SECRET,
    request_token_params={'scope': 'email'},
    base_url='http://www.uandus.net/api/v1.0/',
    request_token_url=None,
    # access_token_method='POST',
    access_token_url='http://www.uandus.net/api/v1.0/oauth/token',
    authorize_url='http://www.uandus.net/api/v1.0/oauth/authorize'
)


def parse_authorized_response(resp):

    global uandus_client

    if resp is None:
        flash('Authentication failed.')
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, dict):
        session['access_token'] = (resp['access_token'], '')
        session['refresh_token'] = (resp['refresh_token'], '')
        uandus_client.set_auth(access_token=session['access_token'][0],
                               refresh_token=session['refresh_token'][0])

    elif isinstance(resp, OAuthResponse):
        print(resp.status)
        if resp.status != 200:
            session['access_token'] = None
            session['refresh_token'] = None
            # session['uandus_client'] = None
            return redirect(url_for('index'))
        else:
            session['access_token'] = (resp.data['access_token'], '')
            session['refresh_token'] = (resp.data['refresh_token'], '')
            uandus_client.set_auth(access_token=session['access_token'][0],
                                   refresh_token=session['refresh_token'][0])
    else:
        raise Exception()

    user_info = uandus_client.user_me()

    user = User.query.filter(User.username == user_info['username']).first()
    if not user:
        user = User(
            username=user_info['username'],
            first_name=user_info['first_name'],
            last_name=user_info['last_name'],
            email=user_info['email']
        )
        db.session.add(user)
        db.session.commit()
    elif user:
        user.first_name = user_info['first_name']
        user.last_name = user_info['last_name']
        user.email = user_info['email']
        db.session.commit()
    login_user(user, True)
    return user


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


#############  OAUTH  #######################
@oauth_blueprint.route('/authorize')
def authorize():
    # next_url = request.args.get('next') or request.referrer or None
    return remote.authorize(
        # callback=url_for('oauth.authorized', next=next_url, _external=True)
        callback=url_for('oauth.authorized', _external=True)
        # callback='http://www.uandus.net:65371/authorized'
    )


@oauth_blueprint.route('/logout')
def logout():
    session.pop('access_token', None)
    session.pop('refresh_token', None)
    logout_user()
    return redirect(url_for('main.home'))


@oauth_blueprint.route('/authorized')
def authorized():
    try:
        resp = remote.authorized_response()
    except:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    user = parse_authorized_response(resp)
    return redirect(url_for('main.home'))

@remote.tokengetter
def get_oauth_token():
    return session.get('access_token')


@oauth_blueprint.route('/token')
def token():
    token = dict()
    token['access_token'] = session.get('access_token')[0]
    token['refresh_token'] = session.get('refresh_token')[0]
    return jsonify(token)


@oauth_blueprint.route('/refresh-token')
def refresh_token():
    data = dict()
    data['grant_type'] = 'refresh_token'
    data['refresh_token'] = session['refresh_token']
    data['client_id'] = CLIENT_ID
    data['client_secret'] = CLIENT_SECRET
    # make custom POST request to get the new token pair
    resp = remote.post(remote.access_token_url, data=data)
    user = parse_authorized_response(resp)

    return redirect(url_for('main.home'))



