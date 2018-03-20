from app import models, db, post_parser
from sqlalchemy import desc
import time

class arhpost(db.Model):
    postid       = db.Column(db.SmallInteger, primary_key = True)
    threadid     = db.Column(db.SmallInteger, primary_key = False)
    pagetext     = db.Column(db.Text, index = False, unique = False)
    userid       = db.Column(db.Integer)
    dateline     = db.Column(db.Integer)
    color        = db.Column(db.CHAR(16), index=False, unique=False)

    allowsmilie     = db.Column(db.SmallInteger, primary_key=False)
    showsignature   = db.Column(db.SmallInteger, primary_key=False)
    visible         = db.Column(db.SmallInteger, primary_key=False)


class arhpostparsed(db.Model):
    postid        = db.Column(db.SmallInteger, primary_key = True)
    pagetext_html = db.Column(db.Text, index = False, unique = False)
    dateline      = db.Column(db.Integer)

def get_lastposts(threadid, numposts=10, postid=0, direction='last'):
    query =  arhpost.query.filter_by(threadid=threadid)

    if direction!='next':
        query = query.order_by(desc("postid"))

    if direction=='next':
        query = query.filter(arhpost.postid>postid)
    elif direction=='prev':
        query = query.filter(arhpost.postid<postid)

    lastposts = query.limit(numposts).all()

    resPosts=[]
    for post in reversed(lastposts):
        pagetext = post_parser.format(post.pagetext)
        resPosts.append({'time':post.dateline,'userid':post.userid, 'postid':post.postid,'pagetext':pagetext, 'color':post.color})

    return resPosts

def get_posts(threads, mstart=0, count=25, search=''):
    qstring = 'SELECT ' \
              ' post.dateline,' \
              ' post.postid,' \
              ' post.threadid,' \
              ' post.userid,' \
              ' post.pagetext ' \
              'FROM arhpost post ' \
              'WHERE threadid in('+threads+') and post.pagetext like "%'+search+'%"' \
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


def get_posts_count(threads, search=''):
    qstring = 'SELECT COUNT(post.postid) AS posts_count FROM arhpost post WHERE threadid in('+threads+') and post.pagetext like "%'+search+'%"'
    return db.session.execute(qstring).first().posts_count

def get_post_number(threads, postid):
    return db.session.execute(
        'SELECT COUNT(post.postid) Count FROM arhpost post WHERE threadid in('+threads+') and postid<=%s' % (postid)).first().Count

    # query_text = 'SELECT SUM(1) Count FROM arhpost '
    # if search_str:
    #     query_text=query_text+' '+'WHERE s_shout like "%'+ search_str +'%"'
    #
    # res = db.session.execute(query_text).first().Count
    # if not res:
    #     res = 0
    #
    # return res
