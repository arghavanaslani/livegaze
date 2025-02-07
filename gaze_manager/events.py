from datetime import datetime

from flask_socketio import join_room, send, emit

# from flask_socketio import send

from .models import GazeData, GazeDatabaseModel
from gaze_manager import gaze_manager
from extensions.db_config import redis_client, db
from extensions import redis_constants
import json


def register_events(socket_io):
    @socket_io.on('new_gaze_data')
    def new_data_received(data):
        # TODO: change variables to match the class
        data['timestamp'] = datetime.utcnow().timestamp()
        gaze_data = GazeData(**data)
        # gaze_data: GazeData = json.loads(data, object_hook=lambda d: GazeData(**d))
        if not gaze_manager.update_thread.is_alive():
            gaze_manager.update_thread.start()
        # gaze_manager.gaze_queue.put(gaze_data)
        redis_client.sadd(redis_constants.TRACKERS_SET,gaze_data.camera_id)
        redis_client.set(redis_constants.get_tracker_key(gaze_data.camera_id), json.dumps(data))
        # db.session.add(GazeDatabaseModel(gaze_data))
        #
        #
        # # print(gaze_data.stim_id, gaze_data.camera_id, gaze_data.pos_x, gaze_data.pos_y)
        # gaze_manager.show_data[gaze_data.stim_id][gaze_data.camera_id] = gaze_data

    @socket_io.on('subscribe_gaze_data')
    def subscribe_gaze_data(data):
        board_id = str(data['board_id'])
        if not gaze_manager.update_thread.is_alive():
            gaze_manager.update_thread.start()
        redis_client.sadd(redis_constants.BOARD_TRACKERS_SET,board_id)
        join_room("board_" + board_id)
        emit("subscribed to gaze data", {'room': "board_" + board_id})

    @socket_io.on('ping')
    def ping():
        print("ping received")
        emit('pong')
