from app import socketio, sql_posts, shouts, events_chat
from flask import session, request
from flask_socketio import emit

bash_threadid = 25 # 25 - id темы с архибашем

@socketio.on('open_bash')
def open_bash(data):
    posts = sql_posts.get_lastposts(bash_threadid, 1, data['postid'], data['direction'])

    if len(posts)==0:
        res = {'pagetext':'Аве Шелли', 'time':0, 'postid':0}
    else:
        res = posts[0]

    return res

@socketio.on('save_bash')
def save_bash(data):
    isNew = data['postid']==''

    postid, pagetext, time = sql_posts.save_post({'postid':data['postid'],
                                          'userid':session['s_user'],
                                          'threadid':bash_threadid,
                                          'color': '',
                                          'pagetext': data['pagetext'],
                                         })

    if isNew:
        newshout = shouts.do_newshout(session['s_user'],'[arhibash]выложил(а) Архибаш![/arhibash]','1',-1,'')
        events_chat.emit_one_message('new', newshout)

        # newshout = shouts.do_newshout(1, '11111', '1', '-1')

    if postid>0:
        return {'postid':postid, 'time':time}
