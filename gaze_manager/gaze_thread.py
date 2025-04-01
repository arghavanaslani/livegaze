import queue
import threading

from .models import GazeData
from extensions.db_config import redis_client
from extensions import redis_constants
from gaze_manager.models import GazeDatabaseModel
from sqlalchemy.orm import sessionmaker
from extensions.db_config import db
from flask_socketio import send
from extensions import socket_io
import json
import time


class GazeUpdateThread(threading.Thread):
    def __init__(self, show_data: dict[int, dict[str, GazeData]]):
        super().__init__()
        # self.gaze_queue = gaze_queue
        self.show_data = show_data
        self.exit_flag = False
        self.time_since_last_db_update = 0.0
        self.db_update_interval = 30.0
        self.time_since_last_board_update = 0.0
        self.board_update_interval = 0.01667
        self.app = None

    def run(self):
        self.time_since_last_db_update = time.time()
        self.time_since_last_board_update = time.time()
        while not self.exit_flag:
            eye_trackers =  redis_client.smembers(redis_constants.TRACKERS_SET)
            for eye_tracker in eye_trackers:
                eye_tracker = eye_tracker.decode('utf-8')
                data = redis_client.get(redis_constants.get_tracker_key(eye_tracker))
                if data is not None:
                    gaze_data = GazeData(**json.loads(data))
                    if gaze_data.stim_id not in self.show_data:
                        self.show_data[gaze_data.stim_id] = dict()
                    self.show_data[gaze_data.stim_id][gaze_data.camera_id] = gaze_data
                    # print(gaze_data.stim_id, gaze_data.camera_id, gaze_data.pos_x, gaze_data.pos_y)
            if time.time() - self.time_since_last_db_update > self.db_update_interval:
                with self.app.app_context():
                    db.session.commit()

            # TODO: update DB?
            if time.time() - self.time_since_last_board_update > self.board_update_interval:
                boards = redis_client.smembers(redis_constants.BOARD_TRACKERS_SET)
                for board in boards:
                    board = board.decode('utf-8')
                    data = self.show_data.get(int(board), None)

                    if data is not None:
                        data_to_send = dict()
                        for camera_id, gaze_data in data.items():
                            data_dict = gaze_data.__dict__
                            data_to_send[camera_id] = data_dict
                            # db.session.add(GazeDatabaseModel(GazeData(**data_dict)))
                        socket_io.socket_io.emit('gaze_data', data_to_send, room="board_" + board, namespace='/board')



    def stop_thread(self):
        with self.app.app_context():
            db.session.commit()
        self.exit_flag = True

