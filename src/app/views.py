from time import strftime
from typing import List
from flask_cors import cross_origin
from flask import request

import app.handlers as handlers

from .ext import q
from app import sckio,\
                app



@app.route('/api/v1/market/list', methods=["GET"])
@cross_origin()
def handle_market_listings():
    print('Listings marketlistings')

    res = handlers.get_marketitems()

    return res


@app.route('/api/v1/filters/list', methods=["GET"])
@cross_origin()
def handle_filters_listings():
    print('Listing filters')

    res = handlers.get_filters()

    return res


@app.route('/api/v1/proxies/list', methods=["GET"])
@cross_origin()
def handle_proxies_listings():
    print('Listing proxies')

    res = handlers.get_proxies()

    return res


@app.route('/api/v1/querystrings/list', methods=["GET"])
@cross_origin()
def handle_querystrings_listings():
    print('Listing querystrings')

    res = handlers.get_querystrings()

    return res


@app.route('/api/v1/purchases/list', methods=["GET"])
@cross_origin()
def handle_purchases_listings():
    print('Listing purchases')

    res = handlers.get_purchases()

    return res


@app.route('/api/v1/filters/update', methods=["POST"])
@cross_origin()
def handle_filters_update():
    f = request.get_json()['f']

    res = handlers.set_filters(f)

    return res


@app.route('/api/v1/proxies/update', methods=["POST"])
@cross_origin()
def handle_proxies_update():
    proxies = request.get_json()['proxies']

    res = handlers.set_proxies(proxies)

    return res


@app.route('/api/v1/querystrings/update', methods=["POST"])
@cross_origin()
def handle_querystrings_update():
    querystrings = request.get_json()['querystrings']
    print('Updating querystrings', querystrings)

    res = handlers.set_querystrings(querystrings)

    return res


@sckio.on('buy_market_item')
def handle_market_buy(data: dict):
    print('Market Buy Item enqueued ...', data)
    task = q.enqueue(handlers.steam_market_buy, data)
    msg: str = f'# Task queued at { task.enqueued_at.strftime("%a %d %b %Y %H:%M:%S") }. { len(q) } jobs queued'

    print(msg)


@sckio.on('disconnect')
def handle_disconnect():
    print('Steamdata gathering ended ...')