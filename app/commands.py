# -*- coding: utf-8 -*-
import re
from random import randint
from app import queries, socketio
from flask import session

def add_new_shout(new_shouts, s_user, msg, s_me, s_private):
    new_shouts.append({'s_user':s_user,'msg':msg,'s_me':s_me,'s_private':s_private})

def roll(num_dice, num_edge):
    result = 0

    if num_dice==0 or num_edge==0:
        return 0

    result = ''

    for i in range(num_dice):
        # dice = ress
        dice = randint(1,num_edge)
        result = ''+result + str(dice)
        if i<num_dice-1:
            result = result + '-'
        # print dice

    return result

def fetch_dice(msg):
    num_dice = 0
    num_edge = 0

    matches = re.search('(^/dice) ([0-9]{1,5}) ([0-9]{1,1000})', msg)
    if matches:
        num_dice = int(matches.group(2))
        num_edge = int(matches.group(3))

    if not matches:
        matches = re.search('^(\d{1,5})d(\d{1,1000})', msg)
        if matches:
            num_dice = int(matches.group(1))
            num_edge = int(matches.group(2))

    if not matches:
        matches = re.search('^/ddd$', msg)
        if not matches:
            matches = re.search(u'^/ддд$', msg)
        if not matches:
            matches = re.search(u'^/lll', msg)
        if not matches:
            matches = re.search(u'^/ввв', msg)

        if matches:
            num_dice = 3
            num_edge = 12

    if not matches:
        matches = re.search('^/d$', msg)
        if not matches:
            matches = re.search(u'^/д$', msg)
        if not matches:
            matches = re.search(u'^/l', msg)
        if not matches:
            matches = re.search(u'^/в', msg)

        if matches:
            num_dice = 1
            num_edge = 12

    return matches, num_dice, num_edge

def fetch_pm(msg):
    matches = re.search('(^/pm) (.*)', msg)
    pmid = 0

    if matches:
        pmarg =  matches.group(2)
        pmuser = queries.get_user_by_userid(pmarg)

        if not pmuser:
            pmuser = queries.get_user_by_username(pmarg)

        if pmuser:
            pmid = pmuser.userid

    return matches,pmid

def command_pm(doshout, msg, new_shouts, callbacks):
    matches, pmid = fetch_pm(msg)

    if matches:
        doshout = False
        done = True
        # socketio.emit('open_private', {'pmid':pmid}, broadcast = False)
        callbacks.append({'call':'open_private','param':{'pmid':pmid}})
    else:
        done = False

    return done, doshout, msg, callbacks

def command_dice(doshout, msg, new_shouts, callbacks):
    matches, num_dice, num_edge = fetch_dice(msg)

    if matches:
        result   = roll(num_dice, num_edge)
        phrase = '[color=black]попробовал кинуть дайсы %sd%s и получил %s Радуйся,[/color] %s' % (num_dice,num_edge,result,str(queries.get_username_byid(session['s_user'])))
        add_new_shout(new_shouts, 1, phrase , '1', -1)
        doshout = False
        done = True
    else:
        done = False

    return done, doshout, msg, callbacks

def command_img(doshout, msg, callbacks):
    matches = re.search('(^/i) (.*)', msg)
    if matches:
        doshout = True
        done = True
        msg = '[img]%s[/img]'%(matches.group(2))
    else:
        done = False

    return done, doshout, msg, callbacks

def command_reload(doshout, msg, callbacks):
    if msg=='/do_reload':
        doshout = False
        done = True
        socketio.emit('do_reload')
    else:
        done = False

    return done, doshout, msg, callbacks

def fetch_command(doshout, msg, s_me, s_private):
    new_shouts = []
    callbacks = []

    done, doshout, msg, callbacks = command_dice(doshout, msg, new_shouts, callbacks)
    if done:
        return doshout, msg, new_shouts, callbacks

    done, doshout, msg, callbacks = command_pm(doshout, msg, new_shouts, callbacks)
    if done:
        return doshout, msg, new_shouts, callbacks

    done, doshout, msg, callbacks = command_img(doshout, msg, callbacks)
    if done:
        return doshout, msg, new_shouts, callbacks

    done, doshout, msg, callbacks = command_reload(doshout, msg, callbacks)
    if done:
        return doshout, msg, new_shouts, callbacks

    return doshout, msg, new_shouts, callbacks
