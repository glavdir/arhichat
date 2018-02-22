# -*- coding: utf-8 -*-

from app import app, queries, events_dialog, notes, shouts
from flask import session, request, json
from app import revision

def auth():
    session['s_user'] = request.cookies.get('bbuserid')
    if not session['s_user']:
        bbsession = request.cookies.get('bbsessionhash')
        if bbsession:
            session['s_user'] = str(queries.get_user_id_by_session(bbsession))

    session['name'] = 'myname'
    session['room'] = 'myroom'


@app.route('/api/last_messages/')
def last_messages():
    auth()
    return json.dumps(shouts.get_array_last_messages())

@app.route('/api/user_auth/')
def user_auth():
    auth()
    userinfo = queries.get_user_by_userid(session['s_user'])

    return json.dumps({
        'userid':session.get('s_user'),
        'timezoneoffset':userinfo.timezoneoffset,
        'opts': queries.get_options_by_userid(userid=session['s_user']),
        })

@app.route('/api/threads/')
def threads():
    threadlist = queries.get_threadlist(favorites=events_dialog.get_favorites())
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

@app.route('/api/archive/')
def archive():
    search_str  = request.args.get('search')
    page        = request.args.get('page')
    count       = request.args.get('count')

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

    total_msg_count = queries.get_messages_count(search_str)
    page_count = get_page_by_number(total_msg_count,count)

    mfinish = count*page
    mstart  = mfinish - count
    messages = list(queries.get_last_messages(mstart,mfinish,search_str).values())
    result = {'messages':messages,'page_count':page_count}

    return json.dumps(result)

@app.route('/api/posts_archive/')
def posts_archive():
    search      = request.args.get('search')
    page        = request.args.get('page')
    count       = request.args.get('count')
    threads     = request.args.get('threads')

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

    mstart  = count*(page - 1)

    result = queries.get_posts(threads=threads, mstart=mstart, count=count, search=search)

    result['page_count'] = get_page_by_number(result['posts_count'],count)

    return json.dumps(result)
