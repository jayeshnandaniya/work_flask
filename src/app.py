"""
File that holds the function that creates the app object
"""

import datetime
from inspect import getsourcefile
import os
import sys

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect

current_path = os.path.abspath(getsourcefile(lambda: 0))
current_dir = os.path.dirname(current_path)
root_dir = os.path.join(current_dir, os.pardir)
sys.path.append(root_dir)


csrf = CSRFProtect()


def load_env_vars(file_path):
    """loads environment variables from a file"""
    with open(file_path) as env_file:
        for line in env_file:
            if line.startswith("#"):
                continue
            # split name / value pair
            key, value = line.strip().split("=", 1)
            os.environ[key] = value  # Load to local environ


def create_app():
    """
    Creates the app using blueprints.
    More info here.
    http://flask.pocoo.org/docs/latest/blueprints/
    """
    load_env_vars(os.path.join(root_dir, ".env"))

    from src.credentials import get_creds

    from src import database
    from src.views import view_blueprint, api_blueprint
    from src.client_views import client_blueprint

    app = Flask(__name__)

    app.register_blueprint(view_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(client_blueprint)

    app_creds = get_creds("app_secrets")

    if (
        app_creds is None
        or "SECRET_KEY" not in app_creds.keys()
        or "JWT_SECRET_KEY" not in app_creds.keys()
    ):
        app.config["SECRET_KEY"] = "verysecretkey"
        app.config["JWT_SECRET_KEY"] = "verysecretjwtkey"
    else:
        app.config["SECRET_KEY"] = app_creds["app_secret_key"]
        app.config["JWT_SECRET_KEY"] = app_creds["jwt_secret_key"]
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

    # If true this will only allow the cookies that contain your JWTs to be sent
    # over https. In production, this should always be set to True
    app.config["JWT_COOKIE_SECURE"] = False

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=3)
    app.config["SQLALCHEMY_DATABASE_URI"] = database.uri_string
    app.config["ERROR_404_HELP"] = False
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.debug = False
    database.init_db()

    JWTManager(app)
    CORS(app)

    return app


def start_app():
    """
    Starts the app, binding to all hosts.
    Not used by docker-compose
    """
    app = create_app()
    app.run()


if __name__ == "__main__":
    start_app()
