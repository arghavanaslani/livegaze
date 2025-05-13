from datetime import datetime

from flask_socketio import join_room, send


def get_room_name(waldo_id: int):
    return f'waldo_{waldo_id}'


def register_waldo_events(socket_io):
    @socket_io.on('waldo_register')
    def waldo_register(data):
        room = data['room']
        join_room(room)
        send(f'user has entered the room.', room=room)

    def send_to_room(room, message):
        send(message, room=room)
