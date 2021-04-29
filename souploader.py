import pandas as pd
from bs4 import BeautifulSoup
import requests
from requests import get

from datetime import datetime, timedelta
import os

HAS_REQUESTS_CACHE = True
CACHE_EXPIRE_MINUTES = int(os.getenv('PY_CACHE_EXPIRE_MINUTES', 10))
try:
    from requests_cache import install_cache
    install_cache(cache_name='py_loader_cache',
                  expire_after=timedelta(minutes=CACHE_EXPIRE_MINUTES))
except ImportError:
    HAS_REQUESTS_CACHE = False

class SoupLoaderError(RuntimeError):
    '''Soup loader error'''
    def __init__(self, text, status_code, url):
        super().__init__(text)
        self.status_code = status_code
        self.url = url
    
def load_soup(addr):
    '''Load a web address into a BS4 soup object'''
    _get = get(addr)
    try:
        _get.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(_get.url)
        raise SoupLoaderError(e.response.text, e.response.status_code, _get.url) from None
        
    soup = BeautifulSoup(_get.text,'lxml')
    return soup

def soup_get_table_as_pandas(soup, **kw):
    '''
    Find a table by something soupish. A useful argument might be 'id=', or 'class='.
    Returns a list of pandas data frames unless 'id=' is specified, in which case
    a single data frame is returned (because only one table can have the same id).
    '''
    table = soup.find('table', kw)
    df = pd.read_html(str(table))
    if 'id' in kw:
        return df[0]
    else:
        return df