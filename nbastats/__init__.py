'''
Loads data from stats.nba.com

Some links:
 * https://github.com/bttmly/nba
 * http://danielwelch.github.io/documenting-the-nba-stats-api.html
 * https://github.com/seemethere/nba_py

'''

import numpy as np

from datetime import datetime, timedelta
import os

from requests import get
import requests.exceptions
import pandas as pd

TODAY = datetime.today()
BASE_URL = 'http://stats.nba.com/stats/{endpoint}'
HEADERS = {
    'user-agent': ('Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'),  # noqa: E501
    'Dnt': ('1'),
    'Accept-Encoding': ('gzip, deflate, sdch'),
    'Accept-Language': ('en'),
    'origin': ('http://stats.nba.com')
    }

HAS_REQUESTS_CACHE = True
CACHE_EXPIRE_MINUTES = int(os.getenv('NBA_PY_CACHE_EXPIRE_MINUTES', 10))
try:
    from requests_cache import install_cache
    install_cache(cache_name='nba_cache',
                  expire_after=timedelta(minutes=CACHE_EXPIRE_MINUTES))
except ImportError:
    HAS_REQUESTS_CACHE = False

class NbaStatsError(RuntimeError):
    def __init__(self, text, status_code, url):
        super().__init__(text)
        self.status_code = status_code
        self.url = url
    
def _get_json(endpoint, params, referer='scores'):
    """
    Internal method to streamline our requests / json getting
    Args:
        endpoint (str): endpoint to be called from the API
        params (dict): parameters to be passed to the API
    Raises:
        HTTPError: if requests hits a status code != 200
    Returns:
        json (json): json object for selected API call
    """
    h = dict(HEADERS)
    h['referer'] = 'http://stats.nba.com/{ref}/'.format(ref=referer)
    _get = get(BASE_URL.format(endpoint=endpoint), params=params,
               headers=h)
    try:
        _get.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(_get.url)
        raise NbaStatsError(e.response.text, e.response.status_code, _get.url) from None
        
    #return _get.text
    return _get.json()

def _api_scrape(json_inp, ndx=0):
    """
    Internal method to streamline the getting of data from the json
    Args:
        json_inp (json): json input from our caller
        ndx (int): index where the data is located in the api
    Returns:
        If pandas is present:
            DataFrame (pandas.DataFrame): data set from ndx within the
            API's json
        else:
            A dictionary of both headers and values from the page
    """

    try:
        headers = json_inp['resultSets'][ndx]['headers']
        values = json_inp['resultSets'][ndx]['rowSet']
    except KeyError:
        # This is so ugly but this is what you get when your data comes out
        # in not a standard format
        try:
            headers = json_inp['resultSet'][ndx]['headers']
            values = json_inp['resultSet'][ndx]['rowSet']
        except KeyError:
            # Added for results that only include one set (ex. LeagueLeaders)
            headers = json_inp['resultSet']['headers']
            values = json_inp['resultSet']['rowSet']
    return pd.DataFrame(values, columns=headers)

def get_params_from_url(url):
    '''Load a URL and get the parameters and values split out into a dictionary'''
    _,parms = url.split('?')
    parms = parms.replace('%20',' ')
    parms = [i.split('=') for i in parms.split('&')]
    parms = {i[0]:i[1] for i in parms}
    return parms
    
def _merge_fields(fields, parms):
    this_fields = dict(**fields)
    for i,j in parms.items():
        if i not in this_fields:
            raise ArgumentError("unknown parameter '{}'; see `fields`".format(i))
        this_fields[i] = j
    return this_fields
