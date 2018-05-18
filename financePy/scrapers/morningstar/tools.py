import time
import requests
import datetime as dt
import pandas as pd
import numpy as np
import os
import re
import zipfile
import pandas as pd
import itertools

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from financePy import scraper as scr
from financePy import general_tools as gt

try:
    from io import StringIO
    from io import BytesIO
except ImportError:
    from StringIO import StringIO
import json
import matplotlib.pyplot as plt


headers = { 
            'ApiKey': 'lstzFDEOhfFNMLikKa0am9mgEKLBl49T',
#                                'Host': 'api-global.morningstar.com',
#                                'Origin': 'http://www.morningstar.com',
 #                               'Pragma': 'no-cache',
  #                              'Referer': 'http://www.morningstar.com/stocks/xnas/aapl/quote.html',
#                                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0',
            'X-API-REALTIME-E': 'eyJlbmMiOiJBMTI4R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ.wX_lECTDnzuDLYRJwI-0hxr-afvqZ-GqrevQMauXMm6kdzx1h6nHmIz5laPMcFjk9g123qS6FRbv2rJIUI4Dsrg2b306xFJ1g2H8h4qiExdYaOd3ag7BA4bXNJiwcu640HMcRHbyN5DCkJvY9ckqEBV1gOwf5vGn0AnFawqJ1rI.hf31mkmpQI_UVGgq.9vtGBjMiejWToIH-ZbZByB7gVgaCCyAy2_SbAcWZVKeHiumgBN8eP-4UlJ2Hc1oFMTRWIJvPsc-4tS8UP_GYTUPL041xxEE_EKP7M1iYPPbSt7YgJgxeC5_ROiIY8TF-Il9Qnpx2x3U3mLjEDp4PBSKFgj1NGq-Fg_53oTNxWaRnxMC1fsJejL70UM827pKxrRnK3at-yGdfHHku6WjBqdw3Wg.gw8hKKyUYdqwwRVqRGUa1w',
            'X-SAL-ContentType': 'nNsGdN3REOnPMlKDShOYjlk6VYiEVLSdpfpXAm7o2Tk='}


def tickers(country):

    country = 'united states' if  country.lower().replace(' ','') in ['usa','unitedstates'] else country
    
    url = 'https://www.countrycode.org/'
    r = requests.get(url)
    content = r.content.decode('utf-8')
    soup = BeautifulSoup(content,'lxml')
    countries  = gt.parse_html_table(soup)   
    countries.columns = list(map(lambda x: x.replace(' ','').replace('\n','').lower() ,countries.columns))   
    countries.country = countries.country.str.lower()
    
    api = '286286941689219'
    iso_code = countries[countries.country == country].isocodes.tolist()[0][-3:].lower()
        
    url = 'https://res.cloudinary.com/torquato/raw/upload/v1524066556/financePy/official_%s_MS.csv' %  iso_code
    
    r = requests.get(url, headers = {'api' : api})
    content = r.content.decode('utf-8')
    
    res = pd.read_csv(StringIO(content))
    res.set_index(res.columns[0], inplace = True)
    
    return res
    

def trailing_returns(ticker,instrum):
    
    fr = instrum['traili_ret_freq'].lower()
    frequency = 'd' if fr in ['d','daily'] else (
                                          'm' if fr in ['m','monthly'] else(
                                                                       'q' if fr in ['q','quarterly'] else None))
    
    if frequency == 'd':
        format__ = ['1Day', '1Week', '1Month', '3Month', 'YearToDate', '1Year', '3Year', '5Year', '10Year', '15Year']
        format_ = ['trailing'+x+'Return' for x in format__]
    elif frequency == 'm':
        format__ = ['1Month', '3Month', '6Month', 'YearToDate', '1Year', '3Year', '5Year', '10Year', '15Year']
        format_ = ['trailing'+x+'Return' for x in format__]    
    elif frequency == 'q':
        format__ = ['1Month', '3Month', '6Month', 'YearToDate', '1Year', '3Year', '5Year', '10Year', '15Year']
        format_ = ['trailing'+x+'Return' for x in format__]
    else:
        raise ValueError(fr + ' is not a correct form for frequency')
        
    url = 'https://api-global.morningstar.com/sal-service/v1/stock/trailingTotalReturns/%s/data?dataType=%s&locale=en-US' % (ticker,frequency)
    r = requests.get(url, headers=headers)
    content = r.content.decode('utf-8')     
    json_res = json.load(StringIO(content))
    
    columns = ['name'] + format_
    rows = [i for i in json_res['trailingTotalReturnsList']]
    array = []
    for col in columns:
        array += [[x[col] for x in rows]]
    
    data = pd.DataFrame(np.array(array).T)
    data.columns =  ['name']  + format_
    data.set_index('name', inplace = True)
    data.dropna(how = 'all', inplace  = True)
    data = data.apply(lambda x: x.astype(float))
    
    return data


def dividens(ticker,instrum):
    
    url = 'https://api-global.morningstar.com/sal-service/v1/stock/dividends/v2/%s/data?locale=en-US' % ticker
    r = requests.get(url, headers=headers)
    content = r.content.decode('utf-8')     
    json_res = json.load(StringIO(content))
    
    columns = [ x if len(x) <= 5 else x.split('.')[-1] for x in json_res['columnDefs_labels'][1:]]
    rows  = [x['label'] for x in json_res['rows']]
    array = np.array([x['datum'] if x['datum'] != [] else [None]*len(columns)   for x in json_res['rows']])
    
    data = pd.DataFrame(array, index = rows, columns = columns)
    data = data.apply(lambda x: x.astype(float))

    return data


def splits(ticker,instrum):
    
    url = 'https://api-global.morningstar.com/sal-service/v1/stock/split/%s/data?locale=en-US' % ticker
    r = requests.get(url, headers=headers)
    content = r.content.decode('utf-8')     
    json_res = json.load(StringIO(content))
    
    data1 = pd.DataFrame(json_res['splitHistory'])
    data2 = pd.DataFrame(json_res['splitOffHistory'])

    return {'splitOffHistory' : data2 , 'splitHistory' : data1}


def ownership(ticker,instrum):

#    opt1 = ['OwnershipData','ConcentratedOwners','Buyers','Sellers']
#    opt2 = ['mutualfund','institution']
    
    results = {}
    for i in itertools.product(instrum['own_opt'][0],instrum['own_opt'][1]):
        url = 'https://api-global.morningstar.com/sal-service/v1/stock/ownership/v1/%s/%s/%s/5/data?locale=en-US' % (ticker,i[0],i[1])
        r = requests.get(url, headers=headers)
        content = r.content.decode('utf-8')     
        json_res = json.load(StringIO(content))
        
        columns = [ x['columnId'] for x in json_res['columnDefs']][1:]
        rows  = [x['name'] if x['name'] != None else 'Total' for x in json_res['rows']]
        array = []
        for col in columns:
            array += [[x[col] for x in json_res['rows']]]
        array = np.array(array).T
        
        data = pd.DataFrame(array, index = rows, columns = columns)
        data.replace('_PO_',np.nan,inplace = True)
        data.dropna(1,how='all',inplace = True)
        results[i] = data
        
    return results
    
    
def executives(ticker,instrum):
    
    url = 'https://api-global.morningstar.com/sal-service/v1/stock/insiders/%s/%s/data?locale=en-US' % (instrum['exe_opt'][0],ticker)
    r = requests.get(url, headers=headers)
    content = r.content.decode('utf-8')     
    if len(content) == 0:
        return ticker   
    json_res = json.load(StringIO(content)) 
    if json_res['rows'] == []:
            return ticker   
    columns = json_res['datesDef']
    outer_rows  = [x['name']+':'+x['title'] if x['type'] == 'person' else x['personId']  for x in json_res['rows']]
    inner_rows  = [[x['name']  for x in json_res['rows'][i]['compensation']] for i in range(len(json_res['rows']))]
    array = []
    for i in range(len(json_res['rows'])):
        inner_dic = []
        for inn in json_res['rows'][i]['compensation']:
            for row in inner_rows[i]:
                if inn['name'] == row:
                    inner_dic += [inn['datum']]
        array += inner_dic
    try:
        array = np.array(array)[:-len(inner_rows[0])]
    except:
        print('\n\n\n'+content+'\n'+url+'\n\n')

    idx = pd.MultiIndex.from_product(  [outer_rows[:-1],inner_rows[0]] , names = ['Person','Compensations'])
    
    data = pd.DataFrame(array, idx, columns)
    data.dropna(how = 'all', inplace = True)
    
    return data
        

def company_profile(ticker,instrum):
    
    url = 'https://api-global.morningstar.com/sal-service/v1/stock/companyProfile/%s?locale=en-US' % ticker
    r = requests.get(url, headers=headers)
    content = r.content.decode('utf-8')     
    json_res = json.load(StringIO(content))
    json_res['sections'].pop('contact')
    
    data = pd.DataFrame(json_res['sections'])
    data.columns = data.iloc[0]
    data = data[1:]
    data = pd.DataFrame(data.values.T,index = data.columns, columns = ['Profile'])

    return data

def real_time_info(ticker,instrum):

    url = 'https://api-global.morningstar.com/sal-service/v1/stock/realTime/v3/%s/data?locale=en-US' % ticker
    r = requests.get(url, headers=headers)
    content = r.content.decode('utf-8')    
    json_res = json.load(StringIO(content))
    
    data = pd.Series(json_res)
    data.name = 'Realt Time info'
    
    return data
    
def complete_valuation(ticker,instrum):

    url = 'https://api-global.morningstar.com/sal-service/v1/stock/valuation/v2/%s?locale=en-US' % ticker
    r = requests.get(url, headers=headers)
    content = r.content.decode('utf-8')     
    json_res = json.load(StringIO(content))
    
    first  = json_res['Collapsed']
    second = json_res['Expanded']
    
    columns = first['columnDefs'][1:]
    rows    = [x['label'] for x in first['rows']] + [x['label'] for x in second['rows']]
    array = np.array([x['datum'] for x in first['rows']+second['rows']])
    
    data = pd.DataFrame(array, index = rows, columns = columns)
    data = data.apply(lambda x: x.astype(float))

    return data


def current_valuation(ticker,instrum):

    url = 'http://financials.morningstar.com/valuate/current-valuation-list.action?&t=%s&region=usa&culture=en-US&cur=&adsFlag=true&_=1490717022553'  % ticker
    r = requests.get(url)
    content = r.content.decode('utf-8')
    if len(content) == 0:
        return ticker
    soup = BeautifulSoup(content, 'lxml') 
    table = soup.find_all('table')[0] 
        
    column_names = []
    for row in table.find_all('tr'):
        th_tags = row.find_all('th') 
        if len(th_tags) > 0 and len(column_names) == 0:
            for th in th_tags:
                column_names.append(th.get_text())

    while '' in column_names:
        column_names.remove('')
    
    df = pd.DataFrame(columns = ['ind'] + column_names)
    
    row_marker = 0
    for row in table.find_all('tr'):
        if row.find('td') == None or row.find('th') == None:
            pass
        else:
            if row.find('th').get_text() == 'Price/Fair Value':
                pass
            else:
                row_in = []
                row_in += [row.find('th').get_text()]
                columns = row.find_all('td')
                for column in columns:
                    row_in += [column.get_text()]
                df.loc[row_marker] = row_in
                if len(columns) > 0:
                    row_marker += 1
            
    df.set_index('ind', inplace = True) 
    df.replace('—',np.nan,inplace = True)
    df.dropna(how = 'all', inplace=True)
    df = df.apply(lambda x: x.astype(float))

    return df

def forward_valuation(ticker,instrum):

    url = 'http://financials.morningstar.com/valuate/forward-valuation-list.action?&t=%s&region=usa&culture=en-US&cur=&adsFlag=true&_=1490717022554' % ticker
    r = requests.get(url)
    content = r.content.decode('utf-8')
    if len(content) == 0:
        return ticker
    soup = BeautifulSoup(content, 'lxml') 
    table = soup.find_all('table')[0] 
    
    column_names = []
    for row in table.find_all('tr'):
        th_tags = row.find_all('th') 
        if len(th_tags) > 0 and len(column_names) == 0:
            for th in th_tags:
                column_names.append(th.get_text())
                
    while '' in column_names:
        column_names.remove('')
    
    
    df = pd.DataFrame(columns = ['ind'] + column_names)
    
    row_marker = 0
    for row in table.find_all('tr'):
        row_in = []
        columns = row.find_all('td')
        for column in columns:
            row_in += [column.get_text()]
        if len(row_in) < len(column_names) or '' in row_in:
            pass
        else:
            df.loc[row_marker] = row_in    
        if len(columns) > 0:
            row_marker += 1
    df.set_index('ind', inplace = True) 
    df.replace('—',np.nan,inplace = True)
    df.dropna(1,how = 'all',inplace=True)
    df = df.apply(lambda x: x.astype(float))

    return df

def history_valuation(ticker,instrum):
    
    url = 'http://financials.morningstar.com/valuate/valuation-history.action?&t=%s&region=usa&culture=en-US&cur=&type=price-earnings&_=1490717022555' % ticker
    r = requests.get(url)
    content = r.content.decode('utf-8')
    if len(content) == 0:
        return ticker
    soup = BeautifulSoup(content, 'lxml') 
    ths = soup.find_all('th')
    second_index = []
    for th in ths:
        text = th.get_text()
        if text not in second_index:
            second_index.append(text)
    
    trs = soup.find_all('tr')
    
    first_index = []
    rows = []
    for tr in trs:
        row = []
        tds = tr.find_all('td')
        for td in tds:
            row.append(td.get_text())
        if '\xa0' in row:
            first_index.append(row[0])
        else:
            rows += [row]

    column_names = [i for i in range(2018-len(rows[0]),2018)]
    idx = pd.MultiIndex.from_product([first_index, second_index],
                                     names = ['Category','Ticker'])
    df = pd.DataFrame(np.array(rows), idx, column_names)
    df.replace('—',np.nan,inplace = True)
    df.dropna(1,how = 'all',inplace=True)
    df = df.apply(lambda x: x.astype(float))
    
    return df


def financials(ticker,instrum):

    categories = list(map(lambda x: 'bs' if x.lower().replace(' ','') == 'balancesheet' or x == 'bs' \
                                     else ( 'is' if x.lower().replace(' ','') == 'incomestatement' or x == 'is'\
                                                 else ( 'cf' if x.lower().replace(' ','') == 'cashflow' or x == 'cf'\
                                                             else print(x +' is not a meaningful code'))), instrum['fin_cat']))
    if None in categories:
        raise ValueError('Categories code error')
    
    frequency = '12' if instrum['fin_frequen'].lower().replace(' ','') in ['a','annual']\
                    else ( '3' if instrum['fin_frequen'].lower().replace(' ','') in ['q','quarterly']\
                               else print(instrum['fin_frequen'] +' is not a meaningful code'))
    if frequency == None:
        raise ValueError('Frequency code error') 
    counter = 0
    tables = {}                    
    for typ in categories:  
        url = 'http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t=%s&reportType=%s&period=%s&dataType=A&order=asc&columnYear=5&number=3' % (ticker, typ, frequency )
        r = requests.get(url)
        content1 = r.content.decode("utf-8")
        while len(content1) == 0 :
            r = requests.get(url)
            content1 = r.content.decode("utf-8")   
            counter += 1
            if counter >= 5:
                return ticker
        content = StringIO( content1[content1.find('. ')+1:])
        data = pd.read_csv(content, sep=',')
        data.set_index(data.columns[0], inplace = True)
        data.dropna(how = 'all', inplace = True)

         
        tables[typ] = data
        time.sleep(0.4)
        
    return tables


def key_ratio(ticker,instrum):

    url= 'http://financials.morningstar.com/ajax/exportKR2CSV.html?t='+ ticker
    r = requests.get(url)
    content = r.content.decode("utf-8")
    if len(content) == 0 or content == 'We’re sorry. There is no available information in our database to display.':
        return ticker
    content = StringIO( content[content.find('ls\n')+3:])
    
    data = pd.read_csv(content, sep=',')
    data[data.columns[0]].fillna(method = 'ffill',inplace = True)
    data.set_index(data.columns[0], inplace = True)
    data.index.name = 'Financials'
    data.dropna(how = 'all', inplace = True)
    data.replace({',':''}, regex = True, inplace = True)
    new_dataframe = data[data[data.columns[-2]] == data.columns[-2]].index.tolist()
    
    result = {}
    
    for i in range(len(new_dataframe)+1):
        
        if i == 0:
            result[data.index.name] = data.loc[:new_dataframe[i],:][:-1].apply(lambda x: x.astype(float))
        elif i == len(new_dataframe):
            temp = data.loc[new_dataframe[-1]:,:]
            temp.index.name = temp.index.tolist()[0]
            temp = temp[1:]
            result[new_dataframe[i-1]] = temp.apply(lambda x: x.astype(float))  
        else:
            temp = data.loc[new_dataframe[i-1]:new_dataframe[i],:][:-1]
            temp.index.name = temp.index.tolist()[0]
            temp = temp[1:]
            result[new_dataframe[i-1]] = temp.apply(lambda x: x.astype(float))    
                
    return result


def get_yield(ticker,instrum):
    url = 'http://financials.morningstar.com/valuate/valuation-yield.action?&t=%s&region=usa&culture=en-US&cur=&_=1490717022555' % ticker
    r = requests.get(url)
    content = r.content.decode('utf-8')
    if len(content) == 0:
        return ticker
    soup = BeautifulSoup(content, 'lxml') 
    
    res = str(soup)
    ticks = res[res.find('ticks')+7:res.find('tickFormatter')-11].split('"')[1:12:2]
    
    grezzo = res[res.find('var data =')+30:res.find('</script>')-23].replace(' ','').split(',')
    values = [float(x) if '.' in x or len(x) <= 3  else '' for x in grezzo]
    while '' in values:
        values.remove('')
    
    data = pd.DataFrame(values, ticks, columns = ['Dividend Yield'])
        
    return data

def priceValue(ticker,instrument):
    url = 'https://api-global.morningstar.com/sal-service/v1/stock/priceFairValue/v1/%s/chart' % ticker
    r = requests.get(url, headers=headers)
    content = r.content.decode('utf-8')     
    json_res = json.load(StringIO(content))
    
    
    
    
    
    















    
#### Same with selenium, almost 1000 times slower




###### TOTAL RETURN AND INDEX
#
#url = 'http://www.morningstar.com/stocks/xnas/aapl/quote.html'
#
#o = Options()
#o.add_argument('-headless')
#driver = webdriver.Firefox( executable_path = '/usr/local/bin/geckodriver', firefox_options=o)
#driver.get(url)
#result = driver.find_element_by_xpath('//table[@class="total-table"]')
#data = pd.read_csv(StringIO(result.text.replace(' ',',')))
#
#### TRAILING RETURNS
#
#url = 'http://www.morningstar.com/stocks/xnas/aapl/quote.html'
#
#o = Options()
#o.add_argument('-headless')
#driver = webdriver.Firefox( executable_path = '/usr/local/bin/geckodriver', firefox_options=o)
#driver.get(url)
#result_dad = driver.find_element_by_xpath('//div[@class="sal-trailing-returns__table daily"]')
#result  = result_dad.find_elements_by_xpath('table')[0]
#
#soup = BeautifulSoup(result.get_attribute('innerHTML'), 'lxml')
#data = st.parse_html_table(soup)
#data.columns = ( x.replace(' ','').replace('\n','') for x in data.columns)
#data
#
#
#r = requests.get(url)
#content = r.content.decode('utf-8')
#soup = BeautifulSoup(content, 'lxml')
#
#
#prova = st.parse_html_table(soup)
#
#
#soup = BeautifulSoup(result.get_attribute('innerHTML'), 'lxml')
#data1 = st.parse_html_table(soup)
#data1.replace({' ':''}, regex = True, inplace = True)
#data1.replace('', np.nan , inplace = True)
#data1.columns = [x.replace(' ','').replace('\n','') for x in data1.columns]
#data1
#
#
##### DIVIDENDS
#
#url1 = 'http://www.morningstar.com/stocks/xnas/aapl/quote.html'
#url2 = 'http://www.morningstar.com/stocks/xmil/atl/quote.html'
#
#o = Options()
#o.add_argument('-headless')
#driver = webdriver.Firefox( executable_path = '/usr/local/bin/geckodriver', firefox_options=o)
#driver.get(url2)
#result_dad = driver.find_element_by_xpath('//div[@class="dividends-table-bottom dividends-bottom"]')
#result  = result_dad.find_elements_by_xpath('table')[0]
#
#
#soup = BeautifulSoup(result.get_attribute('innerHTML'), 'lxml')
#data = st.parse_html_table(soup)
#data.replace({'\n':''}, regex = True, inplace = True)
#data.replace('', np.nan , inplace = True)
#
#data.columns = data.iloc[0,:]
#data.set_index('Calendar', inplace = True)
#data = data[1:]
#data.dropna(how = 'all', inplace = True)
#data
#





def historical(ticker,instrum ,interval="1d"):
    
    start_date,end_date = gt.dates_checker(instrum['start_date'],instrum['end_date'],'-')
    url = 'http://globalquote.morningstar.com/globalcomponent/RealtimeHistoricalStockData.ashx?ticker=%s&showVol=true&dtype=his&f=d&curry=USD&range=%s|%s&isD=true&isS=true&hasF=true&ProdCode=DIRECT' % (ticker,start_date,end_date)
    r = requests.get(url)
    content = r.content.decode('utf-8')
    json_res = json.loads(content)
    
    if json_res == None:
        return ticker
    
    pricedata = json_res['PriceDataList'][0]
    
    datapoint = pricedata['Datapoints']
    
    o = pd.Series([ x[0] for x in datapoint])
    o.name = 'Open'
    h = pd.Series([ x[1] for x in datapoint])
    h.name = 'High'
    l = pd.Series([ x[2] for x in datapoint])
    l.name = 'Low'
    c = pd.Series([ x[3] for x in datapoint])
    c.name = 'Close'
    ohlc = pd.concat([o,h,l,c],1)
    
    volume = pd.Series(json_res['VolumeList']['Datapoints'])
    volume.name = 'Volume'
    ohlc = pd.concat([ohlc,volume],1)
    
    dates = np.array(pricedata['DateIndexs'])
    dates = dates - dates[-1] + len(pd.date_range(start_date,end_date)) -1
    
    date = pd.date_range(start_date,end_date)[dates]
    ohlc.set_index(date,inplace = True)    
    
    return ohlc
#    if True:
#        
#        if type(start_date) == type([]):
#            start_date = '%s-%s-%s'   %  (str(start_date[0]),  gt.formatt(start_date[1]), gt.formatt(start_date[2]))
#    
#        if type(end_date) == type([]):
#            end_date = '%s-%s-%s'   %  (str(end_date[0]),  gt.formatt(end_date[1]), formatt(end_date[2]))
#        
#        url = 'http://globalquote.morningstar.com/globalcomponent/RealtimeHistoricalStockData.ashx?ticker=%s&showVol=true&dtype=his&f=d&curry=USD&range=%s|%s&isD=true&isS=true&hasF=true' % (ticker,start_date,end_date)
#        
#        r = requests.get(url)
#        content = r.content.decode('utf-8')
#        cont = json.loads(content)
#        
#        
#        pricedata = cont['PriceDataList'][0]
#        
#        datapoint = pricedata['Datapoints']
#        
#        o = pd.Series([ x[0] for x in datapoint])
#        o.name = 'Open'
#        h = pd.Series([ x[1] for x in datapoint])
#        h.name = 'High'
#        l = pd.Series([ x[2] for x in datapoint])
#        l.name = 'Low'
#        c = pd.Series([ x[3] for x in datapoint])
#        c.name = 'Close'
#        ohlc = pd.concat([o,h,l,c],1)
#        
#        volume = pd.Series(cont['VolumeList']['Datapoints'])
#        volume.name = 'Volume'
#        ohlc = pd.concat([ohlc,volume],1)
#        
#        dates = np.array(pricedata['DateIndexs'])
#        dates = dates - dates[0]
#        
#        date = pd.date_range('2018-01-01','2018-03-01')[dates]
#        
#        
#        ohlc.set_index(date,inplace = True)
#        
#        return ohlc
#    
#    
#    if False:
    
    
    

#8214 booh
#8217 close
#8219 open
#8222 high
#8223 tipo media mensile
#8224 low
#8225 close
#8226 tipo volume
#8235 tipo media mensile
#8238
    
    
#    if type(start_date) == type([]):
#        start_date = '%s-%s-%s'   %  (str(start_date[0]),  gt.formatt(start_date[1]), gt.formatt(start_date[2]))
#
#    if type(end_date) == type([]):
#        end_date = '%s-%s-%s'   %  (str(end_date[0]),  gt.formatt(end_date[1]), gt.formatt(end_date[2]))
#       
#        
#    url = 'http://mschart.morningstar.com/chartweb/defaultChart?type=getcc&secids='+ticker+'&dataid=8225&startdate='+start_date\
#        +'&enddate='+end_date+'&currency=usd&format=1'
#    r = requests.get(url)
#    content = r.content.decode('utf-8')
#    
#    p = re.compile(r'(\d+-\d+-\d+)')
#    dates = p.findall(content)
#    
#    p = re.compile(r'(\d+\.\d+)')
#    prices = p.findall(content)
#    
#    
#    data = pd.DataFrame(np.array([dates,prices]).T, columns = ['Date','Price'])
#    data['Date'] =  pd.DatetimeIndex(data.Date)
#    data.set_index('Date', inplace = True)
#    data = data.apply(lambda x: x.astype(float))
#
#    return data


    url = 'http://globalquote.morningstar.com/globalcomponent/RealtimeHistoricalStockData.ashx?ticker=F&showVol=true&dtype=his&f=d&curry=USD&range=1900-1-1|2018-04-10&isD=true&isS=true&hasF=true&ProdCode=DIRECT'













