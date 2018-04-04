from flask_script import Server, Manager
from app import create_app
from app.commands import InitDbCommand


# Setup Flask-Script with command line commands
manager = Manager(create_app)
manager.add_command("runserver", Server(host='0.0.0.0', port=5000))
manager.add_command('init_db', InitDbCommand)

if __name__ == "__main__":
    import os
    os.environ['DEBUG'] = 'true'
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
    manager.run()
