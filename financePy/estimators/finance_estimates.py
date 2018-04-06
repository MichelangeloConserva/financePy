from matplotlib import dates
from datetime import datetime, date, time, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os


def bollinger_bands(data, cat = 'Close', window = 20, dropna = True, notifier = False):

    SMA = data[cat].rolling(window).mean()
    upper = SMA + data[cat].rolling(window).std()
    lower = SMA - data[cat].rolling(window).std()
    
    result = pd.concat([data[cat],SMA,upper,lower],1)    
    result.columns = ['Close','SMA'+str(window),'Upper','Lower']
    if dropna:
        result.dropna(inplace = True)
    else:
        result.fillna(method = 'ffill', inplace = True)
        
    if notifier:
        up = result.apply( lambda x : int(x.Close > x.Upper), 1)
        down = result.apply( lambda x : -1*int(x.Close < x.Lower), 1)
        result['Notifier'] = up + down

    return result


def exp_mov_avg(data, windows_list = [35,70], cat = 'Close', dropna = True, notifier = False):
    
    result = pd.concat([ data[cat].ewm(span = x).mean() for x in windows_list ]+[data[cat]] ,1)
    result.columns = ['Ema_'+str(x) for x in windows_list] + ['Close']
    
    
    if dropna:
        result.dropna(inplace = True)
    else:
        result.fillna(method = 'ffill', inplace = True)
        
    if notifier and len(windows_list) == 2:
        result['Notifier'] = result.apply( lambda x : 1 if (round(x['Ema_'+str(windows_list[0])],2) >= round(x['Ema_'+str(windows_list[1])],2)) else -1 , 1)

    return result
        







