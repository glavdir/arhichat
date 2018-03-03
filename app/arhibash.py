from flask import session
from app import socketio, sql_posts

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
    postid, pagetext = sql_posts.save_post({'postid':data['postid'],
                                          'userid':session['s_user'],
                                          'threadid':bash_threadid,
                                          'color': '',
                                          'pagetext': data['pagetext'],
                                         })
    return {'postid':postid}
