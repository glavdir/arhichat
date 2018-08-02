from flask import session, request
from app import app, socketio, sql_threads
import json

@app.route('/api/forums/')
def forums():
    threads = sql_threads.get_threadlist()
    forums = sql_threads.get_forums()
    # for thread in threads:
    #     forums[thread['forumid']]['threads'].append(thread)
    return json.dumps(forums)


@socketio.on('save_forum')
def add_note(data):
    if not data['title']:
        return {'error':'Не заполнено наименование'}

    result = sql_threads.save_forum(data)
    return result
