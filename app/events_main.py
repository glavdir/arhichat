from flask import session, request
from app import socketio, clients, api
from flask_socketio import emit, join_room
import datetime
from app import events_chat,events_dialog,queries,shouts


def on_connect():
    try:
        api.auth()
    except:
        pass
    try:
        if request.cookies.get('bbuserid'):
            session['s_user'] = request.cookies.get('bbuserid')
    except:
        print(request.cookies)

    try:
        print(str(datetime.datetime.now())+' connect-' + str(request.sid)+' usr:'+str(session['s_user']))
        clients[request.sid] = session['s_user']
    except:
        pass
        # print('Кто-то не может войти')

    if not session.get('s_user'):
        session['s_user']=0

    session['room'] = 'myroom'

    # join_room(request.sid)
    join_room(session.get('s_user'))
    join_room(session.get('room'))

    events_chat.emitlastmessages(-1,request.sid)
    events_chat.emit_active_users(room=session.get('room'))


@socketio.on('connect')
def connect():
    on_connect()


@socketio.on('disconnect')
def disconnect():
    print(str(datetime.datetime.now())+' disconnect-'+str(request.sid))

    # emit('preview_message', {'sid':request.sid, 'msg': '', 'color':''},room=session.get('chn'), broadcast=True, include_self=False)
    if request.sid in clients:
        del clients[request.sid]
    # socketio.close_room(request.sid)

    events_chat.emit_active_users(room=session.get('room'))


@socketio.on('reconnect')
def reconnect():
    print(str(datetime.datetime.now())+' reconnect-' + str(request.sid))
    # events_chat.emitlastmessages(-1,request.sid)
    on_connect()


@socketio.on('error')
def error():
    print(str(datetime.datetime.now())+' error-' + str(request.sid))
    on_connect()


@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    print(str(datetime.datetime.now())+' error-' + str(request.sid))
    on_connect()

# @socketio.on('king')
# def king(data):
#     # join_room('myroom')
#     # return None
#     emit('kong',room=request.sid)


@socketio.on('save_option')
def save_option(data):
    # print(data)
    # if session.get('options'):
    #     options = session['options']
    # else:
    options = queries.get_options_by_userid(session['s_user'])

    for key in data:
        if key in options:
            options[key] = data[key]

    session['options'] = options

    update_shouts = queries.save_options(options,session['s_user'])

    if update_shouts:
        shouts.set_lm_color(session['s_user'],options['s_color'])
        events_chat.emitlastmessages(-1)
