from flask import session, request
from app import socketio, sql_threads
import json

@socketio.on('save_forum')
def add_note(data):
    if not data['title']:
        return {'error':'Не заполнено наименование'}

    result = sql_threads.save_forum(data)
    return result
