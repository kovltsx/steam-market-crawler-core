from os.path import abspath
from decouple import config

# GENERAL
NTHREADS = 50
MAKE_REQ_DELAY = 1
QUERIES_PATH    = abspath('queries.txt')
PROXIES_PATH    = abspath('proxies.txt')
LOGS_PATH       = abspath('logs/')

# FLASK_SOCKETIO
FSCKIO_EVENT_HANDLER = 'gevent'

# SELENIUM
HEADLESS = True
NT_DRIVERPATH       = abspath('chromedriver.exe')
LINUX_DRIVERPATH    = abspath('chromedriver')
NT_BINARYPATH       = abspath('chromium/chrome.exe')
LINUX_BINARYPATH    = abspath('chromium/chrome')
USERDATA_PATH       = abspath('userdata')

# FLASK
FLASK_SECRET_KEY = 'Topsy-Krettz'

# MONGODB
DB_NAME         = 'steam_market_bot'
MONGO_HOSTNAME  = 'localhost'
MONGO_PORT      = 27017
MONGO_URI_CONN  = f'mongodb://{MONGO_HOSTNAME}:{MONGO_PORT}/{DB_NAME}'

# REDIS
REDIS_HOSTNAME  = 'localhost'
REDIS_PORT      = 6379
REDIS_URI_CONN  = f'redis://{REDIS_HOSTNAME}:{REDIS_PORT}'

# URLS
# U_QUERY         = 'https://steamcommunity.com/market/search/render/?query=$QUERY&start=1&count=100&search_descriptions=0&sort_column=price&sort_dir=desc&appid=730&norender=1'
U_QUERY         = 'https://steamcommunity.com/market/search/render/?query=$QUERY&search_descriptions=0&sort_column=price&sort_dir=desc&appid=730&norender=1'
U_LISTINGS      = 'https://steamcommunity.com/market/listings/730/$QUERY/render/?query=&start=$START&count=$COUNT&country=US&language=english&currency=1'
U_LISTINGS_HTML = 'https://steamcommunity.com/market/listings/730/$QUERY/?query=&start=0&count=100'
U_CSGOFLOATAPI  = 'https://api.csgofloat.com/?url='
U_STEAM_SIGNIN  = 'https://steamcommunity.com/login'

# STEAM
STEAM_USERN = config('USERN')
STEAM_PASSW = config('PASSW')

# TELEGRAM
TELEGRAM_TOKEN  = config('TELEGRAM_TOKEN')
TELEGRAM_CHATID = config('TELEGRAM_CHATID')
