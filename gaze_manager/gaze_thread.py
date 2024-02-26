import queue
import threading

from .models import GazeData


class GazeUpdateThread(threading.Thread):
    def __init__(self, gaze_queue: queue.Queue, show_data: dict[int, dict[str, GazeData]]):
        super().__init__()
        self.gaze_queue = gaze_queue
        self.show_data = show_data
        self.exit_flag = False

    def run(self):
        while not self.exit_flag:
            gaze_data: GazeData = self.gaze_queue.get()
            if gaze_data.stim_id not in self.show_data:
                self.show_data[gaze_data.stim_id] = dict()
            self.show_data[gaze_data.stim_id][gaze_data.camera_id] = gaze_data

            # TODO: update DB?
    def stop_thread(self):
        self.exit_flag = True

