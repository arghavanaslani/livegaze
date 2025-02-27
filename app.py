# import imp

from flask import Flask, render_template, Response, stream_with_context, request

import gaze_manager
from gaze_manager.events import register_events
from waldo.socketio_events import register_waldo_events
from extensions.socket_io import socket_io

from extensions import db_config

import os

import signal
from boards.views import board_blueprint
from settings.views import settings_blueprint
from waldo.views import waldo_blueprint
from main_page.views import main_page_blueprint
from flask_bootstrap import Bootstrap
from signal_handlers import signal_int_handler
from flask import Flask
from flask_wtf.csrf import CSRFProtect

import random

thread = None
csrf = CSRFProtect()
app = Flask(__name__)
if os.path.exists('config.py'):
    app.config.from_pyfile("config.py")
else:
    app.config.from_pyfile("config_example.py")
app.app_context().push()
db_config.init_db(app)
csrf.init_app(app)

# register socket io events
register_events(socket_io)
register_waldo_events(socket_io)
socket_io.init_app(app)
app.register_blueprint(board_blueprint, url_prefix="/boards")
app.register_blueprint(settings_blueprint, url_prefix="/settings")
app.register_blueprint(waldo_blueprint, url_prefix="/waldo")
app.register_blueprint(main_page_blueprint)
bootstrap = Bootstrap(app)
gaze_manager.gaze_manager.update_thread.app = app

signal.signal(signal.SIGINT, signal_int_handler)


# @app.route('/', methods=["GET"])
# def index():
#     return render_template('demo.html', camera_ids=2)


# forms
@app.route('/participant.html')
def participant():
    return render_template("participant.html")


@app.route('/stimulus.html')
def stimulus():
    return render_template("stimulus.html")


@app.route('/experiment.html')
def experiment():
    return render_template("experiment.html")


# effects
@app.route('/transformed1')
def transformed1():
    return render_template('transformed1.html', camera_ids=1)


@app.route('/transformed/<string:board_id>')
def transformed(board_id):
    return render_template('transformed.html', board_id=int(board_id), mode='simple')

@app.route('/transformed/<string:mode>/<string:board_id>')
def transformer_mode(mode, board_id):
    if mode not in ['simple', 'torch', 'waldo']:
        mode = 'simple'
    return render_template('transformed.html', board_id=int(board_id), mode=mode)

@app.route('/torch')
def torch():
    return render_template('torch.html', camera_ids=1)


@app.route('/torch_new/<string:board_id>')
def torch_new(board_id):
    return render_template('torch_new.html', camera_ids=1,
                           board_id=int(board_id))

if __name__ == '__main__':
    app.run()
