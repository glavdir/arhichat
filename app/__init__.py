async_mode = 'gevent'
message_queue = ''


# if async_mode == 'gevent':
#     from gevent import monkey
#     monkey.patch_all()
#     message_queue = 'redis://'

from flask import Flask
from flask_sqlalchemy   import SQLAlchemy
from flask_socketio     import SocketIO
from flask_redis        import FlaskRedis
from app import cbbcodes
import time

msgcount = 35
clients = {}
default_color = '#0000ff'

parser = cbbcodes.get_parser()
post_parser = cbbcodes.get_post_parser()
revision = time.time()

app = Flask(__name__)
app.config.from_object('config')
app.static_url_path='/static'
app.static_folder = './static'
app.template_folder='.'
db = SQLAlchemy(app)
redis = FlaskRedis(app,decode_responses=True)

from flask_cors import CORS
cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

from app import queries
last_messages = queries.get_last_messages(userid=-1)

socketio = SocketIO(app,
                    async_mode = async_mode,
                    ping_timeout=40,
                    ping_interval = 1,
                    transports=['websocket'],
                    policy_server=False,
                    logger = False,
                    message_queue=message_queue
                    )


from app import views, api, sql_characters, sql_posts, models, events_main, events_dialog, notes, events_character_edit, arhibash

db.create_all()
db.session.commit()
