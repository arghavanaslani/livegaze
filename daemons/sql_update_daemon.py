import threading
from extensions import redis_constants
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from gaze_manager.models import GazeData, GazeDatabaseModel
from boards.models import Board
import os
if os.path.exists('config.py'):
    from config import SQLALCHEMY_DATABASE_URI as DATABASE_URL
else:
    from config_example import SQLALCHEMY_DATABASE_URI as DATABASE_URL
import time
import json
import redis


class SqlUpdateDaemon(threading.Thread):
    def __init__(self,  db_update_interval=30.0):
        super().__init__()
        self.exit_flag = False
        self.time_since_last_db_update = 0.0
        self.time_since_last_board_update = 0.0
        self.board_update_interval = 0.01667
        self.db_update_interval = 5.0
        engine = create_engine(DATABASE_URL, echo=True)
        session_maker = sessionmaker(bind=engine)
        self.db_session = session_maker()
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


    def run(self):
        while not self.exit_flag:
            time.sleep(0.016)
            record = self.redis_client.get(redis_constants.RECORD)
            if not redis_constants.is_recording(record):
                continue
            record_session_id = self.redis_client.get(redis_constants.RECORD_SESSION_ID).decode('utf-8')
            if time.time() - self.time_since_last_db_update > self.db_update_interval:
                self.db_session.commit()
                self.time_since_last_db_update = time.time()
            if time.time() - self.time_since_last_board_update > self.board_update_interval:
                eye_trackers = self.redis_client.smembers(redis_constants.TRACKERS_SET)
                for eye_tracker in eye_trackers:
                    eye_tracker = eye_tracker.decode('utf-8')
                    data = self.redis_client.get(redis_constants.get_dbtracker_key(eye_tracker))
                    if data is not None:
                        data = data.decode('utf-8')
                        gaze_data = GazeData(**json.loads(data))
                        gd_model = GazeDatabaseModel(gaze_data)
                        gd_model.session_id = record_session_id
                        print("gaze_data", gaze_data)
                        self.db_session.add(gd_model)
                        self.redis_client.delete(redis_constants.get_dbtracker_key(eye_tracker))
                self.time_since_last_board_update = time.time()


if __name__ == "__main__":

    sql_update_daemon = SqlUpdateDaemon()
    sql_update_daemon.daemon = True
    sql_update_daemon.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sql_update_daemon.exit_flag = True
        sql_update_daemon.join()