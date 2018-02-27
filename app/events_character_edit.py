# -*- coding: utf-8 -*-
from flask import session
from flask_socketio import emit
from app import socketio, sql_characters
import json


def simple_character_list(characters):
    result = []
    for character in characters:
        result.append({'name': character.name, 'id': character.id})
    return result


@socketio.on('get_tags')
def send_tags():
    emit('character_tags', json.dumps(get_tags()))


def get_tags():
    tags = sql_characters.get_all_tags()
    return [tag.name for tag in tags]


@socketio.on('find_characters')
def find_characters(filter=None):
    characters = simple_character_list(sql_characters.find_characters(filter))
    emit('character_list', json.dumps(characters))


@socketio.on('get_character_info')
def get_character_info(id):
    result = sql_characters.get_character(id['id'])
    return json.dumps(result)


@socketio.on('save_character')
def save_character(data):
    character = data['Character']

    isNew = False
    if character['author'] is None:  # new character
        character['author'] = session['s_user']
        isNew = True


    tags_count = sql_characters.count_values(sql_characters.Tags)
    character_count = sql_characters.count_values(sql_characters.Characters)

    result_id = sql_characters.write_character(character)

    if (sql_characters.count_values(sql_characters.Tags) > tags_count):
        emit('character_tags', json.dumps(get_tags()), broadcast=True)

    if result_id:
        return json.dumps(sql_characters.get_character(result_id))
    return None


@socketio.on('delete_character')
def delete_character(data):
    result = sql_characters.delete_character(data['Character'])
    return result
