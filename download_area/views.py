from flask import Blueprint, render_template, current_app, redirect, url_for, flash, Response, request
from flask_login import login_required, current_user
from gaze_manager.models import GazeDataSession, GazeDatabaseModel
from extensions.db_config import db, redis_client
from extensions import redis_constants
import json

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
    gaze_data = db.session.query(GazeDatabaseModel).filter_by(gaze_data_session_id=session_id).all()

    # Convert to JSON
    gaze_data_json = [gaze_data_item.to_dict() for gaze_data_item in gaze_data]

    # Return as JSON response
    response = current_app.response_class(
        response=json.dumps(gaze_data_json),
        status=200,
        mimetype='application/json'
    )
    return response