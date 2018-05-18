import time
import requests
import datetime as dt
import pandas as pd
import numpy as np
import quandl
import os
import re
import zipfile
import pandas as pd
import json

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

from financePy import general_tools as gt

try:
    from io import StringIO
    from io import BytesIO
except ImportError:
    from StringIO import StringIO

quandl.ApiConfig.api_key = 'bsiBauMrYWn6J1yxSpQG'





def tickers():
    """
    All the WIKI symbols stored in a pandas dataframe
        
  
    Returns
    -------
    df : a pandas datafram
        A pandas dataframe with a column for the ticker and the name 

    """
    url = 'https://www.quandl.com/api/v3/databases/WIKI/codes?api_key=bsiBauMrYWn6J1yxSpQG'
    request = requests.get(url)
    z = zipfile.ZipFile(BytesIO(request.content))
    df = pd.read_csv(z.open(z.namelist()[0]), names = ['ticker','name'])
    
    return df

def historical(ticker, start_date = '2017-01-01', end_date ='2018-01-01', collapse = 'daily'):
    
    collapse = collapse.lower()
    if collapse in ['1d','daily']:
        collapse = 'daily'
    elif collapse in ['m','monthly']:
        collapse = 'monthly'
    elif collapse in ['q','quarterly']:
        collapse = 'quarterly'
    elif collapse in ['a','annual']:
        collapse = 'annual'
    if type(start_date) == type([]):
        start_date = '%s-%s-%s'   %  (str(start_date[0]),  gt.formatt(start_date[1]), gt.formatt(start_date[2]))

    if type(end_date) == type([]):
        end_date = '%s-%s-%s'   %  (str(end_date[0]),  gt.formatt(end_date[1]), gt.formatt(end_date[2]))
    elif type(end_date) == type(''):
        pass
    else:
        end_date = dt.datetime.today()
        end_date = '%s-%s-%s'   %  (str(end_date.year),  gt.formatt(end_date.month), gt.formatt(end_date.day))
        
    return quandl.get(ticker, start_date , end_date , collapse = collapse )
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    