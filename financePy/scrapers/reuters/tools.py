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

print('THIS MODULE IS IN ALPHA AND MAY NOT WORK')


def get_financials_IT(name, categories = ['Balance Sheet' ]):
    start = 'https://duckduckgo.com/?q='
    end = '&t=canonical&ia=web'
    duck = start + str(name.split())[1:-1].replace(',','').replace('\'','').replace(' ','+') + '+Reuters' + end 
    #categories = ['Income Statement', 'Balance Sheet', 'Cash Flow' ]
    tables = {}
    
    o = Options()
    o.add_argument('-headless')
    
    for typ in categories:
        driver = webdriver.Firefox( executable_path = '/usr/local/bin/geckodriver', firefox_options=o)
        driver.get(duck)
        results = driver.find_elements_by_xpath('//a[@class="result__a"]')
        search_url = results[1].get_attribute('href')
        search_url = 'https://it.reuters.com/investing/stocks/incomeStatement?stmtType='+typ[:3].upper()+'&perType=ANN&symbol=' + search_url.split('/')[-1]
        driver.get(search_url)
        content = driver.page_source
        soup = BeautifulSoup(content, 'lxml') # Parse the HTML as a string
        table = soup.find_all('table')[0] # Grab the first table
        table = gt.parse_html_table(table)
        table.set_index(table.iloc[:,0], inplace = True)
        table.drop(columns = [table.columns[0]], inplace = True)
        table.columns = list(map(lambda x :str(x.split()[0]),  table.columns))
        table.replace({',':'','\(':'','\)':''}, regex = True, inplace = True)
        table.replace('--',np.nan , inplace = True)
        table.dropna(inplace = True)
        driver.quit()
        tables[typ] = table
    
    return  tables