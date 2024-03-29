from datetime import datetime

from extensions.socket_io import socket_io
from .models import GazeData
from gaze_manager import gaze_manager
import json


@socket_io.on('new_gaze_data')
def new_data_received(data):
    # TODO: change variables to match the class
    data['timestamp'] = datetime.utcnow().timestamp()
    gaze_data = GazeData(**data)
    # gaze_data: GazeData = json.loads(data, object_hook=lambda d: GazeData(**d))
    if not gaze_manager.update_thread.is_alive():
        gaze_manager.update_thread.start()
    # print("received gaze data", gaze_data.pos_x, gaze_data.pos_y)
    gaze_manager.gaze_queue.put(gaze_data)
