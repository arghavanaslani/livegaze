import queue
from .gaze_thread import GazeUpdateThread
from .models import GazeData

class GazeManager:
    def __init__(self):
        self.show_data: dict[int, dict[str, GazeData]] = dict()
        # self.gaze_queue = queue.Queue()
        self.update_thread = GazeUpdateThread( self.show_data)
        self.update_thread.daemon = True


gaze_manager = GazeManager()
