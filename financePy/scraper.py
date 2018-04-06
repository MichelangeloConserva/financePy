import time
import requests
import datetime as dt
import pandas as pd
import numpy as np
import quandl
import os
import re
import zipfile
try:
    from io import StringIO
    from io import BytesIO
except ImportError:
    from StringIO import StringIO

quandl.ApiConfig.api_key = 'bsiBauMrYWn6J1yxSpQG'


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
            

def get_yahoo_tickers():
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

def get_quandl_tickers():
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
    # Print New Line on Complete
    if iteration == total: 
        print()

# 
# Sample Usage
# 

#from time import sleep
#
#
#data = []
#l = len(quand)
#
#printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
#for i in range(l):
#    try:
#        data += [quandl.get(quand[i], start_date = '2017-01-01', end_date ='2018-01-01' )]
#    except:
#        pass
#    # Update Progress Bar
#    printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)


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


def get_data_from_QUANDL_list(symbols,start_date = [2000,1,1], end_date=False, frequency = '1d', folder = True, folder_name = 'current_data'):
    """
    """

    if type(start_date) == type([]):
        start_date = '%s-%s-%s'   %  (str(start_date[0]),  formatt(start_date[1]), formatt(start_date[2]))

    if type(end_date) == type([]):
        end_date = '%s-%s-%s'   %  (str(end_date[0]),  formatt(end_date[1]), formatt(end_date[2]))
    elif type(end_date) == type(''):
        pass
    else:
        end_date = dt.datetime.today()
        end_date = '%s-%s-%s'   %  (str(end_date.year),  formatt(end_date.month), formatt(end_date.day))
        
    if type(symbols) == type(pd.Series()):
        symbols = symbols.tolist()
        
    l = len(symbols)
    data = {}

    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for i in range(len(symbols)):
        symb = symbols[i][5:]
        data[symb] = quandl.get(symbols[i], start_date = '2017-01-01', end_date ='2018-01-01' )
        if len(data[symbols[i][5:]].index) == 0:
            data.pop(symb)
        printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)

    return data



def get_data_from_YAHOO_list(symbols, start_date = [2000,1,1], end_date=False, frequency = '1d', folder = True, folder_name = 'current_data'):
    """
    Given a list of symbols I will return a dictionary. Its index will be the symbols in the given list and 
    the values pandas dataframes containting Date, Open, High, Adj. Close. 
    
    an excel file containing almost all yahoo symbols is here http://investexcel.net/all-yahoo-finance-stock-tickers/


    Parameters
    ----------
    symbols : an array-like.
        An array of all the companies you want to know. REMEMBER TO USE YAHOO SYMBOLS.
    start_date : a list containing the date in number or a string or a datetime.
        The order is YYYY, M, D if you choose the array form. "YYYY-MM-DD" for the string form, same for datetime form, default [2000,1,1].
    end_date : a list containing the date in number or a string or a datetime.
        The order is YYYY, M, D if you choose the array form. "YYYY-MM-DD" for the string form, same for datetime form, default False.
    frequency : a string
        a string which represents the frequency of data, default '1d'
    folder : boolean
        A bool to decide if you'd like to have all the data stored in a folder
    folder_name : a string
        The name for the folder where to store the data, dafault "current_data"
        
  
    Returns
    -------
    data : a dict
        A pandas dataframe is assigned at each symbol
    folder : a folder in your pc
        a folder which contains all the data you downloaded
        
        
    Examples
    --------
    >>> from financePy import scraper as st
    >>> data = st.get_data_from_list(['AAPL','ATL.MI','BMW.DE'])

    """
    if type(start_date) == type(''):
        start_date = start_date.split('-')
        start_date = [int(x) for x in start_date]
    if type(symbols) == type(pd.Series()):
        symbols = symbols.tolist()
    
    data = {}
    not_yet = []
    
    symbols = list(map(lambda x: symbols.remove(x) if '.TI' in x else x, symbols))
    
    for symbol in symbols:
        if symbol == None:
            symbols.remove(None)
        else:
            num_space = 15-len(symbol)
            data[symbol] = timeout(get_historical, (symbol,start_date,end_date, frequency), timeout_duration = 5)
            if type(data[symbol]) == type(pd.DataFrame()):
                print(symbol+' '*num_space+'has been done correctly')
            elif data[symbol] == -1:
                data.pop(symbol)
                print(symbol +' '*num_space+ 'removed')
            else:
                data.pop(symbol)
                not_yet.append(symbol)
                print(symbol +' '*num_space+ 'not yet')


        
    
    for symbol in not_yet:
        data[symbol] = timeout(get_historical, (symbol,start_date,end_date, frequency), timeout_duration = 15)
        if type(data[symbol]) == type(pd.DataFrame()):
            num_space = 15-len(symbol)
            print(symbol+' '*num_space+'has been done correctly')
            not_yet.remove(symbol)

    while len(not_yet) >0:
        print('There are '+str(len(not_yet))+' to be downloaded, shall I continue?')
        ans = input()
        
        if ans.lower() in ['yes','y']:
            for symbol in not_yet:
                data[symbol] = timeout(get_historical, (symbol,start_date,end_date, frequency), timeout_duration = 60)
                if type(data[symbol]) == type(pd.DataFrame()):
                    num_space = 15-len(symbol)
                    print(symbol+' '*num_space+'has been done correctly')
                    not_yet.remove(symbol)
        else:
            break


        
    for i in list(data.keys()):
        if type(data[i]) != type(pd.DataFrame()):
            data.pop(i)
    
    for key in list(data.keys()):
        if not len(data[key]) > 1:
            data.pop(key)
    
    max_len = max([len(x.index) for x in data.values()])
    for x in data.values():
        if len(x.index) == max_len:
            max_index = x.index
            break
    for key,item in data.items():
        if len(data[key]) < max_len:
            data[key] = fill_data(data[key], max_index)
    
    
    
    if folder:    
        if not os.path.exists(folder_name+'/'):
            os.makedirs(folder_name+'/')
            
        for df in data.keys():
            try: 
                data[df].to_csv(folder_name+'/'+df+'.csv',index = False)
            except:
                if df not in not_yet:
                    not_yet.append(df)
            
        f = open(folder_name+'/'+'missing.txt', 'w')
        for missed in not_yet:
            f.write(missed+'\n')
        f.close()

    return data

def get_historical(ticker,start_date = [2000,1,1], end_date=False ,interval="1d"):
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
        a string which represents the frequency of data.
        
  
    Returns
    -------
    data : a pandas dataframe
        A pandas dataframe for the symbol
    """
    
    url = "https://finance.yahoo.com/quote/%s/history" % ticker
    r = requests.get(url)
    res = r.content.decode('utf-8')
        
    if "No results for &#x27;%s&#x27" % ticker.lower() in res:
        return -1
        
    if end_date: 
        end_date = int(time.mktime(dt.datetime(end_date[0],end_date[1],end_date[2]).timetuple()))
    else:
        today = dt.datetime.today()
        end_date = int(time.mktime(dt.datetime(today.year,today.month,today.day).timetuple()))
        
        
        
    url = "https://finance.yahoo.com/quote/%s/history" % ticker
    r = requests.get(url)
    cookie = r.cookies["B"]

    pattern = re.compile('.*"CrumbStore":\{"crumb":"(?P<crumb>[^"]+)"\}')
    txt = r.content
    for line in txt.splitlines():
        m = pattern.match(line.decode("utf-8"))
        if m is not None:
            crumb = m.groupdict()['crumb']
            crumb = crumb.replace(u'\\u002F', '/')

    if type(start_date) == type([]):
        start = int(time.mktime(dt.datetime(start_date[0],start_date[1],start_date[2]).timetuple()))
    else:
        start = start_date
    if not end_date: 
        today = dt.datetime.today()
        end_date = int(time.mktime(dt.datetime(today.year,today.month,today.day).timetuple()))
    
    
    api_url = "https://query1.finance.yahoo.com/v7/finance/download/%s?period1=%s&period2=%s&interval=%s&events=%s&crumb=%s"
    url = api_url % (ticker, start, end_date, interval, 'history', crumb)   
    
    data = requests.get(url, cookies={'B':cookie})
    content = StringIO(data.content.decode("utf-8"))
    
    data = pd.read_csv(content, sep=',')
    data['Date'] =  pd.DatetimeIndex(data.Date)
    data.set_index('Date', inplace = True)
    data = data.loc[dt.datetime(start_date[0],start_date[1],start_date[2]):,:]
    
    return data

    































