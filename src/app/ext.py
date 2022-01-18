import pymongo, redis
from rq import Queue
import cfg as config
from browserc import Browser

# Redis Queue
try:
    r_conn = redis.Redis(host=config.REDIS_HOSTNAME, port=config.REDIS_PORT)
    q = Queue(connection = r_conn)
    print('Redis Queue setup completed')
except Exception as e:
    raise e


# Selenium Browser
try:
    dctx = Browser()
    print('Browser has been initialized')
    if dctx.hsignin(config.STEAM_USERN, config.STEAM_PASSW) != False:
        print('User has been succesfully logged in')
except Exception as e:
    raise e


# MongoDB
try:
    mongo_client: pymongo.mongo_client.MongoClient = pymongo.MongoClient(config.MONGO_HOSTNAME, config.MONGO_PORT)
    print('Database connection established')
except Exception as e:
    raise e

