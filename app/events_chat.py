from flask import session, request
from flask_socketio import emit
from app import socketio, queries, redis, shouts
from app import db
from app import commands
# from app import translate
import json

def emit_active_users(room=''):
    if not room:
        room = request.sid
    emit('activeusers', queries.get_active_users(s_user=session['s_user']), room=room)


def emitlastmessages(pmid, room=''):
    if int(pmid) == -1:
        if room == '':
            room = session.get('room')

        unreads = queries.get_unread_pms(session['s_user'])

        socketio.emit('messages', {'pmid': pmid,
                                   'msgs': shouts.get_array_last_messages(),  # queries.get_last_messages(userid=-1),
                                   'unreads': unreads}
                      , room=room)  # userid=session['s_user']

# def get_offline_unread(unreads):
#     res = []
#     usr = queries.get_user_by_userid(4)
#     res.append({'userid': str(usr.userid), 'userlook': queries.userlook(usr), 'online': False, 'unread': False})
#     return res


def emit_one_message(action, message):
    if message.s_private == -1:
        rooms = [session.get('room')]
    else:
        # rooms = [session.get('s_user')]
        rooms = [str(message.s_user)]
        if not str(message.s_private) in rooms:
            rooms.append(str(message.s_private))

    if action == 'delete':
        msg = {'sid': message.sid, 'pmid': str(message.s_private)}
    else:
        msg = queries.msg(message, False)

    # msg['msg'] = translate.translate(msg['msg'], 'eo')['text'][0]

    for room in rooms:
        socketio.emit('one_message', {'action': action, 'message': msg}, room=room)


def check_adminpermissions():
    if not 'adminpermissions' in session:
        session['adminpermissions'] = queries.get_adminpermissions(session['s_user'])
    return session['adminpermissions']


@socketio.on('get_activeusers')
def get_activeusers():
    emit_active_users()


@socketio.on('get_messages')
def get_messages(data):
    return json.dumps({'msgs': shouts.get_array_last_messages()})


@socketio.on('load_messages')
def load_messages(data):
    return json.dumps({'msgs': queries.get_messages(session['s_user'], data['pmid'], data['sid'])})


@socketio.on('chat_text')
def text(message, chat_socket=''):
    msg = message['msg']
    doshout = True
    s_me = '0'
    s_private = message['pmid']

    if msg[:4] == '/me ':
        s_me = '1'
        msg = msg[4:]

    doshout, msg, new_shouts, callbacks = commands.fetch_command(doshout, msg, s_me, s_private)

    for new_shout in new_shouts:
        news = shouts.do_newshout(new_shout.get('s_user'),
                                  new_shout.get('msg'),
                                  new_shout.get('s_me'),
                                  new_shout.get('s_private'))
        emit_one_message('new', news)

    if doshout:
        newshout = shouts.do_newshout(session['s_user'], msg, s_me, s_private)

        if newshout.s_private == -1:
            try:
                # pylint:disable-msg=E1101
                iserttext = "insert into Corvus (s_user, s_time, s_shout, s_me, s_private) " \
                            "values (:s_user, :s_time, :s_shout, :s_me, :s_private)"
                db.session.execute(iserttext, {'s_user': newshout.s_user,
                                               's_time': newshout.s_time,
                                               's_shout': newshout.s_shout,
                                               's_me': newshout.s_me,
                                               's_private': newshout.s_private})
                db.session.commit()

                # db.
            except:
                print('Corv do not remember post: '+newshout.s_shout)

        if not newshout.s_private == -1:
            set_unread_pm(session['s_user'], s_private)

        emit_one_message('new', newshout)

    if callbacks:
        return json.dumps(callbacks)


def set_unread_pm(s_user, s_private):
    redis.hset('pm_%s' % s_private, 'usr_%s' % s_user, s_user)


def del_unread_pm(s_user, s_private):
    redis.hdel('pm_%s' % s_user, 'usr_%s' % s_private)


@socketio.on('edit_message')
def edit_message(message):
    ismsgexist, shout = queries.get_message_by_sid(message['sid'], True)
    if ismsgexist and (shout['s_user'] == session['s_user'] or check_adminpermissions()):
        return {'shout': shout}
    else:
        return None


@socketio.on('edit_commit')
def edit_message_commit(message):
    # pylint:disable-msg=E1101
    editshout = queries.find_shout_by_sid(message['sid'])
    # pmid = editshout.s_private
    editshout.s_shout = message['msg']
    db.session.commit()
    shouts.edit_shout_in_last(editshout)
    emit_one_message('edit', editshout)


@socketio.on('edit_delete')
def edit_delete(message):
    editshout = shouts.delete_shout(message['sid'])
    emit_one_message('delete', editshout)


@socketio.on('open_private')
def open_private(message):
    pmid = message['pmid']
    del_unread_pm(session['s_user'], pmid)
    return json.dumps(queries.get_pm_by_mpid(session['s_user'], pmid))


@socketio.on('read_private')
def read_private(message):
    del_unread_pm(session['s_user'], message)
    return None
