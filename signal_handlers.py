import sys

from gaze_manager import gaze_manager


def signal_int_handler(signum, frame):
    # gaze_manager.update_thread.stop_thread()
    sys.exit(0)


