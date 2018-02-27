from app import queries, db
from sqlalchemy.dialects.mysql import INTEGER

CharacterTags = db.Table('character_tags', db.Model.metadata,
                          db.Column('tag_id', INTEGER(unsigned=True), db.ForeignKey('tags.id'), primary_key=True),
                          db.Column('character_id', INTEGER(unsigned=True), db.ForeignKey('characters.id'), primary_key=True)
                          )


class Tags(db.Model):
    __tablename__ = 'tags'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    characters = db.relationship('Characters', secondary=CharacterTags, lazy='subquery',
                                 back_populates='tags')


class Characters(db.Model):
    __tablename__ = 'characters'
    id              = db.Column(INTEGER(unsigned=True), primary_key=True, unique=True, autoincrement=True)
    name            = db.Column(db.String(64), index=False)
    description     = db.Column(db.String(5000), index=False)
    author          = db.Column(INTEGER(unsigned=True), index=False)
    tags = db.relationship('Tags', secondary=CharacterTags, lazy='subquery',
                           back_populates='characters')

    def toDict(self):
        tags = []
        for t in self.tags:
            tags.append(t.name)
        d = {'id': self.id, 'name': self.name, 'description': self.description, 'author': self.author, 'tags': tags}
        return d

    def fromDict(self, data):
        if data['id'] is not None:
            self.id             = data['id']
        self.name           = data['name']
        self.description    = data['description']
        self.author         = data['author']
        self.tags = []
        for tn in data['tags']:
            self.tags.append(get_tag(tn))

    def __eq__(self, other):
        if self.id != other.id:
            return False
        if self.name != other.name:
            return False
        if self.name != other.name:
            return False
        if self.tags != other.tags:
            return False
         #no need to compare author
        return True


# functions

def get_all_tags():
    tags = Tags.query.order_by(Tags.name.asc()).all()
    return tags

def get_tag(tag_name):
    tag = Tags.query.filter_by(name=tag_name).first()
    if tag:
        return tag
    db.session.execute('INSERT IGNORE INTO tags SET  name = :name;', {'name': tag_name})
    db.session.commit()
    return Tags.query.filter_by(name=tag_name).first()


def get_character(character_id):

    record = Characters.query.get(character_id)
    result = record.toDict()
    user = queries.get_user_by_userid(result['author'])
    if user:
        result['author_name'] = user.username
    else:
        result['author_name'] = "[Автор неизвестен]"

    return result


def get_character_list():
    query = Characters.query.with_entities(Characters.name,
                                           Characters.id)
    result = query.all()
    return result


def write_character(character_dict):
    char_id = character_dict['id']
    exists = False
    char = None

    if char_id is not None:
        char = Characters.query.get(char_id)

    if char is None:
        char = Characters()
    else:
        exists = True

    char.fromDict(character_dict)
    if not exists:
        db.session.add(char)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        db.session.flush()  # for resetting non-commited .add()
        return None

    return char.id




def delete_character(character_id):
    if character_id is None:
        return False

    character = Characters.query.get(character_id)
    db.session.delete(character)
    db.session.commit()
    character = Characters.query.get(character_id)
    return character is None


def find_characters(filters):
    filter_array = []
    if filters:
        name = filters['name'].lower()
        tags = filters['tags']
        if name:
            filter_array.append(Characters.name.like(name+'%'))
        if tags:
            filter_array.append(Characters.tags.any(Tags.name.in_(tags)))

    return db.session.query(Characters).filter(*filter_array).all()

def count_values(model):
    return db.session.execute( db.session.query(model).statement.with_only_columns([db.func.count()]).order_by(None)).scalar()


