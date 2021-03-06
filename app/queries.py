# -*- coding: utf-8 -*-
# pylint:disable-msg=E1101
import time
import json
from collections import OrderedDict
import hashlib

from sqlalchemy import desc
from sqlalchemy import or_
from sqlalchemy import and_

from app import models
from app import msgcount
from app import parser
from app import clients
from app import redis
from app import db
from app.matfilter import matfilter
from app import usernames

grouptags = []

def get_user_id_by_session(bbsession):
    session = models.arhsession.query.filter_by(sessionhash=bbsession).first()
    if session:
        return session.userid
    return 0

def set_session_by_userid(userid):
    # pylint:disable-msg=E1101
    sessionhash = md5(str(time.time()))

    newsession = models.arhsession()
    newsession.userid = userid
    newsession.sessionhash = sessionhash

    db.session.add(newsession)
    db.session.commit()

    return sessionhash

def md5(mystring):
    return hashlib.md5(mystring.encode('utf-8')).hexdigest()

def login(username,password):
    user = get_user_by_username(username)
    passwordhash = md5(md5(password)+user.salt)

    result = {}

    if user.password == passwordhash:
        result['userid'] = user.userid
        result['passwordhash'] = md5(passwordhash)
    else:
        result['userid'] = 0
        result['passwordhash'] = ''

    return result

def userlook(user):
    if user==None:
        return "Anonymous"
    else:
        if user.userid in usernames:
            return usernames[user.userid]

        groupid = user.displaygroupid

        if user.displaygroupid==0:
            groupid = user.usergroupid

        group = models.arhusergroup.query.get(groupid)

        if user.yahoo:
            username = user.yahoo
        else:
            username = user.username

        # username = trs.to_eo(username)

        res = group.opentag + username + group.closetag

        usernames[user.userid] = res

        return res

def get_unread_pms(s_user):
    return redis.hgetall('pm_%s' % s_user)

def get_active_users(s_user=0):
    # active_users = models.arhuser.query.filter(models.arhuser.lastactivity>time.time()-3600/2).all() #3600/2
    #
    # for usrid in clients.values():
    #     if usrid and usrid!=0:
    #         active_users.append(get_user_by_userid(usrid))
    #
    # # unread_pms = get_unread_pms(s_user)
    # # for key in unread_pms:
    #
    # res = [{'userid':'1', 'userlook':str(userlook(get_user_by_userid(1))), 'online':True, 'unread':False}]
    # usr_dbl = []
    #
    # for usr in active_users:
    #     if usr:
    #         if not usr in usr_dbl and usr.userid!=1:
    #             usr_dbl.append(usr)
    #             # is_unread = ('usr_%s' % usr.userid) in unread_pms
    #             try:
    #                 res.append({'userid':str(usr.userid), 'userlook':userlook(usr),'online':True, 'unread':False})
    #             except:
    #                 pass

    res = [{'userid':'1', 'userlook':str(userlook(get_user_by_userid(1))), 'online':True, 'unread':False}]
    usr_dbl = ['1']

    for usrid in clients.values():
        if usrid and str(usrid)!='0' and not str(usrid) in usr_dbl:
            res.append({'userid': str(usrid), 'userlook': userlook(get_user_by_userid(usrid)), 'online': True, 'unread': False})
            usr_dbl.append(str(usrid))

    return res

def get_user_by_userid(userid):
    if userid and str(userid)!='0':
        return models.arhuser.query.get(userid)
    # else:
    #     return {'userid':0, 'timezoneoffset':0, 'password':'pass'}

def get_user_by_username(username):
    if username:
        return models.arhuser.query.filter_by(username=username).first()

def get_userlook_byid(userid):
    if userid==-1:
        return ''

    if userid:
        return userlook(get_user_by_userid(userid))
    else:
        return 'anonimous'

def get_username_byid(userid):
    if userid == -1:
        return ''

    if userid:
        return get_user_by_userid(userid).username
    else:
        return 'anonimous'

def get_pm_users(userid):
    # pylint:disable-msg=E1101
    result = db.session.execute('SELECT distinct s_private AS userid '
                                'FROM  arhinfernoshout  WHERE  s_user = %s and s_private<>-1 '
                                'UNION   '
                                'SELECT distinct s_user AS userid    '
                                'FROM  arhinfernoshout  WHERE  s_private = %s and s_user<>-1 ' % (userid,userid)).fetchall()
    users = []
    for user in result:
        users.append({'userid': user.userid, 'userlook': get_userlook_byid(user.userid)})

    return users



def get_adminpermissions(userid):
    user = models.arhuser.query.get(userid)
    adminpermissions = False
    group = models.arhusergroup.query.get(user.usergroupid)

    if group.adminpermissions>0:
        adminpermissions = True

    return adminpermissions


def get_s_color(user):
    s_color = 'black'

    if user:
        if user.shoutuser:
           s_color = user.shoutuser[0].s_color

    return s_color

def msg(shout,original,action=''):
    s_color = 'black'
    if shout.user:
        if shout.user.shoutuser:
            s_color = shout.user.shoutuser[0].s_color

    s_shout = shout.s_shout
    # s_color = get_s_color(shout.user)

    if not original:
        s_shout = parser.format(s_shout)
        mats = matfilter(s_shout)
        if mats:
            for mat in mats:
                s_shout = s_shout.replace(mat, "<span class='cens'>[цензура]</span><span class='mat'>%s</span>"%(mat))

    # s_shout = trs.to_eo(s_shout)

    return {'msg': s_shout, 's_user':str(shout.s_user), 'user': userlook(shout.user), 'sid': shout.sid, 'me': shout.s_me, 'time': shout.s_time, 'color': s_color, 'pmid':shout.s_private, 'pmuser':get_username_byid(shout.s_private)}

def get_last_messages(mstart=0,mfinish=msgcount,search_str='',userid=0, pmid=-1):
    # if not search_str:
    #     shouts = models.arhinfernoshout.query.filter((models.arhinfernoshout.s_private==-1)|(models.arhinfernoshout.s_private==userid)|(models.arhinfernoshout.s_user==userid)).order_by(desc("sid"))[mstart:mfinish]
    # else:
    #     shouts = models.arhinfernoshout.query.filter_by(s_private=-1).filter(models.arhinfernoshout.s_shout.like('%'+ search_str +'%')).order_by(desc("sid"))[mstart:mfinish]

    query = models.arhinfernoshout.query

    if str(pmid)=='-1':
        query = query.filter_by(s_private=-1)
    else:
        query = query.filter(or_(and_(models.arhinfernoshout.s_user == userid, models.arhinfernoshout.s_private == pmid),
                                 and_(models.arhinfernoshout.s_user == pmid, models.arhinfernoshout.s_private == userid)))

    if search_str:
        query = query.filter(models.arhinfernoshout.s_shout.like('%'+ search_str +'%'))

    shouts = query.order_by(desc("sid"))[mstart:mfinish]
    shouts.reverse()
    # msgs = []
    # for shout in shouts:
    #     msgs.append(msg(shout, False))

    msgs = OrderedDict()
    for shout in shouts:
        msgs[shout.sid]=(msg(shout, False))
        # msgs.append(msg(shout, False))

    return msgs

def get_last_message():
    return models.arhinfernoshout.query.filter_by().order_by(desc("sid")).first()

def pmid_filter(userid,pmid):
    if str(pmid)=='-1':
        return 's_private = "-1"'
    else:
        return '(s_private = "%(pmid)s" and s_user="%(userid)s") or (s_user = "%(pmid)s" and s_private="%(userid)s")'%{'pmid':pmid,'userid':userid}

def get_messages_count(search_str='',userid=0, pmid=-1):
    query_text = 'SELECT SUM('+pmid_filter(userid,pmid)+') Count FROM arhinfernoshout'

    if search_str:
        query_text=query_text+' '+'WHERE s_shout like "%'+ search_str +'%"'

    res = db.session.execute(query_text).first().Count
    if not res:
        res = 0

    return res

def get_messages(userid, pmid, sid=0):
    if pmid==-1:
        qfilter = or_(models.arhinfernoshout.s_private == -1)
    else:
        qfilter = or_(and_(models.arhinfernoshout.s_user == userid, models.arhinfernoshout.s_private == pmid),
                      and_(models.arhinfernoshout.s_user == pmid, models.arhinfernoshout.s_private == userid))

    if sid!=0:
        qfilter = and_(qfilter, models.arhinfernoshout.sid<sid)

    query = models.arhinfernoshout.query

    shouts = query.filter(qfilter).order_by(desc("sid")).limit(msgcount).all()#[0:msgcount]
    shouts.reverse()

    msgs = []
    for shout in shouts:
        msgs.append(msg(shout, False))
    return msgs

def get_pm_by_mpid(userid, pmid):
    return {'msgs': get_messages(userid,pmid)}

def find_shout_by_sid(sid):
    return models.arhinfernoshout.query.filter_by(sid=sid).first()

def find_thread_by_threadid(threadid):
    return models.arhthread.query.filter_by(threadid=threadid).first()

def find_thread_by_postid(postid):
    try:
        return db.session.execute('select threadid from arhpost where postid=%s' % (postid)).first()
    except:
        return 0

def get_message_by_sid(sid,original):
    return True, msg(find_shout_by_sid(sid), original)


def get_sid_number(sid,userid=0, pmid=-1):
    return db.session.execute('SELECT SUM(('+pmid_filter(userid,pmid)+') and sid<=%s) Count FROM arhinfernoshout' % (sid)).first().Count

def get_options_by_userid(userid):
    options = {'transport_switch':False,
               'use_polling': False,
               'use_kong': True,
               'show_kong': False,
               'show_img': False,
               'censor': True,
               'style':'default',
               # 'font_size':16,
               'all_styles':['default','dragon', 'oceanzero', 'dragon_old'],
               's_color': get_s_color(get_user_by_userid(userid))}

    store_options = models.usersettings.query.filter_by(userid=userid).first()
    if store_options:
        if store_options.settings:
            options_keys = json.loads(store_options.settings)
            for key in options_keys:
                if key in options:
                    options[key] = options_keys[key]

    return options

def save_options(options,userid):
    update_shouts = False

    save_options = models.usersettings.query.filter_by(userid=userid).first()

    if not save_options:
        save_options = models.usersettings()
        db.session.add(save_options)

    save_options.userid = userid

    if 'all_styles' in options:
        del options['all_styles']

    save_options.settings = json.dumps(options)
    db.session.commit()
    arhinfernoshoutuser = models.arhinfernoshoutusers.query.filter_by(s_user=userid).first()
    if arhinfernoshoutuser.s_color != options['s_color']:
        arhinfernoshoutuser.s_color = options['s_color']
        db.session.commit()
        update_shouts = True

    return update_shouts

#
# def get_threadsettings_by_threadid(threadid):
#     settings = {'num_posts': 11}
#
#     store_settings = models.threadsettings.query.filter_by(threadid=threadid).first()
#     if store_settings:
#         if store_settings.settings:
#             settings_keys = json.loads(store_settings.settings)
#             for key in settings_keys:
#                 if key in settings:
#                     settings[key] = settings_keys[key]
#
#     return settings
#
# def save_threadsettings(options,threadid):
#     save_options = models.threadsettings.query.filter_by(threadid=threadid).first()
#
#     if not save_options:
#         save_options = models.threadsettings()
#         db.session.add(save_options)
#
#     save_options.threadid = threadid
#     save_options.settings = json.dumps(options)
#     db.session.commit()
