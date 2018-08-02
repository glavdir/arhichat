# -*- coding: utf-8 -*-
import datetime
from flask import render_template, session, request, send_file
from app import app, queries, events_chat, api, socketio, revision

expire_date = datetime.datetime.now() + datetime.timedelta(days=365 * 10)


@app.route('/.well-known/acme-challenge/<string:filename>')
def cert(filename):
    return send_file('static/'+filename)


@app.route('/alert')
def alert():
    message = queries.get_last_message()
    events_chat.emit_one_message('new', message)
    return 'alert'


@app.route('/do_msg')
def do_msg():
    msg = request.args.get('msg')
    pmid = request.args.get('pmid')
    s_me = request.args.get('me')
    s_user = request.args.get('userid')

    if str(s_me) == '1':
        msg = '/me '+msg

    session['s_user'] = s_user
    events_chat.text({'msg': msg, 'pmid': pmid}, socketio)
    return 'ok'


@app.route('/')
def dc(transport='websocket'):
    api.auth()

    # if not session['s_user'] or str(session['s_user'])=='0':
    #     return render_template('templates/notlogin.html')

    font_size = request.args.get('font_size')
    style = request.args.get('style')
    transp = request.args.get('transport')

    if not font_size:
        font_size = ''

    if not style:
        style = ''

    if transp:
        transport = transp

    return render_template('dc.html',
                           font_size=font_size,
                           style=style,
                           revision=revision,
                           transport=transport,
                           active_users=queries.get_active_users(session['s_user']),
                           curuserid=session['s_user'],
                           opts=queries.get_options_by_userid(userid=session['s_user']))
