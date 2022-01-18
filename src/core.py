# https://gist.github.com/andxras/dcaef0e1ab996bffaed0d4cae6e9e3bd

import  time,\
        random,\
        requests,\
        sys

from bs4 import BeautifulSoup
from typing import List, Iterator, Dict
from json import dumps

from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

# local modules
import cfg as config
from concurrency import ThreadPool, lock
from browserc.misc import save_screenshot
from app.ext import q # redis queue
from app.ext import mongo_client # mongo db
from app.ext import dctx # selenium driver context

# global vars
retries = Retry(total = 0,
				backoff_factor = 0.1,
				status_forcelist = [ 500, 502, 503, 504, 429 ])

proxies: List[str] = []
queries: List[str] = []

query_results: List[dict] = []
total_count_records: Dict[str, int] = {}



""" Build url based on a query parameter
"""
build_u = lambda u, q: u.replace('$QUERY', q)


def initlst(f: str) -> None:
    """ Initialize list from text file
    """

    if f == 'proxies':
        fpath = config.PROXIES_PATH
    if f == 'queries':
        fpath = config.QUERIES_PATH 

    with open(fpath, 'r') as items:
        for i in items.readlines():
            j = i.strip()
            if f:
                globals()[f].append(j)

    return


def make_request(url: str) -> requests.models.Response:
    r_count = 0

    while True:
        if r_count > 3:
            r_count = 0
            time.sleep(60) # proxy might be blocked, sleep for half a min

        s = init_req_session() # initialize new proxy session
        res = s.get(url, timeout=10)

        if res.status_code == 200:
            break
        
        r_count += 1
        print(f'Requests count ({r_count}) on url {url} using proxy {s.proxies["http"]}')

    return res


def init_req_session() -> requests.sessions.Session:
    global proxies

    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=retries))
    addr: str = random.choice(proxies)

    s.headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0'
    }

    s.proxies = {
        'http': 'http://' + addr,
        'https': 'http://' + addr
    }

    return s


def get_extended_info(inspect_url: str) -> dict:
    """Get additional data using csgofloat api

    Args:
        inspect_url (str): inspect url

    Returns:
        dict: data from csgofloat api
    """
    url = config.U_CSGOFLOATAPI + inspect_url
    r = requests.get(url)
    data = r.json()

    return data['iteminfo']


def initial_query(q: str) -> None:
    global  query_results,\
            total_count_records

    url = build_u(config.U_QUERY, q)
    rq = make_request(url)
    res = rq.json()
    if res:
        if q not in total_count_records:
            total_count_records[q] = 0 # initialize key w 0 value

        #if res['total_count'] != total_count_records[q]:
        print(q, res['total_count'], '!=', total_count_records[q]) #TODO: ????

        total_count_records[q] = res['total_count']
        for r in res['results']:
            query_results.append({
                'hash_name': r['hash_name'],
                'sell_listings': r['sell_listings']
            })

    return


def get_item_listings(result: str) -> None:
    """ Get item listings given a result dict containing keys `hash_name` and `sell_listings`
    """

    sckio = SocketIO(message_queue = config.REDIS_URI_CONN)

    step: int  = 100 # max value
    total_count: int = result['sell_listings']
    start: int = 0 # valor inicial
    count: int = step if total_count > step else total_count # valor inicial

    # initial request with default `start` and `count` params

    while True:
        url = config.U_LISTINGS\
                .replace('$QUERY', result['hash_name'])\
                .replace('$START', str(start))\
                .replace('$COUNT', str(count))
        print('Fetching items in url:', url)
        rq = make_request(url)
        res = rq.json()

        if res['total_count']:
            total_count = res['total_count']

        if res['listinginfo']:
            for key in res['listinginfo']:
                if not mongo_client.market.listinginfo.find_one({ 'listingid': key }):
                    # for each item listings
                    data: dict = get_item_data(res['listinginfo'][key])

                    # notify user via telegram
                    send_telegram_message(f'Nuevo artículo publicado { data }\n')

                    if data:
                        is_match, buy = filter_weapon(data)
                        if is_match:
                            send_telegram_message(f'Se encontró un artículo solicitado, procediendo a comprar { data }\n')
                            if buy:
                                q.enqueue(handle_market_buy, data)
                            
                        jdata: str = dumps(data)
                        mongo_client.market.listinginfo.insert_one(data) # insert into db
                        try:
                            sckio.emit('steamdata', jdata)
                            print(jdata)
                        except Exception as e:
                            raise e
        else:
            break

        # eof request
        # e.g. https://steamcommunity.com/market/listings/730/Five-SeveN | Case Hardened (Field-Tested)/render/?query=&start=200&count=80&country=US&language=english&currency=1
        start = start + count if start + count < total_count else total_count
        time.sleep(
            random.randrange(3,8) # 2,5 s
        )

    return


def get_item_data(data: dict) -> dict:
    item = {}
    inspect_url: str = get_inspect_url(data)

    if not inspect_url:
        return item

    extdata: dict = get_extended_info(inspect_url)

    item['listingid'] = data['listingid']
    item['weapon_type'] = extdata['weapon_type']
    item['item_name'] = extdata['item_name']

    if 'sticker' not in item['weapon_type'].lower():
        item['wear'] = extdata['wear_name']
        item['img'] = extdata['imageurl']

        kphase:int = get_knife_phase(extdata['imageurl'])
        if kphase:
            item['item_name'].join(f' Phase {kphase}')
    else:
        item['wear'], item['img'] = '-', '-'

    item['paint_seed'] = extdata['paintseed']
    item['float'] = extdata['floatvalue']
    item['stickers'] = get_stickers(extdata)
    item['inspect_url'] = inspect_url
    item['last_seen'] = time.strftime('%D %H:%M:%S')
    item['price'] = get_price(data)
    item['action_buy'] = get_buymarket_script(data)
    item['hash_name'] = extdata['full_item_name']


    return item


def get_knife_phase(s: str) -> int or None:
    idx = s.find('phase')
    if idx != -1:
        return int(s[idx+5:][:1])

    return


def get_buymarket_script(data: dict) -> str:
    t_script = f'javascript:BuyMarketListing(\'listing\', %listingid%, %appid%, %contextid%, %id%)'
    listingid = data['listingid']
    appid = data['asset']['appid']
    contextid = data['asset']['contextid']
    _id = data['asset']['id']
    
    try:
        s = t_script\
                .replace('%listingid%', listingid)\
                .replace('%appid%', str(appid))\
                .replace('%contextid%', contextid)\
                .replace('%id%', _id)
    except Exception as e:
        raise e

    return s


def get_price(data: dict) -> int:
    try:
        converted_price = data['converted_price']
        converted_fee = data['converted_fee']
        _p = str(converted_price + converted_fee)
        price = '$' +_p[:-2] + '.' + _p[-2:]
    except:
        return None

    return price


def get_inspect_url(data: dict) -> str:
    inspect_url = ''

    listingid: str = data['listingid']

    try:
        assetid: str = data['asset']['id']
        link: str = data['asset']['market_actions'][0]['link']
    except:
        return inspect_url

    try:
        inspect_url =   link\
                        .replace('%listingid%', listingid)\
                        .replace('%assetid%', assetid)
    except Exception as e:
        raise e

    return inspect_url


def get_stickers(data: dict) -> List[str]:
    stickers = []

    if (data['stickers']):
        for i in data['stickers']:
            stickers.append(i['name'])

    return stickers


def update_listinginfo(test=False) -> None:
    global  query_results,\
            queries

    while True:

        # init user-input listings
        initlst('proxies')
        initlst('queries')

        p = ThreadPool(config.NTHREADS)

        # get a hash_name list based on query results
        for query in queries:
            p.add_task(initial_query, query)

        p.wait_completion()

        p = ThreadPool(config.NTHREADS if len(query_results) > config.NTHREADS else len(query_results))

        print('query_results:', query_results)

        # get listings based on hash_name list
        for query in query_results:
            p.add_task(get_item_listings, query)

        p.wait_completion()

        if test != False:
            return

        print('Update task finished, retrying in 2s ...')
        time.sleep(2)


def handle_market_buy(data: Dict[str, str]):

    sckio = SocketIO(message_queue = config.REDIS_URI_CONN)

    if data['hash_name']:
        try:
            url = build_u(config.U_LISTINGS_HTML, data['hash_name'])
        except Exception as e:
            raise e

    try:
        if dctx.hpurchase_item(url, data['action_buy']) != False:
            sckio.emit("action_buy_response', f'The purchase of the item {data['hash_name']} has been successful")
            # save to database
            mongo_client.market.purchases.insert_one(data)
    except Exception as e:
        print('There was an error trying to purchase item:', e)
        sckio.emit("action_buy_response', f'The purchase of the item {data['hash_name']} has failed")

    return


def get_listinginfo() -> List[dict]:
    """ Returns listinginfo last 10 records from database
    """

    try:
        res: List[dict] = mongo_client.market.listinginfo.find().limit(50).sort([('$natural', -1)])
    except Exception as e:
        raise e
    
    return list(res)


def retrieve_filters() -> List[dict]:
    flst = []

    try:
        flst = mongo_client.market.filters.find()
    except Exception as e:
        raise e

    return list(flst)


def update_filters(f: dict) -> List[str]:
    flst = []

    print('filter =>',f)

    try:
        mongo_client.market.filters.insert_one(f)
        flst = retrieve_filters()
        print('filters', flst)
    except Exception as e:
        raise e

    return flst


def retrieve_purchases() -> List[dict]:
    plst = []

    try:
        plst = mongo_client.market.purchases.find().limit(10).sort([('$natural', -1)])
    except Exception as e:
        raise e

    return list(plst)


def retrieve_proxies() -> List[str]:
    plst = []

    try:
        with open(config.PROXIES_PATH, 'r') as f:
            for i in f.readlines():
                addr = i.strip()
                if addr:
                    plst.append(addr)
    except Exception as e:
        raise e
    
    return plst


def update_proxies(proxies: str = "") -> List[str]:   
    plst = []

    print(type(proxies), proxies)

    try:
        with open(config.PROXIES_PATH, 'w') as f:
            for p in proxies.split():
                f.write(p + '\n')

        plst: List[str] = retrieve_proxies()
    except Exception as e:
        raise e

    return plst


def retrieve_querystrings() -> List[str]:
    qlst = []

    try:
        with open(config.QUERIES_PATH, 'r') as f:
            for i in f.readlines():
                addr = i.strip()
                if addr:
                    qlst.append(addr)
    except Exception as e:
        raise e
    
    return qlst


def update_querystrings(queries: str = "") -> List[str]:
    qlst = []

    print(type(queries.split(',')), queries.split(','))

    try:
        with open(config.QUERIES_PATH, 'w') as f:
            for q in queries.split(','):
                f.write(q.strip() + '\n')

        qlst: List[str] = retrieve_proxies()
    except Exception as e:
        raise e

    return qlst


def send_telegram_message(data: str) -> dict:
    url = f'https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage?chat_id={config.TELEGRAM_CHATID}&parse_mode=Markdown&text={data}'

    r = make_request(url)

    return r.json()


def restartListings() -> None:
    print(f"Scheduler started at {time.strftime('%D %H:%M:%S')} ...")
    try:
        scheduler = BlockingScheduler()
        scheduler.add_job(lambda: mongo_client.market.listinginfo.drop(), IntervalTrigger(minutes=60 * 24 * 7))
        scheduler.start()
    except (KeyboardInterrupt):
        print('SIGTERM')


def filter_weapon(item: dict) -> (bool, bool):
    filters: List[dict] = retrieve_filters()

    for f in filters:
        if  item["weapon_type"] == f["weapon_type"]    and \
            item["item_name"] == f["item_name"]  and \
            item["wear"] == f["wear"]   and \
            item["price"] >= f["prange"]['f'] and item["price"] <= f["prange"]['t'] and \
            item["float"] >= f["frange"]['f'] and item["float"] <= f["frange"]['t']:

            if not f["stickers"]:
                return True, f["buy"]
            elif any(s in item["stickers"] for s in f["stickers"]):
                return True, f["buy"]

    return False, False

