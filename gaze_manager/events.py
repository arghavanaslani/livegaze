from datetime import datetime

from flask_socketio import join_room, send, emit

# from flask_socketio import send

from flask import request
from .models import GazeData, GazeDatabaseModel
from gaze_manager import gaze_manager
from extensions.db_config import redis_client, db
from extensions import redis_constants
from trackers.models import Tracker, TrackerState
from trackers.utils import updated_tracker_state
import json




def get_tracker_model(tracker_id):
    tracker = db.session.query(Tracker).filter_by(tracker_id=tracker_id)
    if tracker.count() == 0:
        tracker = Tracker(tracker_id=tracker_id, tracker_state=TrackerState.sending_data)
        db.session.add(tracker)
    else:
        tracker = tracker.first()
    return tracker


def register_events(socket_io):

    @socket_io.on('new_gaze_data', namespace='/gaze')
    def new_data_received(data):
        data['timestamp'] = datetime.utcnow().timestamp()
        gaze_data = GazeData(**data)
        if not gaze_manager.update_thread.is_alive():
            gaze_manager.update_thread.start()
        if not redis_client.sismember(redis_constants.TRACKERS_SET, gaze_data.camera_id):
            redis_client.sadd(redis_constants.TRACKERS_SET,gaze_data.camera_id)
            tracker = get_tracker_model(gaze_data.camera_id)
            tracker.tracker_state = TrackerState.sending_data
            updated_tracker_state(gaze_data.camera_id, TrackerState.sending_data)
            db.session.commit()
        redis_client.set(redis_constants.get_tracker_key(gaze_data.camera_id), json.dumps(data))
        redis_client.set(redis_constants.get_dbtracker_key(gaze_data.camera_id), json.dumps(data))
        # db.session.add(GazeDatabaseModel(gaze_data))
        #
        #
        # # print(gaze_data.stim_id, gaze_data.camera_id, gaze_data.pos_x, gaze_data.pos_y)
        # gaze_manager.show_data[gaze_data.stim_id][gaze_data.camera_id] = gaze_data

    @socket_io.on('subscribe_gaze_data', namespace='/board')
    def subscribe_gaze_data(data):
        board_id = str(data['board_id'])
        if not gaze_manager.update_thread.is_alive():
            gaze_manager.update_thread.start()
        redis_client.sadd(redis_constants.BOARD_TRACKERS_SET,board_id)
        join_room("board_" + board_id, namespace='/board')
        emit("subscribed to gaze data", {'room': "board_" + board_id})

    @socket_io.on('ping', namespace='/gaze')
    def ping(data):
        print("ping received")
        tracker_id = str(data['camera_id'])
        tracker = get_tracker_model(tracker_id)
        tracker.tracker_state = TrackerState.ready
        redis_client.set(redis_constants.get_session_key(request.sid), tracker_id)
        updated_tracker_state(tracker_id, tracker.tracker_state)
        db.session.commit()
        emit('pong')

    @socket_io.on('disconnect', namespace='/gaze')
    def gaze_disconnect():
        tracker_id = redis_client.get(redis_constants.get_session_key(request.sid))
        print("disconnect received")
        if tracker_id is None:
            return
        tracker_id = tracker_id.decode('utf-8')
        tracker = get_tracker_model(tracker_id)
        tracker.tracker_state = TrackerState.inactive
        db.session.commit()
        redis_client.srem(redis_constants.TRACKERS_SET, tracker_id)
        redis_client.delete(redis_constants.get_tracker_key(tracker_id))
        redis_client.delete(redis_constants.get_session_key(request.sid))
        redis_client.srem(redis_constants.BOARD_TRACKERS_SET, tracker_id)
        updated_tracker_state(tracker_id, TrackerState.inactive)


