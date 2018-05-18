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
import re as __re__

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

try:
    from io import StringIO
    from io import BytesIO
except ImportError:
    from StringIO import StringIO



def usage_refill(credentials):
    for i in credentials.index:
        url = 'https://forex.1forge.com/1.0.3/quota?api_key='+credentials.loc[i,'api']
        r = requests.get(url)
        content = r.content.decode('utf-8')
        res = json.loads(content)
        credentials.loc[i,'usage'] = res['quota_used']/res['quota_limit']

        

def dates_checker(start_date,end_date, sep = '-'):
    if type(start_date) == type([]):
        start_date = '%s-%s-%s'   %  (str(start_date[0]),  formatt(start_date[1]), formatt(start_date[2]))
    elif type(start_date) == type(''):
        p1 = __re__.compile(r'\d\d\d\d.\d\d.\d\d')
        p2 = __re__.compile(r'\d\d\d\d.\d.\d')
        if p1.match(start_date) is not None or p2.match(start_date) is not None:
            start_date = start_date.split(start_date[4])
            start_date = '%s%s%s%s%s'   %  (start_date[0], sep ,formatt(int(start_date[1])), sep ,formatt(int(start_date[2])))
        else:
            print(start_date)
            raise ValueError('Wrong start_date format')
    else:
        raise ValueError('I think start_date should be a list or a string')        

    if type(end_date) == type([]):
        end_date = '%s-%s-%s'   %  (str(end_date[0]),  formatt(end_date[1]), formatt(end_date[2]))
    elif type(end_date) == type(''):
        p1 = __re__.compile(r'\d\d\d\d.\d\d.\d\d')
        p2 = __re__.compile(r'\d\d\d\d.\d.\d')
        if p1.match(end_date) is not None or p2.match(end_date) is not None:
            end_date = end_date.split(end_date[4])
            end_date = '%s%s%s%s%s'   %  (end_date[0], sep ,formatt(int(end_date[1])), sep ,formatt(int(end_date[2])))
        else:
            raise ValueError('Wrong end_date format')
    else:
        end_date = dt.datetime.today()
        end_date = '%s-%s-%s'   %  (str(end_date.year),  formatt(end_date.month), formatt(end_date.day))

    return start_date,end_date


def parse_html_table(table):
    '''https://github.com/Benny-/Yahoo-ticker-symbol-downloader'''
    n_columns = 0
    n_rows=0
    column_names = []

    for row in table.find_all('tr'):
        
        td_tags = row.find_all('td')
        if len(td_tags) > 0:
            n_rows+=1
            if n_columns == 0:
                n_columns = len(td_tags)
                
        th_tags = row.find_all('th') 
        if len(th_tags) > 0 and len(column_names) == 0:
            for th in th_tags:
                column_names.append(th.get_text())

    if len(column_names) > 0 and len(column_names) != n_columns:
        raise Exception("Column titles do not match the number of columns")

    columns = column_names if len(column_names) > 0 else range(0,n_columns)
    df = pd.DataFrame(columns = columns,
                      index= range(0,n_rows))
    row_marker = 0
    for row in table.find_all('tr'):
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            df.iat[row_marker,column_marker] = column.get_text()
            column_marker += 1
        if len(columns) > 0:
            row_marker += 1
            
    for col in df:
        try:
            df[col] = df[col].astype(float)
        except ValueError:
            pass
    
    return df

def get_ret_vol_SR(weights, log_ret):
    weights = np.array(weights)
    ret = sum(log_ret.mean() * weights * 252)
    vol = np.sqrt(np.dot(weights.T,np.dot(log_ret.cov()*252,weights)))
    SR = ret/vol
    return np.array([ret,vol,SR])

def filter_by(data_dict, symbols_list, filt, ratio = 0.75):
    if filt == 'volume':
        volumes = [data_dict[x]['Volume'].sum() for x in symbols_list]
        volumes = sorted(volumes)
        volume = min(volumes[int(len(volumes)*(1-ratio)):])
        symbols_list = list(map(lambda x : x if data_dict[x]['Volume'].sum() > volume else 'Not enough' , symbols_list))
        return np.array(symbols_list)
    else:
        raise ValueError('No right filter specified')
        
def fill_data(data, max_index):
    filler = np.full((1, len(data.columns)), np.nan)
    filled = pd.DataFrame(index = max_index, columns=data.columns)
    for i in max_index:
        if i not in data.index:
            filled.loc[i] = filler
        else:
            filled.loc[i] = data.loc[i].values
    filled.reset_index(inplace = True)
    filled.fillna(method='backfill', inplace = True)
    filled.index = max_index
    
    return filled


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    if iteration == total: 
        print()


def timeout(func, args=(), kwargs={}, timeout_duration=2, default=None):
    '''This function will spwan a thread and run the given function using the args, kwargs and 
    return the given default value if the timeout_duration is exceeded 
    ''' 
    import threading
    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = default
        def run(self):
            try:
                self.result = func(*args, **kwargs)
            except:
                self.result = default
    it = InterruptableThread()
    it.start()
    it.join(timeout_duration)
    if it.isAlive():
        return []
    else:
        return it.result

def formatt(i):
    if i >= 10:
        return str(i)
    else:
        return str(str(0)+str(i))
