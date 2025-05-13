
TRACKERS_SET = f'trackers'
BOARD_TRACKERS_SET = f'board_trackers'
RECORD = f'record'
RECORD_SESSION_ID = f'record_session_id'


def get_tracker_key(tracker_id: str) -> str:
    return f'tracker:{tracker_id}'

def get_dbtracker_key(tracker_id: str) -> str:
    return f'dbtracker:{tracker_id}'

def get_session_key(session_id: str) -> str:
    return f'session:{session_id}'

def is_recording(record) -> bool:
    if record is not None:
        if record.decode('utf-8') == "False":
            return False
    else:
        return False
    return True

