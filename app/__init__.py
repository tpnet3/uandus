from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth
from flask_wtf.csrf import CSRFProtect
from flask_user import UserManager, SQLAlchemyAdapter
from flask_login import LoginManager

from workers import UandusClient

CLIENT_ID = ""
CLIENT_SECRET = ""

db = SQLAlchemy()
csrf = CSRFProtect()
oauth = OAuth()

uandus_client = None
lm = LoginManager()


def create_app(extra_config_settings={}):
    """Create a Flask applicaction.
    """


    # Instantiate Flask
    app = Flask(__name__)

    # Load App Config settings
    app.config['JSON_AS_ASCII'] = False
    # Load common settings from 'app/settings.py' file
    app.config.from_object('app.settings')
    # Load local settings from 'app/local_settings.py'
    app.config.from_object('app.local_settings')
    # Load extra config settings from 'extra_config_settings' param
    app.config.update(extra_config_settings)

    oauth.init_app(app)
    # Setup Flask-SQLAlchemy
    db.init_app(app)

    # Setup WTForms CSRFProtect
    csrf.init_app(app)

    global CLIENT_ID
    global CLIENT_SECRET

    CLIENT_ID = app.config.setdefault('CLIENT_ID', '')
    CLIENT_SECRET = app.config.setdefault('CLIENT_SECRET', '')

    # Define bootstrap_is_hidden_field for flask-bootstrap's bootstrap_wtf.html
    from wtforms.fields import HiddenField

    def is_hidden_field_filter(field):
        return isinstance(field, HiddenField)

    app.jinja_env.globals['bootstrap_is_hidden_field'] = is_hidden_field_filter

    # Setup Flask-User to handle user account related forms
    from .models.user_models import User

    db_adapter = SQLAlchemyAdapter(db, User)  # Setup the SQLAlchemy DB Adapter
    user_manager = UserManager(db_adapter, app)  # Init Flask-User and bind to app

    app.app_context().push()

    # Applications
    global uandus_client

    uandus_client = UandusClient(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

    # Register blueprints
    from app.views.main_views import main_blueprint
    from app.views.oauth_views import oauth_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(oauth_blueprint)

    return app






