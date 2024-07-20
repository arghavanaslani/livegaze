from flask import Blueprint, render_template, current_app, redirect, url_for, flash, Response
from settings.models import Settings
from artworks.models import Artwork
from artworks.utils import gen_artwork_img
from extensions.db_config import db


waldo_blueprint = Blueprint('waldo', __name__)
WALDO_ID_BEGIN = 3


@waldo_blueprint.route('/main/<string:waldo_id>')
def get_waldo_page(waldo_id):
    return render_template('waldo.html', waldo_id=int(waldo_id))


@waldo_blueprint.route('/<string:waldo_id>/<string:screen_height>/<string:screen_width>')
def get_waldo(waldo_id, screen_height, screen_width):
    waldo_path = f"static/waldo/waldo_{waldo_id}.jpg"
    settings = db.session.query(Settings).first()
    artwork = db.session.query(Artwork).get(int(waldo_id) + WALDO_ID_BEGIN)
    return Response(gen_artwork_img('waldo', int(screen_width), int(screen_height), artwork, settings),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
