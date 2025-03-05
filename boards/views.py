from flask import Blueprint, render_template, current_app, redirect, url_for, Response, request
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.datastructures import CombinedMultiDict

from boards.utils import gen_artwork_img
from boards.forms import ArtworkForm, StimForm
from boards.models import Board, Stimulus, StimulusBoard, StimType
from settings.models import Settings
from werkzeug.utils import secure_filename
from extensions.db_config import db
import json
import os
import re
import requests
from boards.utils import get_unique_filename

board_blueprint = Blueprint('boards', __name__)


@board_blueprint.route('/')
def get_artworks():
    boards = db.session.query(Board).all()
    return render_template('boards/artworks.html',
                           title='Artworks', boards=boards)


@board_blueprint.route('/new', methods=['GET', 'POST'])
def add_artwork():
    stimuli = db.session.query(Stimulus).all()
    print(stimuli)
    return render_template('boards/create_board.html', stimuli=stimuli)
    # form = ArtworkForm()
    # if form.validate_on_submit():
    #     artwork = Board(name=form.name.data, bio=form.bio.data)
    #     uploaded_image = form.image.data
    #     image_name = secure_filename(uploaded_image.filename)
    #     image_path = os.path.join(current_app.config['ARTWORK_UPLOAD_PATH'], image_name)
    #     image_path = get_unique_filename(image_path)
    #     uploaded_image.save(image_path)
    #     artwork.image_path = image_path
    #     db.session.add(artwork)
    #     db.session.commit()
    #     flash('Artwork has been successfully added')
    #     return redirect(url_for('boards.add_artwork'))
    # return render_template('boards/add_artworks.html', form=form, title='Add Artwork')


@board_blueprint.route('/save_board', methods=['POST'])
def save_board():
    stim_ids = request.form.getlist('stimuli[]')
    board_name = request.form.get('board_name')
    if not stim_ids or len(stim_ids) == 0:
        return Response({'error': 'Please select at least one stimulus'}, 400)
    if not board_name or board_name is None or len(board_name) == 0:
        return Response({'error': 'Please enter a board name'}, 400)
    new_board = Board(name=board_name)
    db.session.add(new_board)
    db.session.commit()
    for i, stim_id in enumerate(stim_ids):
        db.session.add(StimulusBoard(board_id=new_board.id, stim_id=stim_id, order_in_board=i))
    db.session.commit()
    return redirect(url_for('main_page.index'), code=302)


@board_blueprint.route('/upload_stim', methods=['POST'])
def add_stim():
    stim_form = StimForm(formdata=CombinedMultiDict((request.files, request.form)))
    if stim_form.validate():
        uploaded_file = stim_form.stim_file.data
        file_name = secure_filename(uploaded_file.filename)
        file_path = os.path.join(current_app.config['STIMULI_UPLOAD_PATH'], file_name)
        file_path = get_unique_filename(file_path)
        uploaded_file.save(file_path)
        stim = Stimulus(file_path=file_path)
        db.session.add(stim)
        db.session.commit()
        print(stim.id, stim.file_path)
        return Response(json.dumps({'stim_id': stim.id, 'stim_path': stim.file_path}),mimetype='application/json',status=200)
    return Response(json.dumps({'error': 'Invalid file'}), mimetype='application/json',status=400)

@board_blueprint.route('/submit_youtube', methods=['POST'])
def submit_youtube():
    video_id = request.form.get('video_id')
    # check if YouTube video id is valid
    response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={current_app.config["YOUTUBE_API_KEY"]}&part=id')
    if response.status_code != 200:
        return Response(json.dumps({'error': 'Invalid YouTube video id'}), mimetype='application/json', status=400)
    data = response.json()
    if not data['items']:
        return Response(json.dumps({'error': 'Invalid YouTube video id'}), mimetype='application/json', status=400)
    if data['pageInfo']['totalResults'] == 0:
        return Response(json.dumps({'error': 'Invalid YouTube video id'}), mimetype='application/json', status=400)

    stim = Stimulus(stim_type=StimType.YOUTUBE, file_path=video_id)
    db.session.add(stim)
    db.session.commit()

    return Response(json.dumps({'stim_path': video_id, 'stim_id': stim.id}), mimetype='application/json', status=200)


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
    stimuli_paths = [stimulus.stimulus.file_path for stimulus in board.stimuli]
    settings = db.session.query(Settings).first()
    context = {
        'stimuli_paths': stimuli_paths,
        'board_id': board_id,
        'pointer_size': settings.pointer_size,
        'aruco_id': board.tag_id,
        'selected_label_id': 0,
    }
    return render_template('boards/simple_board.html', **context)


@board_blueprint.route('/calibration')
def get_calib():
    return render_template('calibration.html', title='Calibration')
