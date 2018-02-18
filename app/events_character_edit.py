# -*- coding: utf-8 -*-
from flask import session, request
from flask_socketio import emit, join_room, leave_room, rooms
from app import socketio, models, db, queries, clients, default_color, events_chat, redis, shouts
import json, datetime, time
import diff_match_patch

dmp = diff_match_patch.diff_match_patch()

cur_namespace=''
expire_date = datetime.datetime.now() + datetime.timedelta(days=365 * 10)


@socketio.on('character_thread_selected')
def character_thread_selected(data):
    characters = queries.get_character_list(data['thread'])
    emit('character_list', json.dumps({'thread': data['thread'], 'characters': [c._asdict() for c in characters]}))
    # return json.dumps([c._asdict() for c in characters])


@socketio.on('get_character_info')
def get_character_info(id):
    result = queries.get_character(id['id'])
    return json.dumps(result)


@socketio.on('save_character')
def save_character(data):
    character = data['Character']
    if character['Author'] is None:
        character['Author'] = session['s_user']
    thread = data['CurrentThread']
    if character['Thread'] is '*':
        character['Thread'] = None
    queries.write_character(character)
    characters = queries.get_character_list(thread)
    emit('character_list', json.dumps({'thread': thread, 'characters': [c._asdict() for c in characters]}))


@socketio.on('delete_character')
def delete_character(data):
    thread = data['CurrentThread']
    result = queries.delete_character(data['Character'])
    if result:
        characters = queries.get_character_list(thread)
        emit('character_list', json.dumps({'thread': thread, 'characters': [c._asdict() for c in characters]}))
    return result
