from flask import session, request
from flask_socketio import emit
from app import db, models, socketio, redis
import json
import diff_match_patch
dmp = diff_match_patch.diff_match_patch()

# @socketio.on('delta')
# def delta(delta):
#     # print(delta)
#     emit('delta',delta, include_self=False, room = session.get('room'))

def get_notes_list():
    order = redis.get('note_order_user_%s'%session['s_user'])

    if not order:
        order = '-1';

    # print(order)

    noteslist = db.session.execute("SELECT id,title FROM notes WHERE private=0 ORDER BY FIND_IN_SET(id,'"+order+"'), id").fetchall()
    # notes = {}
    # for note in noteslist:
    #     notes['note_'+str(note.id)] ={'id':note.id, 'title':note.title, 'editing':False}

    notes = []
    for note in noteslist:
        notes.append({'id':note.id, 'title':note.title, 'editing':False})

    return notes

@socketio.on('add_note')
def add_note(data):
    note= models.notes()
    note.author = session['s_user']
    note.private = 0
    note.title = 'Новая заметка'
    db.session.add(note)
    db.session.commit()
    return {'id':note.id, 'title':note.title}


@socketio.on('rename_note')
def rename_note(data):
    note= models.notes.query.filter_by(id=data['id']).first()
    note.title = data['title']
    db.session.commit()
    return ''

@socketio.on('del_note')
def rename_note(data):
    note= models.notes.query.filter_by(id=data['id']).first()
    db.session.delete(note)
    db.session.commit()
    return True

@socketio.on('notes_order')
def notes_order(data):
    redis.set('note_order_user_%s'%session['s_user'], ','.join(data['order']))
    return ''

@socketio.on('get_notes')
def get_notes(data):
    notes = get_notes_list()
    return {'notes':notes}

def get_note_text(id):
    text = redis.get('note_%s' % id)
    if not text:
        text = ''
    return text

@socketio.on('open_note')
def open_note(data):
    return {'id':data['id'],'note':get_note_text(data['id'])}

@socketio.on('note_diff')
def note_diff(data):
    #emit('diff', {'userid': user_id, 'diffs': data['diffs'], 'color': data['color']}, room=dlg_room(session.get('chn')), broadcast=True, include_self=False)
    old_note = get_note_text(data['id'])
    new_note, nottext = dmp.patch_apply(dmp.patch_fromText(data['diffs']), old_note)
    redis.set('note_%s' % data['id'], new_note)
