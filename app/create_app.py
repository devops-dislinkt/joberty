from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_cors import CORS

db = SQLAlchemy()


def create_app():
    import config
    import routes

    flask_app = Flask(__name__)
    CORS(flask_app)
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_CONNECTION_URI
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    flask_app.config["SECRET_KEY"] = config.secret_key
    CORS(flask_app)

    with flask_app.app_context():
        db.init_app(flask_app)
        db.create_all()
        flask_app.register_blueprint(routes.api, url_prefix="/api")

    return flask_app
