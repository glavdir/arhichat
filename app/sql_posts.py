from app import models, db, post_parser
from sqlalchemy import desc
from sqlalchemy import and_
import time

class arhpost(db.Model):
    postid       = db.Column(db.Integer, primary_key = True)
    threadid     = db.Column(db.SmallInteger, primary_key = False)
    pagetext     = db.Column(db.Text, index = False, unique = False)
    userid       = db.Column(db.Integer, db.ForeignKey('arhuser.userid'))
    dateline     = db.Column(db.Integer)
    color        = db.Column(db.CHAR(16), index=False, unique=False)

    allowsmilie     = db.Column(db.SmallInteger, primary_key=False)
    showsignature   = db.Column(db.SmallInteger, primary_key=False)
    visible         = db.Column(db.SmallInteger, primary_key=False)

    comments = db.relationship('post_comments', backref='post', lazy='joined')
    # user = db.relationship('arhuser', foreign_keys=userid, lazy='joined')

class post_comments(db.Model):
    postid       = db.Column(db.Integer, db.ForeignKey('arhpost.postid'))
    sid          = db.Column(db.SmallInteger, primary_key = True, unique = True)
    text         = db.Column(db.Text, index = False, unique = False)
    userid       = db.Column(db.Integer, db.ForeignKey('arhuser.userid'))
    dateline     = db.Column(db.Integer)
    color        = db.Column(db.CHAR(16), index=False, unique=False)
    user         = db.relationship('arhuser', foreign_keys=userid, lazy='joined')

class arhpostparsed(db.Model):
    postid        = db.Column(db.SmallInteger, primary_key = True)
    pagetext_html = db.Column(db.Text, index = False, unique = False)
    dateline      = db.Column(db.Integer)

def get_lastposts(threadid, numposts=10, postid=0, direction='last'):
    query =  arhpost.query.filter_by(threadid=threadid).filter_by(visible=1)

    if direction!='next':
        query = query.order_by(desc(arhpost.postid))

    if direction=='next':
        query = query.filter(arhpost.postid>postid)
    elif direction=='prev':
        query = query.filter(arhpost.postid<postid)

    lastposts = query.limit(numposts).all()

    resPosts=[]
    for post in reversed(lastposts):
        pagetext = post_parser.format(post.pagetext)
        comments = []
        for comm in post.comments:
            comments.append({'sid':comm.sid,
                             'userid': comm.userid,
                             'username': comm.user.username,
                             'text': comm.text,
                             'dateline': comm.dateline,
                             'color': comm.color
                             })
        resPosts.append({'time':post.dateline,'userid':post.userid, 'postid':post.postid,'pagetext':pagetext, 'color':post.color, 'comments':comments})

    return resPosts

def get_posts(threads, mstart=0, count=25, search=''):
    # query = arhpost.query
    # query = query.filter(and_(arhpost.threadid in (threads),arhpost.visible))
    #
    # if search:
    #     query = query.filter(arhpost.pagetext.like('%'+ search +'%'))
    #
    # lastposts = query.order_by("postid")[mstart:count]

    qstring = 'SELECT ' \
              ' post.dateline,' \
              ' post.postid,' \
              ' post.threadid,' \
              ' post.userid,' \
              ' post.pagetext ' \
              'FROM arhpost post ' \
              'WHERE threadid in('+threads+') and visible and post.pagetext like "%'+search+'%"' \
              'ORDER BY postid ' \
              'LIMIT '+str(mstart)+','+str(count)+''

    lastposts = db.session.execute(qstring).fetchall()
    resPosts=[]
    for post in reversed(lastposts):
        resPosts.append({'time':post.dateline,'userid':post.userid, 'postid':post.postid,'pagetext':post_parser.format(post.pagetext)})

    # qstring = 'SELECT COUNT(post.postid) AS posts_count FROM arhpost post WHERE threadid in('+threads+') and post.pagetext like "%'+search+'%"'
    # posts_count = db.session.execute(qstring).first().posts_count

    return {'posts':resPosts} #,'posts_count':posts_count

def save_post(data):
    isNew = data['postid']==''

    if isNew:
        post = arhpost()
        post.threadid   = data['threadid']
        post.userid     = data['userid']
        post.dateline   = int(time.time())
        post.allowsmilie = 1
        post.showsignature = 1
        post.visible = 1
    else:
        post = arhpost().query.filter_by(postid=data['postid']).first()

    post.pagetext = data['pagetext']
    post.color    = data['color']

    if isNew:
        db.session.add(post)

    db.session.commit()

    pagetext_html = post_parser.format(post.pagetext)

    return post.postid,pagetext_html,post.dateline

def del_post(data):
    post = arhpost().query.filter_by(postid=data['postid']).first()
    post.visible = 0
    db.session.commit()

    return data['postid']

def get_posts_count(threads, search=''):
    qstring = 'SELECT COUNT(post.postid) AS posts_count FROM arhpost post WHERE threadid in('+threads+') and post.pagetext like "%'+search+'%"'
    return db.session.execute(qstring).first().posts_count

def get_post_number(threads, postid):
    return db.session.execute(
        'SELECT COUNT(post.postid) Count FROM arhpost post WHERE threadid in('+threads+') and postid<=%s' % (postid)).first().Count


def save_comment(data):
    newcomment = post_comments()
    newcomment.postid   = int(data['postid'])
    newcomment.userid   = data['userid']
    newcomment.text     = data['text']
    newcomment.color    = data['color']
    newcomment.dateline = int(time.time())
    db.session.add(newcomment)
    db.session.commit()

    data['sid'] = newcomment.sid
    data['dateline'] = newcomment.dateline
    data['username'] = newcomment.user.username

    return newcomment.sid
