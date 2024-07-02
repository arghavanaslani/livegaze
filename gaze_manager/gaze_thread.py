import queue
import threading

from .models import GazeData
from extensions.db_config import redis_client
from extensions import redis_constants
import json


class GazeUpdateThread(threading.Thread):
    def __init__(self, gaze_queue: queue.Queue, show_data: dict[int, dict[str, GazeData]]):
        super().__init__()
        self.gaze_queue = gaze_queue
        self.show_data = show_data
        self.exit_flag = False

    def run(self):
        while not self.exit_flag:
            eye_trackers = redis_client.smembers(redis_constants.TRACKERS_SET)
            for eye_tracker in eye_trackers:
                eye_tracker = eye_tracker.decode('utf-8')
                data = redis_client.get(redis_constants.get_tracker_key(eye_tracker))
                if data is not None:
                    gaze_data = GazeData(**json.loads(data))
                    if gaze_data.stim_id not in self.show_data:
                        self.show_data[gaze_data.stim_id] = dict()
                    self.show_data[gaze_data.stim_id][gaze_data.camera_id] = gaze_data
                    # print(gaze_data.stim_id, gaze_data.camera_id, gaze_data.pos_x, gaze_data.pos_y)
            # gaze_data: GazeData = self.gaze_queue.get()
            # if gaze_data.stim_id not in self.show_data:
            #     self.show_data[gaze_data.stim_id] = dict()
            # self.show_data[gaze_data.stim_id][gaze_data.camera_id] = gaze_data

            # TODO: update DB?
    def stop_thread(self):
        self.exit_flag = True

