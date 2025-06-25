from flask import Blueprint, render_template, current_app, redirect, url_for, Response, request
from flask_login import login_required
from werkzeug.datastructures import CombinedMultiDict

from flask_app.boards.utils import gen_artwork_img
from flask_app.boards.forms import StimForm
from flask_app.boards.models import Board, Stimulus, StimulusBoard, StimType
from flask_app.settings.models import Settings
from werkzeug.utils import secure_filename
from flask_app.extensions.db_config import db
import json
import os
import requests
import ffmpeg
import sys
from flask_app.boards.utils import get_unique_filename

board_blueprint = Blueprint('boards', __name__)


@board_blueprint.route('/')
@login_required
def get_artworks():
    boards = db.session.query(Board).order_by(Board.date_added).all()
    return render_template('boards/artworks.html',
                           title='Artworks', boards=boards)


@board_blueprint.route('/new', methods=['GET', 'POST'])
@login_required
def add_artwork():
    stimuli = db.session.query(Stimulus).order_by(Stimulus.date_added).all()
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
@login_required
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
@login_required
def add_stim():
    stim_form = StimForm(formdata=CombinedMultiDict((request.files, request.form)))
    if stim_form.validate():
        # check if the file is a valid image or video
        if not stim_form.stim_file.data or not stim_form.stim_file.data.filename:
            return Response(json.dumps({'error': 'Invalid file'}), mimetype='application/json', status=400)
        if not stim_form.stim_file.data.content_type.startswith(('image/', 'video/')):
            return Response(json.dumps({'error': 'Invalid file type'}), mimetype='application/json', status=400)
        uploaded_file = stim_form.stim_file.data
        file_name = secure_filename(uploaded_file.filename)
        file_path = os.path.join(current_app.config['STIMULI_UPLOAD_PATH'], file_name)
        file_path = get_unique_filename(file_path)
        uploaded_file.save(file_path)
        thumbnail_path = file_path
        if uploaded_file.content_type.startswith('video/'):
            # create a thumbnail for the video
            thumbnail_path = get_unique_filename(os.path.splitext(file_path)[0] + '.jpg')
            probe = ffmpeg.probe(file_path)
            time = float(probe['streams'][0]['duration']) // 2
            width = probe['streams'][0]['width']
            try:
                (
                    ffmpeg
                    .input(file_path, ss=time)
                    .filter('scale', width, -1)
                    .output(thumbnail_path, vframes=1)
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
            except ffmpeg.Error as e:
                print(e.stderr.decode(), file=sys.stderr)
                sys.exit(1)
        stim = Stimulus(file_path=file_path, thumbnail_path=thumbnail_path, stim_type=StimType.IMAGE if uploaded_file.content_type.startswith('image/') else StimType.VIDEO)
        db.session.add(stim)
        db.session.commit()
        return Response(json.dumps({'stim_id': stim.id, 'stim_path': stim.file_path, 'thumbnail_path' : thumbnail_path}),mimetype='application/json',status=200)
    return Response(json.dumps({'error': 'Invalid file'}), mimetype='application/json',status=400)

@board_blueprint.route('/submit_youtube', methods=['POST'])
@login_required
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

    stim = Stimulus(stim_type=StimType.YOUTUBE, file_path=video_id, thumbnail_path='https://img.youtube.com/vi/' + video_id + '/hqdefault.jpg')
    db.session.add(stim)
    db.session.commit()

    return Response(json.dumps({'stim_path': video_id, 'stim_id': stim.id}), mimetype='application/json', status=200)

@board_blueprint.route('/submit_webpage', methods=['POST'])
@login_required
def submit_web():
    web_url = request.form.get('web_url')
    if not web_url or len(web_url) == 0:
        return Response(json.dumps({'error': 'Please enter a valid URL'}), mimetype='application/json', status=400)
    if not web_url.startswith(('http://', 'https://')):
        web_url = 'http://' + web_url
    stim = Stimulus(stim_type=StimType.WEBPAGE, file_path=web_url, thumbnail_path='https://www.google.com/s2/favicons?domain=' + web_url)
    db.session.add(stim)
    db.session.commit()
    return Response(json.dumps({'stim_path': web_url, 'stim_id': stim.id}), mimetype='application/json', status=200)


@board_blueprint.route('/simple/<string:board_id>/<string:screen_height>/<string:screen_width>')
@login_required
def mapped_gaze_feed(board_id, screen_height, screen_width):
    artwork = db.session.query(Board).get(board_id)
    settings = db.session.query(Settings).first()
    return Response(gen_artwork_img('simple', int(screen_width), int(screen_height), artwork, settings),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@board_blueprint.route('/torch/<string:board_id>/<string:screen_height>/<string:screen_width>')
@login_required
def get_torch_feed(board_id, screen_height, screen_width):
    artwork = db.session.query(Board).get(board_id)
    settings = db.session.query(Settings).first()
    return Response(gen_artwork_img('torch', int(screen_width), int(screen_height), artwork, settings),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@board_blueprint.route('/simple_js/<string:board_id>')
@login_required
def get_simple_js(board_id):
    board = db.session.query(Board).get(board_id)
    # stimuli_paths = [stimulus.stimulus.file_path for stimulus in board.stimuli]
    # stimuli_types = [stimulus.stimulus.stim_type for stimulus in board.stimuli]
    stimuli = [stimulus.stimulus for stimulus in board.stimuli]
    settings = db.session.query(Settings).first()
    context = {
        'stimuli': stimuli,
        'board_id': board_id,
        'pointer_size': settings.pointer_size,
        'aruco_id': board.tag_id,
        'selected_label_id': 0,
    }
    return render_template('boards/simple_board.html', **context)

@board_blueprint.route('/calibration')
def get_calib():
    return render_template('calibration.html', title='Calibration')
