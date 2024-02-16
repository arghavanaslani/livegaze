from app import socket_io
from .models import GazeData
from gaze_manager import gaze_manager
import json


@socket_io.on('json', namespace='/gaze')
def new_data_received(data):
    gaze_data: GazeData = json.loads(data, object_hook=lambda d: GazeData(**d))
    if not gaze_manager.update_thread.is_alive():
        gaze_manager.update_thread.start()
    print("received gaze data", gaze_data.pos_x, gaze_data.pos_y)
    gaze_manager.gaze_queue.put(gaze_data)