import time

from sqlalchemy import desc

from app import last_messages
from app import models
from app import db
from app import queries
from app import msgcount
from app import parser

def do_newshout(s_user, msg, s_me, s_private, dialog_id=''):
    newshout = models.arhinfernoshout()
    newshout.s_time = int(time.time())
    newshout.s_user = s_user
    newshout.s_shout = msg
    newshout.s_me = s_me
    newshout.s_private = s_private
    newshout.dialog_id = dialog_id
    db.session.add(newshout)
    db.session.commit()

    if str(s_private)=='-1':
        last_messages[newshout.sid]=queries.msg(newshout, False)
        if len(last_messages)>msgcount:
            last_messages.popitem(last=False)

    return newshout

def delete_shout(sid):
    editshout = queries.find_shout_by_sid(sid)
    db.session.delete(editshout)
    db.session.commit()

    del_shout_from_last(sid,editshout.s_private)

    return editshout

def delete_last_by_dialog_id(dialog_id):
    sid = 0
    if dialog_id:
        q_sid = models.arhinfernoshout.query.filter_by(dialog_id=str(dialog_id)).order_by(desc("sid")).first()
        if q_sid:
            sid = q_sid.sid
            db.session.execute("delete from arhinfernoshout where dialog_id = '%s'" % (str(dialog_id)))
            # del_shout_from_last(sid, q_sid.s_private)
            try:
                del_shout_from_last(sid, q_sid.s_private)
            except:
                pass

    return sid

def del_shout_from_last(sid,s_private):
    if str(s_private)=='-1':
        del last_messages[int(sid)]
        # if len(last_messages)<25:
            # last_messages.clear()
            # last_messages.update(queries.get_last_messages(userid=-1))
            # last_messages.sor
            # for ms in mess:
            #     last_messages[ms.sid] = ms

def edit_shout_in_last(editshout):
    if str(editshout.s_private)=='-1':
        shout = last_messages[editshout.sid]
        if shout:
            shout['msg'] = parser.format(editshout.s_shout)

def get_array_last_messages():
    return list(last_messages.values())[-msgcount:]

def set_lm_color(s_user,s_color):
    for msg in last_messages:
        if last_messages[msg]['s_user']==s_user:
            last_messages[msg]['color'] = s_color
