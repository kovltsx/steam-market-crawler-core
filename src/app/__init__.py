import cfg as config
from concurrency import ThreadPool

# monkey patching for `flask_socketio` using gevent
from gevent import monkey; monkey.patch_all()

from flask_socketio import SocketIO, emit
from flask import Flask
from flask_cors import CORS

from .ext import dctx,\
                 mongo_client

app = Flask(__name__)
app.config['SECRET_KEY'] = config.FLASK_SECRET_KEY
CORS(app)
sckio = SocketIO(
    app,
    message_queue = config.REDIS_URI_CONN,
    cors_allowed_origins = '*',
    async_mode = config.FSCKIO_EVENT_HANDLER
)


# infinite loop to update listinginfo
import core

# update listinginfo in the background
txUpdateListingInfo = ThreadPool(1)
txUpdateListingInfo.add_task(core.update_listinginfo)

# restart listinginfo in the background
txRestartListingInfo = ThreadPool(1)
txRestartListingInfo.add_task(core.restartListings)


# es necesario que se importen estos modulos locales desde este lugar para evitar error: circular import
from . import   views,\
                handlers
