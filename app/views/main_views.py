from flask import Blueprint, render_template, url_for, session, request, jsonify, redirect
from flask_user import current_user


# When using a Flask app factory we must use a blueprint to avoid needing 'app' for '@app.route'
main_blueprint = Blueprint('main', __name__, template_folder='templates')


@main_blueprint.route('/')
def home():
    return render_template('pages/home.html')


@main_blueprint.route('/user')
def user_profile():
    user = current_user
    return render_template('pages/user_profile.html', user=user)
