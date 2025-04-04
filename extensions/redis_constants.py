
TRACKERS_SET = f'trackers'
BOARD_TRACKERS_SET = f'board_trackers'


def get_tracker_key(tracker_id: str) -> str:
    return f'tracker:{tracker_id}'

def get_session_key(session_id: str) -> str:
    return f'session:{session_id}'

