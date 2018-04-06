import scraper as scr
import pandas as pd
import numpy as np
import plotter 

from scipy.optimize import minimize
from models import stationary as st
from estimators import finance_estimates as fe


start_date = [2000,1,1]
end_date = False


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



class Portfolio:
    def __init__(self,symbols, start_date = start_date, end_date=end_date, by = 'quandl', filt = False, filt_ratio=0.75, null_treshold = 0.01):
        if type(symbols) == type(pd.Series()):
            symbols = symbols.tolist()
            
        if by == 'quandl':
            self.tecnical_data = scr.get_data_from_QUANDL_list(symbols, start_date = start_date, end_date=end_date, folder = False)
            self.symbols_list = list(self.tecnical_data.keys())
            self.by = by
        elif by == 'yahoo':
            self.tecnical_data = scr.get_data_from_YAHOO_list(symbols, start_date = start_date, end_date=end_date, folder = False)
            self.symbols_list = list(self.tecnical_data.keys())
            self.by = by
        
        if filt:
            filterer = filter_by(self.tecnical_data, list(self.tecnical_data.keys()), filt, filt_ratio)
            bilancer = 0
            for i in range(len(filterer)):
                if filterer[i] == 'Not enough':
                    self.tecnical_data.pop(self.symbols_list[i-bilancer])
                    self.symbols_list.pop(i-bilancer)
                    bilancer += 1

            
#        to_delete = []
#        for ticker in self.symbols_list:
#            if len(self.tecnical_data[ticker].Close[self.tecnical_data[ticker].Close.isnull()])/len(self.tecnical_data[ticker].Close) >= null_treshold:
#                to_delete.append(ticker)

        
    def bollinger_bands(self, cat = 'Close', window = 20, dropna = True, notifier = False, output = False):
        bollinger_bands = {}
        for symbol in self.symbols_list:
            bollinger_bands[symbol] = fe.bollinger_bands(self.tecnical_data[symbol], cat = cat, window = window, dropna = dropna, notifier = notifier)
        self.boll_bands = bollinger_bands
        if output:
            return bollinger_bands
    
    def EMA(self, windows_list = [35,70], cat = 'Close', plot = False, dropna = True, output = False, notifier = False):
        ema = {}
        for symbol in self.symbols_list:
            ema[symbol] = fe.exp_mov_avg(self.tecnical_data[symbol], windows_list = windows_list, cat = cat, dropna = dropna, notifier = notifier)
        self.ema = ema
        
        if plot:
            plotter.mov_avg_plot(ema,notifier)
        
        if output:
            return ema
            
    
    def markowits_allocation(self, minimun = 0.01, plot = False):
        if self.by == 'yahoo':
            close = 'Adj Close'
        elif self.by == 'quandl':
            close = 'Adj. Close'            
        prices = pd.concat([self.tecnical_data[ticker][close] for ticker in self.symbols_list],1)

        prices.columns = self.symbols_list
        log_ret = np.log(prices/prices.shift(1))
        
        constraints = ({'type' : 'eq', 'fun' : lambda x: np.sum(x)-1})
        bounds = [(0,1) for i in range(len(self.symbols_list))]
        init_guess = [ 1/len(self.symbols_list) for i in range(len(self.symbols_list))]
        
        neg_sharpe = lambda x,y : -1 * get_ret_vol_SR(x,y)[2]
        opt_result = minimize(neg_sharpe, init_guess, args=(log_ret), method = 'SLSQP', bounds = bounds, constraints = constraints)
        self.weights  = opt_result.x[opt_result.x>minimun]/sum(opt_result.x)
        self.stocks = list(np.array(self.symbols_list)[opt_result.x>minimun])
        
        
        mark_result = pd.concat([pd.Series(self.stocks), pd.Series(self.weights)],1)
        mark_result.columns = ['Stock','Weight']
        mark_result['SR'] = mark_result['Stock'].apply(lambda x: self.tecnical_data[x][close].mean()/self.tecnical_data[x][close].std(),1)
        mark_result.set_index('Stock', inplace = True) 
        mark_result = mark_result.apply(lambda x: round(x,4),0)
        rec = float(mark_result['Weight'].sum())
        mark_result['Weight'] = mark_result['Weight'].apply(lambda x: round((x/rec)*100,2), 0)
        
        if plot:
            plotter.weights_plotter(self.weights,self.stocks,mark_result['SR'])

        
        if opt_result.message == 'Optimization terminated successfully.':
            return mark_result
        else:
            print('Optimization was not terminated successfully.')






























