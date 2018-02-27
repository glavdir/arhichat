from app import db
from sqlalchemy.dialects.mysql import INTEGER
from app import sql_characters
import enum
# ROLE_USER = 0
# ROLE_ADMIN = 1

class arhuser(db.Model):
    userid   = db.Column(db.Integer, primary_key = True)
    usergroupid     = db.Column(db.SmallInteger, db.ForeignKey('arhusergroup.usergroupid'))
    displaygroupid  = db.Column(db.SmallInteger, db.ForeignKey('arhusergroup.usergroupid'))
    membergroupids  = db.Column(db.String)
    lastactivity    = db.Column(db.Integer, index = False, unique = False)
    username = db.Column(db.String(100), index = True, unique = True)
    shouts = db.relationship('arhinfernoshout', backref='user', lazy='dynamic')
    yahoo = db.Column(db.String(100), index = False, unique = False)
    timezoneoffset    = db.Column(db.SmallInteger, index = False, unique = False)

    def __repr__(self):
        return u'<%r>' % (self.username)

class arhsession(db.Model):
    sessionhash = db.Column(db.CHAR(32), primary_key = True)
    userid     = db.Column(db.Integer)

class usersettings(db.Model):
    userid     = db.Column(db.Integer, primary_key = True)
    settings   = db.Column(db.Text, index=False, unique=False)
    #CREATE TABLE usersettings (userid INTEGER primary key, settings TEXT)

class threadsettings(db.Model):
    threadid   = db.Column(db.Integer, primary_key = True)
    settings   = db.Column(db.Text, index=False, unique=False)
    # CREATE TABLE threadsettings(threadid INTEGER primary key, settings TEXT)

class arhusergroup(db.Model):
    usergroupid   = db.Column(db.SmallInteger, primary_key = True)
    opentag       = db.Column(db.String(100), index = False, unique = False)
    closetag      = db.Column(db.String(100), index=False, unique=False)
    adminpermissions = db.Column(db.SmallInteger)
    # users         = db.relationship('arhuser', backref='group', lazy='dynamic')

class arhforum(db.Model):
    forumid     = db.Column(db.SmallInteger, primary_key = True)
    childlist   = db.Column(db.String(1000), index = False, unique = False)

class arhthread(db.Model):
    threadid     = db.Column(db.SmallInteger, primary_key = True)
    forumid      = db.Column(db.SmallInteger, primary_key = False)
    title        = db.Column(db.String(100), index = False, unique = False)

class arhpost(db.Model):
    postid       = db.Column(db.SmallInteger, primary_key = True)
    threadid     = db.Column(db.SmallInteger, primary_key = False)
    pagetext     = db.Column(db.Text, index = False, unique = False)
    userid       = db.Column(db.Integer)
    dateline     = db.Column(db.Integer)
    color        = db.Column(db.CHAR(16), index=False, unique=False)

    allowsmilie = db.Column(db.SmallInteger, primary_key=False)
    showsignature = db.Column(db.SmallInteger, primary_key=False)
    visible = db.Column(db.SmallInteger, primary_key=False)


class arhpostparsed(db.Model):
    postid        = db.Column(db.SmallInteger, primary_key = True)
    pagetext_html = db.Column(db.Text, index = False, unique = False)
    dateline      = db.Column(db.Integer)

class arhinfernoshoutusers(db.Model):
    s_user  = db.Column(db.SmallInteger, db.ForeignKey('arhuser.userid'), primary_key=True)
    s_color = db.Column(db.String(32), index =False, unique =False)
    users = db.relationship('arhuser', backref='shoutuser')

class arhinfernoshout(db.Model):
    sid         = db.Column(db.Integer, primary_key = True)
    s_user      = db.Column(db.SmallInteger, db.ForeignKey('arhuser.userid'), index=True, unique=False)
    s_time      = db.Column(db.Integer, index = False, unique = False)
    s_shout     = db.Column(db.Text,    index=False, unique=False)
    s_me        = db.Column(db.Enum('0', '1'), default='0')
    s_private   = db.Column(db.SmallInteger, index=True, unique=False)
    dialog_id   = db.Column(db.CHAR(16),     index=True, unique=False)

class dialogs(db.Model):
    id          = db.Column(db.Integer, primary_key = True)
    dialog_id   = db.Column(db.CHAR(16), index=True, unique=False)
    color       = db.Column(db.CHAR(16), index=False, unique=False)
    reply       = db.Column(db.Text,     index=False, unique=False)
    archive     = db.Column(db.Boolean,  index=True, unique=False)

class dialogs_users(db.Model):
    userid           = db.Column(db.Integer, primary_key = True)
    last_dialog_id   = db.Column(db.CHAR(16),   index=True,  unique=False)
    last_color       = db.Column(db.CHAR(16),   index=False, unique=False)
    dialogs_colors   = db.Column(db.Text,       index=False, unique=False)
    favorites        = db.Column(db.Text,       index=False, unique=False)


# CREATE TABLE IF NOT EXISTS notes (
# 	id int(10) unsigned NOT NULL AUTO_INCREMENT,
# 	title char(32),
# 	text TEXT,
# 	author int(10) unsigned,
#     private int(1) unsigned NOT NULL DEFAULT 0,
# 	PRIMARY KEY (id)
# )

class notes(db.Model):
    id      = db.Column(db.Integer,   primary_key = True)
    title   = db.Column(db.CHAR(32), index=False, unique=False)
    author  = db.Column(db.Integer,  index=False, unique=False)
    private = db.Column(db.Integer, index=False, unique=False)
    text    = db.Column(db.Text,     index=False, unique=False)



class CharacterThreadData(db.Model):
    __tablename__ = 'character_thread_data'
    id              = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    character_id    = db.Column(INTEGER(unsigned=True), db.ForeignKey('characters.id'), primary_key=True, nullable=False)
    thread_id       = db.Column(INTEGER(unsigned=True), primary_key=True, nullable=False) # cannot be foreign key because of database
    note_id         = db.Column(INTEGER(unsigned=True), db.ForeignKey('notes.id'), nullable=True)
    character_style = db.Column(db.Text(1024), index=False, unique=False)
    __table_args__ = (
        db.UniqueConstraint("character_id", "thread_id"),
    )


######################
# Выполнить это вручную, остальное должно подняться само

# CREATE TABLE `characters` (
#   `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
#   `name` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
#   `description` varchar(5000) COLLATE utf8_unicode_ci DEFAULT NULL,
#   `author` int(10) unsigned DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   UNIQUE KEY `id` (`id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

# CREATE TABLE `tags` (
#   `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
#   `name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
#   PRIMARY KEY (`id`),
#   UNIQUE KEY `id` (`id`),
#   UNIQUE KEY `name` (`name`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
