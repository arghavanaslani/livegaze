from flask import Flask, Response, stream_with_context, request, render_template

import gaze_manager
from gaze_manager.events import register_events
from waldo.socketio_events import register_waldo_events
from extensions.socket_io import socket_io
from authentication.utils import set_app_for_auth
from authentication.views import auth_blueprint
from trackers.views import trackers_blueprint
from trackers.events import register_events as register_tracker_events
from download_area.views import download_area_blueprint

from extensions import db_config

import os

import signal
from boards.views import board_blueprint
from settings.views import settings_blueprint
from waldo.views import waldo_blueprint
from main_page.views import main_page_blueprint
from flask_bootstrap import Bootstrap
from signal_handlers import signal_int_handler
from flask_wtf.csrf import CSRFProtect

def register_socketio_events(socket_io, app):
    register_events(socket_io)
    register_waldo_events(socket_io)
    register_tracker_events(socket_io)
    socket_io.init_app(app)


def init_parts(app):
    app.app_context().push()
    db_config.init_db(app)
    csrf.init_app(app)
    set_app_for_auth(app)
    bootstrap = Bootstrap(app)
    gaze_manager.gaze_manager.update_thread.app = app
    signal.signal(signal.SIGINT, signal_int_handler)


def register_blueprints(app):
    app.register_blueprint(board_blueprint, url_prefix="/boards")
    app.register_blueprint(settings_blueprint, url_prefix="/settings")
    app.register_blueprint(waldo_blueprint, url_prefix="/waldo")
    app.register_blueprint(main_page_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(trackers_blueprint, url_prefix="/trackers")
    app.register_blueprint(download_area_blueprint, url_prefix="/da")


thread = None
csrf = CSRFProtect()
app = Flask(__name__)
if os.path.exists('config.py'):
    app.config.from_pyfile("config.py")
else:
    app.config.from_pyfile("config_example.py")

init_parts(app)
register_socketio_events(socket_io, app)
register_blueprints(app)


if __name__ == '__main__':
    app.run()
