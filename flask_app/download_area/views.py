from flask import Blueprint, render_template, redirect, url_for, flash, Response, request
from flask_login import login_required
from flask_app.gaze_manager.models import GazeDataSession, GazeDatabaseModel
from flask_app.extensions.db_config import db

download_area_blueprint = Blueprint('da', __name__)

@download_area_blueprint.route('/')
@login_required
def get_sessions():
    # Query all GazeDataSession objects from the database where have at least one GazeDatabaseModel, paginate them
    # and pass them to the template
    gaze_data_sessions = db.session.query(GazeDataSession).filter(GazeDataSession.gaze_datas.any()).all()
    # Paginate the results
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total = len(gaze_data_sessions)
    start = (page - 1) * per_page
    end = start + per_page
    sessions = gaze_data_sessions[start:end]
    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page
    return render_template('download_area.html', sessions=sessions, page=page, total_pages=total_pages)

@download_area_blueprint.route('/download_session/<int:session_id>', methods=['GET'])
@login_required
def download_session(session_id):
    # Get the session from the database
    session = db.session.query(GazeDataSession).filter_by(id=session_id).first()
    if session is None:
        flash('Session not found', 'error')
        return redirect(url_for('da.get_sessions'))

    # Get all GazeDatabaseModel objects for this session
    gaze_data = db.session.query(GazeDatabaseModel).filter_by(session_id=session_id).all()

    # Convert to csv
    csv_data = "id,stim_id,camera_id,pos_x,pos_y,session_id,added_date\n"
    for gaze in gaze_data:
        csv_data += f"{gaze.id},{gaze.board_id},{gaze.eyetracker_id},{gaze.gaze_position_x},{gaze.gaze_position_y},{gaze.session_id},{gaze.added_date}\n"

    # Create a response with the csv data
    response = Response(csv_data, mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename=f"gaze_data_session_{session_id}.csv")
    return response