import requests
from app import db

forumMain = 81
forumArchive = 95

class arhforum(db.Model):
    forumid             = db.Column(db.SmallInteger, primary_key = True)
    styleid             = db.Column(db.SmallInteger)
    title               = db.Column(db.String(100))
    title_clean         = db.Column(db.String(100))
    description         = db.Column(db.String(100))
    description_clean   = db.Column(db.String(100))
    options             = db.Column(db.Integer)
    showprivate         = db.Column(db.SmallInteger)
    displayorder        = db.Column(db.SmallInteger)
    daysprune           = db.Column(db.SmallInteger)
    childlist           = db.Column(db.String(1000), index = False, unique = False)
    parentid            = db.Column(db.SmallInteger)
    parentlist          = db.Column(db.String(100))
    defaultsortfield    = db.Column(db.String(100))
    defaultsortorder    = db.Column(db.String(100))

class arhthread(db.Model):
    threadid     = db.Column(db.SmallInteger, primary_key = True)
    forumid      = db.Column(db.SmallInteger, primary_key = False)
    title        = db.Column(db.String(100), index = False, unique = False)


def get_thread_title(dialog_id):
    thread_title = ''
    thread = arhthread.query.filter_by(threadid=dialog_id).first()
    if thread:
        thread_title = thread.title
    return thread_title

def get_threadlist(favorites=[]):
    keys = {'forumMain':forumMain,'forumArchive':forumArchive}

    forums = db.session.execute('SELECT childlist FROM arhforum WHERE forumid IN (%(forumMain)s,%(forumArchive)s)'%keys).fetchall()

    childlist = ''
    for forum in forums:
        if childlist!='':
            childlist = childlist+','
        childlist = childlist+forum.childlist

    keys['childlist'] = childlist

    if not favorites or favorites == '[]':
        favorites_str = '0'
    else:
        favorites_str = ','.join(favorites)

    keys['favorites'] = favorites_str
    threadlist = db.session.execute('SELECT'
                                    '   threadid,'
                                    '   forumid,'
                                    '   title,'
                                    '   threadid IN (%(favorites)s) as isFav '
                                    'FROM '
                                    '    arhthread '
                                    'WHERE '
                                    '    forumid IN (%(childlist)s)  '
                                    'ORDER BY '
                                    '   isFav DESC,threadid DESC'%keys).fetchall()
    threads = []

    for thread in threadlist:
        threads.append({'threadid':thread.threadid, 'title':thread.title, 'isFav':thread.isFav!=0, 'forumid':thread.forumid})

    return threads


def get_forums():
    keys = {'forumMain': forumMain, 'forumArchive': forumArchive}
    forumlist =  db.session.execute('SELECT '
                                    '	forumid,'
                                    '   parentid,'
                                    '	title,'
                                    '   displayorder,'
                                    '   forumid IN (%(forumMain)s,%(forumArchive)s) AS isRoot,'
                                    '   IF (forumid IN (%(forumMain)s,%(forumArchive)s) , forumid, parentid) AS forumPart                               '
                                    'FROM'
                                    '	arhforum '
                                    'WHERE'
                                    '	parentid IN (%(forumMain)s,%(forumArchive)s) OR forumid IN (%(forumMain)s,%(forumArchive)s)'
                                    'ORDER BY'
                                    '	forumPart,'
                                    '   isRoot DESC,'
                                    '   displayorder'%keys).fetchall()

    forums = {}

    for forum in forumlist:
        forums[forum.forumid] = forumDict(forum)

    return forums

def forumDict(forum):
    return {'forumid':forum.forumid,
                        'parentid': forum.parentid,
                        'title':forum.title,
                        'isRoot':forum.forumid==forumMain or forum.forumid==forumArchive,
                        'threads':[],
                        'isMain':forum.forumid==forumMain,
                        'show':False
                       }


def save_forum(data):
    isNew = data['forumid']=='' or data['forumid']==0

    if isNew:
        forum = arhforum()
        forum.styleid             = 0
        forum.options             = 97991 #не знаю что это за айдишник, но во всех разделах он есть
        forum.showprivate         = 0
        forum.displayorder        = 1
        forum.daysprune           = -1
        forum.parentid            = forumMain
        forum.parentlist          = str(forumMain)
        forum.defaultsortfield    = 'lastpost'
        forum.defaultsortorder    = 'desc'
    else:
        forum = arhforum().query.filter_by(forumid=data['forumid']).first()
        forum.parentid = data['parentid']

    forum.title = data['title']
    forum.title_clean = data['title']

    if isNew:
        db.session.add(forum)

    db.session.commit()

    reqText = "http://arhimag.org/forum_rebuild.php?forumid=%s"%forum.forumid
    req = requests.get(reqText, headers={'Content-Type': 'application/json'})

    result = forumDict(forum)

    result['isNew'] = isNew

    return result
