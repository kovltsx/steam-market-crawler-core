import time

from typing import List
from bson.json_util import dumps
from flask import jsonify
from app import core

def get_marketitems():
    res = [res for res in core.get_listinginfo()]
    
    return { 'listings': dumps(res) }


def get_filters():
    res = [res for res in core.retrieve_filters()]
    
    return { 'listings': dumps(res) }


def set_filters(f):
    res = [res for res in core.update_filters(f)]
    
    return { 'listings': dumps(res) }


def get_proxies():
    res = [res for res in core.retrieve_proxies()]
    
    return { 'listings': dumps(res) }


def set_proxies(proxies: str):
    res = [res for res in core.update_proxies(proxies)]
    
    return { 'listings': dumps(res) }


def get_querystrings():
    res = [res for res in core.retrieve_querystrings()]
    
    return { 'listings': dumps(res) }


def set_querystrings(queries: str):
    res = [res for res in core.update_querystrings(queries)]
    
    return { 'listings': dumps(res) }


def get_purchases():
    res = [res for res in core.retrieve_purchases()]
    
    return { 'listings': dumps(res) }


def steam_market_buy(data: dict) -> None:
    core.handle_market_buy(data)

    return