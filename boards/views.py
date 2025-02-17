from flask import Blueprint, render_template, current_app, redirect, url_for, flash, Response

from boards.utils import gen_artwork_img
from boards.forms import ArtworkForm
from boards.models import Board
from settings.models import Settings
from werkzeug.utils import secure_filename
from extensions.db_config import db
import os
from boards.utils import get_unique_filename

board_blueprint = Blueprint('boards', __name__)


@board_blueprint.route('/')
def get_artworks():
    boards = db.session.query(Board).all()
    return render_template('boards/artworks.html',
                           title='Artworks', boards=boards)


@board_blueprint.route('/new', methods=['GET', 'POST'])
def add_artwork():
    form = ArtworkForm()
    if form.validate_on_submit():
        artwork = Board(name=form.name.data, bio=form.bio.data)
        uploaded_image = form.image.data
        image_name = secure_filename(uploaded_image.filename)
        image_path = os.path.join(current_app.config['ARTWORK_UPLOAD_PATH'], image_name)
        image_path = get_unique_filename(image_path)
        uploaded_image.save(image_path)
        artwork.image_path = image_path
        db.session.add(artwork)
        db.session.commit()
        flash('Artwork has been successfully added')
        return redirect(url_for('boards.add_artwork'))
    return render_template('boards/add_artworks.html', form=form, title='Add Artwork')


@board_blueprint.route('/simple/<string:board_id>/<string:screen_height>/<string:screen_width>')
def mapped_gaze_feed(board_id, screen_height, screen_width):
    artwork = db.session.query(Board).get(board_id)
    settings = db.session.query(Settings).first()
    return Response(gen_artwork_img('simple', int(screen_width), int(screen_height), artwork, settings),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@board_blueprint.route('/torch/<string:board_id>/<string:screen_height>/<string:screen_width>')
def get_torch_feed(board_id, screen_height, screen_width):
    artwork = db.session.query(Board).get(board_id)
    settings = db.session.query(Settings).first()
    return Response(gen_artwork_img('torch', int(screen_width), int(screen_height), artwork, settings),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@board_blueprint.route('/simple_js/<string:board_id>')
def get_simple_js(board_id):
    board = db.session.query(Board).get(board_id)
    settings = db.session.query(Settings).first()
    context = {
        'board_url': board.image_path,
        'board_id': board_id,
        'pointer_size': settings.pointer_size,
        'aruco_id' : board.tag_id,
        'selected_label_id' : 0,
    }
    return render_template('boards/simple_board.html', **context)


@board_blueprint.route('/calibration')
def get_calib():
    return render_template('calibration.html', title='Calibration')
