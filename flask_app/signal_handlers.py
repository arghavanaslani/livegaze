import sys

from flask_app.extensions import redis_constants
from flask_app.gaze_manager import gaze_manager
from flask_app.extensions.db_config import redis_client


def signal_int_handler(signum, frame):
    gaze_manager.update_thread.stop_thread()
    redis_client.set(redis_constants.RECORD, 'False')
    sys.exit(0)


