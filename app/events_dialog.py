# -*- coding: utf-8 -*-
import json
import datetime
import requests
import diff_match_patch

from flask import session, request
from flask_socketio import emit, join_room, leave_room
from app import socketio, sql_posts, models, sql_threads, api, default_color, events_chat, redis, shouts

dmp = diff_match_patch.diff_match_patch()

cur_namespace=''
expire_date = datetime.datetime.now() + datetime.timedelta(days=365 * 10)

def dlg_room(threadid):
    return 'dlg_'+str(threadid)

@socketio.on('dialog_start', namespace=cur_namespace)
def dialog_start(message):
    threadid = str(message['threadid'])
    session['chn'] = threadid
    join_room(dlg_room(threadid))
    join_room('myroom')
    return {'sid':request.sid}

@socketio.on('send_text', namespace=cur_namespace)
def dialog_text(message):
    threadid = str(message['threadid'])
    session['chn'] = threadid
    msg = message['msg']
    color = message['color']

    postid,pagetext = save_reply(msg,color)

    delsid = shouts.delete_last_by_dialog_id(threadid)

    userid = session['s_user'] if session['s_user'] else 0
    newshout = shouts.do_newshout(userid, 'ответил(а) на канале [dialog=%(dialog_id)s]%(title)s[/dialog]' % {'dialog_id':threadid, 'title':sql_threads.get_thread_title(threadid)}, '1', -1, threadid)

    emit('dialog_message', {'pagetext': pagetext, 'color':color, 'postid':postid, 'comments':[]},room=dlg_room(session.get('chn')), namespace=cur_namespace)

    if delsid!=0:
        del_shout = models.arhinfernoshout()
        del_shout.sid = delsid
        events_chat.emit_one_message('delete', del_shout)
        socketio.emit('one_message', {'action': 'delete', 'message': {'sid':delsid, 'pmid':-1}}, room=session.get('room'))

    events_chat.emit_one_message('new',newshout)

@socketio.on('send_comment', namespace=cur_namespace)
def send_comment(message):
    threadid = str(message['threadid'])
    session['chn'] = threadid
    msg = message['msg']
    color = message['color']

    commentdata = {'postid': message['postid'],
                   'userid': session['s_user'],
                   'threadid': session['chn'],
                   'color': color,
                   'text': msg}

    sql_posts.save_comment(commentdata)
    emit('dialog_comment', commentdata, room=dlg_room(session.get('chn')),namespace=cur_namespace)



def bb_msg(color, text):
    return text

def refresh_forum():
    reqText = "http://arhimag.org/rebuild.php?threadid=%s"%session['chn']
    req = requests.get(reqText, headers={'Content-Type': 'application/json'})

def save_reply(reply, color):
    postid, pagetext_html, time = sql_posts.save_post({'postid':'',
                                                 'userid':session['s_user'],
                                                 'threadid':session['chn'],
                                                 'color': color,
                                                 'pagetext':bb_msg(color,reply)
                                                 })
    refresh_forum()
    return postid, pagetext_html

def change_reply(message):
    postid, pagetext_html, time = sql_posts.save_post({'postid':message['id'],
                                                 'pagetext':bb_msg(message['color'],message['msg']),
                                                 'color':message['color']
                                                 })
    return pagetext_html

@socketio.on('dialog_preview', namespace=cur_namespace)
def dialog_preview(message):
    msg = message['msg']
    color = message['color']

    threadid = session.get('chn')
    user_id = session.get('s_user')

    pr_msg = {'userid': user_id, 'msg': msg, 'color':color}

    redis.hset('dlg_%s'%threadid,'usr_%s'%user_id, pr_msg)

    emit('preview_message', pr_msg ,room=dlg_room(session.get('chn')), broadcast=True, include_self=False)

@socketio.on('diff', namespace=cur_namespace)
def diff(data):
    threadid = session.get('chn')
    user_id = session.get('s_user')

    if 'color' in data:
        color = data['color']
    else:
        color = ''

    if 'isCommenting' in data:
        isCommenting = data['isCommenting']
    else:
        isCommenting = False

    emit('diff', {'userid': user_id, 'diffs': data['diffs'], 'color': color, 'isCommenting':isCommenting}, room=dlg_room(session.get('chn')), broadcast=True, include_self=False)
    save_diffs(data, threadid, user_id)

def save_diffs(data, threadid, user_id):
    prw = redis.hget('dlg_%s' % threadid, 'usr_%s' % user_id)
    if prw:
        prw = eval(prw)
        text = str(prw['msg'])
    else:
        text = ''

    if 'color' in data:
        color = data['color']
    else:
        color = ''

    if 'isCommenting' in data:
        isCommenting = data['isCommenting']
    else:
        isCommenting = False

    msg, nottext = dmp.patch_apply(dmp.patch_fromText(data['diffs']),text)
    pr_msg = {'userid': user_id, 'msg': msg, 'color': color, 'isCommenting':isCommenting}
    redis.hset('dlg_%s'%threadid,'usr_%s'%user_id, pr_msg)

def get_previews(threadid):
    redis_previews = redis.hgetall('dlg_%s' % threadid)

    for key in redis_previews:
        prw = redis_previews.get(key)
        redis_previews[key] = eval(prw)

    return redis_previews

@socketio.on('dialog_change', namespace=cur_namespace)
def dialog_change(message):
    html_msg =  change_reply(message)
    emit('dialog_change_commit', {'msg': html_msg, 'id':message['id'] },room=dlg_room(session.get('chn')), broadcast=True, include_self=False)

@socketio.on('del_post', namespace=cur_namespace)
def del_post(message):
    postid = sql_posts.del_post(message)
    emit('post_deleted', {'postid': postid},room=dlg_room(session.get('chn')), broadcast=True, include_self=True)
    refresh_forum()

@socketio.on('set_color', namespace=cur_namespace)
def set_color(message):
    userid = session['s_user']
    if userid!=0:
        set_thread_color(message['threadid'], message['color'])
        emit('color_set', {'userid': userid, 'color': message['color']}, room=dlg_room(message['threadid']))

def opts_key():
    s_user = session.get('s_user')

    if not s_user:
        api.auth()

    return 'opts_'+str(session.get('s_user'))

@socketio.on('set_favorites', namespace=cur_namespace)
def set_favorites(message):
    userid = session['s_user']
    if userid!=0:
        threadid = str(message['threadid'])
        favorites = get_favorites()

        if not threadid in favorites:
            favorites.append(threadid)
        elif threadid in favorites:
            favorites.remove(threadid)

        redis.hset(opts_key(), 'fav_threads', json.dumps(favorites))

def get_favorites():
    favorites_str = redis.hget(opts_key(), 'fav_threads')

    if not favorites_str:
        favorites = []
    else:
        favorites = json.loads(favorites_str)

    return favorites

def is_favorite_thread(threadid):
    return threadid in get_favorites()


def color_key(threadid):
    return 'color_'+str(threadid)


def get_colors():
    colors_str = redis.hget(opts_key(), 'colors')
    if not colors_str:
        colors = {'default': default_color, 'threads': {}}
    else:
        colors = json.loads(colors_str)
    return colors

@socketio.on('set_noteID', namespace=cur_namespace)
def set_noteID(message):
    redis.hset('noteID',message['threadid'],message['noteID'])

def get_noteID(threadid):
    return redis.hget('noteID', threadid)


def get_thread_color(threadid):
    colors = get_colors()
    key = color_key(threadid)
    if key in colors['threads']:
        return colors['threads'][key]
    else:
        return colors['default']

def get_thread_is_comment(threadid):
    isCommenting=False
    inRedis = redis.hget(opts_key(), 'is_commenting_'+str(threadid))
    if inRedis:
        isCommenting = inRedis=='True'
    return isCommenting

@socketio.on('set_commenting', namespace=cur_namespace)
def set_commenting(message):
    redis.hset(opts_key(), 'is_commenting_'+str(message['threadid']), message['isCommenting'])

def set_thread_color(threadid, color):
    colors = get_colors()
    key = color_key(threadid)

    colors['threads'][key] = color
    colors['default'] = color

    redis.hset(opts_key(), 'colors', json.dumps(colors))

def get_thread(threadid):
    return {'posts': sql_posts.get_lastposts(threadid),
            'color': get_thread_color(threadid),
            'is_favorite':is_favorite_thread(threadid),
            'previews':get_previews(threadid),
            'noteID':get_noteID(threadid),
            'is_commenting':get_thread_is_comment(threadid)}

@socketio.on('dialog_refresh', namespace=cur_namespace)
def dialog_refresh(message):
    try:
        leave_room(dlg_room(session['chn']))
    except:
        pass

    threadid = str(message['threadid'])
    session['chn'] = threadid
    join_room(dlg_room(session['chn']))
    join_room('myroom')

    return get_thread(threadid)

@socketio.on('set_last_thread', namespace=cur_namespace)
def set_last_thread(data):
    redis.hset(opts_key(), 'threadid', data['threadid'])

def get_last_thread():
    threadid = redis.hget(opts_key(), 'threadid')
    if not threadid:
        threadid = 0
    return threadid
