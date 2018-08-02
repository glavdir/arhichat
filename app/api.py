# -*- coding: utf-8 -*-

from flask import session, request, json
from app import app, queries, sql_posts, sql_threads, events_dialog, notes, shouts
from app import revision

def auth(userid = '0'):
    if userid!='0':
        session['s_user'] = userid
    else:
        userid = request.cookies.get('bbuserid')
        if not userid:
            bbsession = request.cookies.get('bbsessionhash')
            if bbsession:
                userid = str(queries.get_user_id_by_session(bbsession))

        bbpassword = request.cookies.get('bbpassword')
        user = queries.get_user_by_userid(userid)

        if user!=None and queries.md5(user.password)==bbpassword:
            session['s_user'] = userid
        else:
            session['s_user'] = '0'

    session['name'] = 'myname'
    session['room'] = 'myroom'

@app.route('/api/do_auth/', methods=["POST"])
def do_auth():
    username = request.args.get('username')
    password = request.args.get('userpass')
    authdata = queries.login(username,password)

    if authdata['userid']!=0:
        auth(authdata['userid'])

    return json.dumps(authdata)

@app.route('/api/user_auth/')
def user_auth():
    auth()

    if session['s_user']!='0':
        userinfo = queries.get_user_by_userid(session['s_user'])
        timezoneoffset = userinfo.timezoneoffset
    else:
        timezoneoffset = 0

    return json.dumps({
        'userid':session.get('s_user'),
        'timezoneoffset':timezoneoffset,
        'opts': queries.get_options_by_userid(userid=session['s_user']),
        })

@app.route('/api/last_messages/')
def last_messages():
    auth()
    return json.dumps(shouts.get_array_last_messages())

@app.route('/api/users/')
def users():
    ids = request.args.get('userid')

    res = []
    if ids:
        for userid in ids.split(','):
            res.append({'userid':userid, 'userlook':queries.get_userlook_byid(userid)})

    return json.dumps(res)

@app.route('/api/threads/')
def threads():
    threadlist = sql_threads.get_threadlist(favorites=events_dialog.get_favorites())
    last_thread = events_dialog.get_last_thread()

    if str(last_thread)=='0' and len(threadlist)>0:
        last_thread = threadlist[0]['threadid']

    result = {'threads': threadlist,
              'threadid': last_thread}

    return json.dumps(result)

def get_page_by_number(number,count):
    return round(float(number)/count + 0.5)

@app.route('/api/get_note/')
def get_note():
    note = request.args.get('note')
    return notes.get_note_text(note)

@app.route('/api/to_notes/',methods=['POST'])
def to_notes():
    id = request.args.get('id')
    text = request.args.get('text')

    if id and str(id)!='0':
        notes.add_to_note(id,text)
        return 'ok'
    else:
        return 'Не заполнен id заметки'


@app.route('/api/archive/')
def archive():
    search_str  = request.args.get('search')
    page        = request.args.get('page')
    count       = request.args.get('count')
    pmid        = request.args.get('pmid')
    sid         = request.args.get('sid')

    if not search_str:
        search_str=''

    try:
        page = int(page)
    except:
        page = 1

    try:
        count = int(count)
    except:
        count = 100

    if count>1000:
        count = 1000

    total_msg_count = queries.get_messages_count(search_str,session['s_user'],pmid)
    page_count = get_page_by_number(total_msg_count,count)

    if sid:
        sid_number = queries.get_sid_number(sid,session['s_user'],pmid)
        page = get_page_by_number(total_msg_count-sid_number,count)

    mfinish = count*page
    mstart  = mfinish - count
    messages = list(queries.get_last_messages(mstart,mfinish,search_str,session['s_user'],pmid).values())
    result = {'messages':messages,'page_count':page_count, 'page':page}

    return json.dumps(result)

@app.route('/api/archive_pmids/')
def archive_pmids():
    return json.dumps(queries.get_pm_users(session['s_user']))

@app.route('/api/posts_archive/')
def posts_archive():
    search      = request.args.get('search')
    page        = request.args.get('page')
    count       = request.args.get('count')
    threads     = request.args.get('threads')
    postid      = request.args.get('postid')

    try:
        page = int(page)
    except:
        page = 1

    try:
        count = int(count)
    except:
        count = 50

    if not threads:
        threads = '0'

    if not search:
        search = ''

    total_post_count = sql_posts.get_posts_count(threads, search)

    if postid:
        post_number = sql_posts.get_post_number(threads, postid)
        page = get_page_by_number(post_number,count)

    mstart  = count*(page - 1)

    result = sql_posts.get_posts(threads=threads, mstart=mstart, count=count, search=search)

    result['page_count'] = get_page_by_number(total_post_count,count)
    result['page'] = page

    # print(page)

    return json.dumps(result)
