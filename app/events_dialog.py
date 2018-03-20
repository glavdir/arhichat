# -*- coding: utf-8 -*-
from flask import session, request
from flask_socketio import emit, join_room, leave_room, rooms
from app import socketio, sql_posts, models, db, queries, sql_threads, api, default_color, events_chat, redis, shouts, post_parser
import json, datetime, time
import diff_match_patch
import requests

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

    emit('dialog_message', {'pagetext': pagetext, 'color':color, 'postid':postid},room=dlg_room(session.get('chn')), namespace=cur_namespace)

    if delsid!=0:
        del_shout = models.arhinfernoshout()
        del_shout.sid = delsid
        events_chat.emit_one_message('delete', del_shout)
        socketio.emit('one_message', {'action': 'delete', 'message': {'sid':delsid, 'pmid':-1}}, room=session.get('room'))

    events_chat.emit_one_message('new',newshout)


def bb_msg(color, text):
    return text
    # return "[color=%s]%s[/color]"%(color,text)

def save_reply(reply, color):
    postid, pagetext_html, time = sql_posts.save_post({'postid':'',
                                                 'userid':session['s_user'],
                                                 'threadid':session['chn'],
                                                 'color': color,
                                                 'pagetext':bb_msg(color,reply)
                                                 })
    # newpost = sql_posts.arhpost()
    #
    # newpost.threadid   = session['chn']
    # newpost.userid     = session['s_user']
    # newpost.dateline   = int(time.time())
    # newpost.pagetext   = bb_msg(color,reply)
    # newpost.allowsmilie = 1
    # newpost.showsignature = 1
    # newpost.visible = 1
    # newpost.color = color
    #
    # db.session.add(newpost)
    # db.session.commit()
    #
    # newpostparsed = sql_posts.arhpostparsed()
    # newpostparsed.postid = newpost.postid
    # newpostparsed.dateline   = newpost.dateline
    # newpostparsed.pagetext_html   =   post_parser.format(newpost.pagetext) #"<font color='%s'>%s</font>"%(color,reply)
    # db.session.add(newpostparsed)
    # db.session.commit()

    reqText = "http://arhimag.org/rebuild.php?threadid=%s"%session['chn']
    req = requests.get(reqText, headers={'Content-Type': 'application/json'})
    # print(reqText, req.status_code, req.text)
    return postid, pagetext_html

def change_reply(message):
    # reply = models.dialogs.query.filter_by(id=message['id']).first()
    # reply.reply = message['msg']

    # post = sql_posts.arhpost().query.filter_by(postid=message['id']).first()
    # # post.pagetext   = "[color=%s]%s[/color]"%(post.color,message['msg'])
    # post.pagetext = bb_msg(message['color'],message['msg'])
    #
    # postparsed = sql_posts.arhpostparsed().query.filter_by(postid=message['id']).first()
    # postparsed.pagetext_html = post_parser.format(post.pagetext) #"<font color='%s'>%s</font>"%(color,reply)
    # db.session.commit()

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
    # threading.Thread(target=save_diffs, args=(data, threadid, user_id))
    emit('diff', {'userid': user_id, 'diffs': data['diffs'], 'color': data['color']}, room=dlg_room(session.get('chn')), broadcast=True, include_self=False)
    save_diffs(data, threadid, user_id)

def save_diffs(data, threadid, user_id):
    prw = redis.hget('dlg_%s' % threadid, 'usr_%s' % user_id)
    if prw:
        prw = eval(prw)
        text = str(prw['msg'])
    else:
        text = ''

    msg, nottext = dmp.patch_apply(dmp.patch_fromText(data['diffs']),text)
    pr_msg = {'userid': user_id, 'msg': msg, 'color': data['color']}
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

def get_thread_color(threadid):
    colors = get_colors()
    key = color_key(threadid)
    if key in colors['threads']:
        return colors['threads'][key]
    else:
        return colors['default']


def set_thread_color(threadid, color):
    colors = get_colors()
    key = color_key(threadid)

    colors['threads'][key] = color
    colors['default'] = color

    redis.hset(opts_key(), 'colors', json.dumps(colors))

def get_thread(threadid):
    return {'posts': sql_posts.get_lastposts(threadid),'color': get_thread_color(threadid), 'is_favorite':is_favorite_thread(threadid), 'previews':get_previews(threadid)}

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
