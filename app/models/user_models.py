# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from flask_user import UserMixin
from app import db


# Define the User data model. Make sure to add the flask_user.UserMixin !!
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    # User authentication information (required for Flask-User)
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.Unicode(32), nullable=False, unique=True)
    email = db.Column(db.Unicode(255), nullable=True)
    first_name = db.Column(db.Unicode(50), nullable=True, server_default=u'')
    last_name = db.Column(db.Unicode(50), nullable=True, server_default=u'')

