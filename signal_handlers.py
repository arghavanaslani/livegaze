import sys

from extensions import redis_constants
from gaze_manager import gaze_manager
from extensions.db_config import redis_client


def signal_int_handler(signum, frame):
    gaze_manager.update_thread.stop_thread()
    redis_client.set(redis_constants.RECORD, 'False')
    sys.exit(0)


