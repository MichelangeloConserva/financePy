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



def tickers():
    """
    All the yahoo symbols stored in a pandas dataframe
        
  
    Returns
    -------
    df : A pandas dataframe with info about
        1. ticker
        2. complete name
        3. exchange
        4. category
        5. country

    """
    
    url = 'http://investexcel.net/wp-content/uploads/2015/01/Yahoo-Ticker-Symbols-September-2017.zip'
    request = requests.get(url)
    z = zipfile.ZipFile(BytesIO(request.content))
    df = pd.read_excel(z.open(z.namelist()[0]))
    z.close()
    df = df.iloc[3:,0:5]
    df.columns = ['ticker','name','exchange','category','country']

    return df

def summary(ticker,*other):
    try:
        url = 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=%s&fields=messageBoardId,longName,shortName,marketCap,underlyingSymbol,underlyingExchangeSymbol,headSymbolAsString,regularMarketPrice,regularMarketChange,regularMarketChangePercent,regularMarketVolume,uuid,regularMarketOpen,fiftyTwoWeekLow,fiftyTwoWeekHigh' % ticker
        r = requests.get(url)
        content = r.content.decode('utf-8')
        json_res = json.loads(content)
        
        data = pd.DataFrame(json_res['quoteResponse']['result'][0], index = ['Summary']).transpose()
        
        return data
    except:
        return ticker

def similars_score(ticker,*other):
    try:
        url = 'https://query2.finance.yahoo.com/v6/finance/recommendationsbysymbol/' + ticker
        r = requests.get(url)
        content = r.content.decode('utf-8')
        json_res = json.loads(content)
        
        data = pd.DataFrame(json_res['finance']['result'][0]['recommendedSymbols'])
        data.set_index('symbol', inplace = True)
        
        return data
    except:
        return ticker
        
def statistics(ticker,*other):
    try:
        url = 'https://finance.yahoo.com/quote/%s/key-statistics?p=%s' % (ticker,ticker)
        r = requests.get(url)
        content = r.content.decode('utf-8')
        soup = BeautifulSoup(content, 'lxml')
        
        data = gt.parse_html_table(soup)
        data.set_index(0, inplace = True)
        data.columns = ['Statistics']
        
        return data
    except:
        return ticker

def financials(ticker,*other):
    try:
        url = 'https://finance.yahoo.com/quote/%s/financials?p=%S' % (ticker,ticker)
        r = requests.get(url)
        content = r.content.decode('utf-8')
        soup = BeautifulSoup(content, 'lxml')
        
        data = gt.parse_html_table(soup)
        data.set_index(0, inplace = True)
        
        return data
    except:
        return ticker


def historical(ticker,start_date = [2000,1,1], end_date=False ,frequency="1d"):
    """
    Given a symbol I will return a pandas dataframe containting Date, Open, High, Adj. Close. 
    
    an excel file containing almost all yahoo symbols is here http://investexcel.net/all-yahoo-finance-stock-tickers/


    Parameters
    ----------
    symbols : a string.
        A string representing the ticker. REMEMBER TO USE YAHOO SYMBOLS.
    start_date : a list containing the date in number or a string or a datetime.
        The order is YYYY, M, D if you choose the array form. "YYYY-MM-DD" for the string form, same for datetime form, default [2000,1,1].
    end_date : a list containing the date in number or a string or a datetime.
        The order is YYYY, M, D if you choose the array form. "YYYY-MM-DD" for the string form, same for datetime form, default False.
    interval : a string
        ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        
  
    Returns
    -------
    data : a pandas dataframe
        A pandas dataframe for the symbol
    """
    
    poss_freq = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk','1mo', '3mo'] #, '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    
    frequency = frequency.lower()
    if frequency not in poss_freq:
        if frequency in ['d','daily']:
            frequency = '1d'
        elif frequency in ['m','monthly']:
            frequency = '1mo'
        elif frequency in ['q','quarterly']:
            frequency = '3mo'
        elif frequency in ['a','annual']:
            frequency = '1y'
        else:
            raise ValueError('Wrong frequency, check the doc for the available values')     
    
    if frequency in poss_freq[:7]:
        raise ValueError('this frequency is not support because yahoo data are inclomplete')
        
    start_date,end_date = gt.dates_checker(start_date,end_date)
    start_date,end_date = int(dt.datetime.timestamp(pd.to_datetime(start_date))),int(dt.datetime.timestamp(pd.to_datetime(end_date)))
    
#    interval = (pd.to_datetime(end_date)-pd.to_datetime(start_date)).days    
#    if frequency == '1h' or '60m':
#        if interval > 730:
#            raise ValueError('The requested range must be within the last 730 days.')
#    elif frequency == '90m':
#        if interval > 60:
#            raise ValueError('The requested range must be within the last 60 days.')
        
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/%s?period1=%d&period2=%d&interval=%s&events=div|split' % (ticker,start_date,end_date,frequency)

    try:
        r = requests.get(url)
    except:
        time.sleep(1)
        r = requests.get(url)
    content = r.content.decode('utf-8')
    json_res = json.loads(content)['chart']
    
    if json_res['result'] == None:
        return ticker
    elif 'timestamp' not in json_res['result'][0].keys():
        return ticker
    else: 
        json_res = json_res['result'][0]
    
    dates = pd.Series([dt.datetime.fromtimestamp(x).date() for x in json_res['timestamp']])
    col = ['Open','High','Low','Close','Volume','Adj Close']
    ohlc = pd.DataFrame(index = dates, columns = col)
    for i in range(len(dates)):
        ohlc.loc[dates[i]] = [json_res['indicators']['quote'][0][x.lower()][i] for x in col[:-1]] + [json_res['indicators']['adjclose'][0]['adjclose'][i]]
    ohlc = ohlc.apply(lambda x: x.astype(float))

    return ohlc














