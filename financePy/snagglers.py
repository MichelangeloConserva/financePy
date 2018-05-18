import pandas as pd
import numpy as np
from financePy import scraper as scr
from financePy import plotter

from scipy.optimize import minimize
from financePy import general_tools as gt
from financePy.estimators import finance_estimates as fe

"""
        traili_ret_freq:
            d,m,
        dividens : 
            
        splits:
            
        ownership:
            opt1 = ['OwnershipData','ConcentratedOwners','Buyers','Sellers']
            opt2 = ['mutualfund','institution']     
        executives:
            
        company_profile:
            
        realt_time_info      :

        complete_valuation    
                 
        current_valuation
        
        forward_valuation
        
        history_valuation
        
        financials
        
        key_ratio
        
        get_yield
"""

class Portfolio:
    def __init__(self,symbols , start_date = [2000,1,1], end_date=False, by = 'm', desider_data = 'all',country = 'united states',fundamentals = True, tecnicals = True, folder = False):
            
        if by.lower() in ['quandl','q']:
            self.by = 'q'
            self.tecnicals = scr.Q_data(symbols, start_date = start_date, end_date=end_date, folder = folder)
            self.symbols = list(self.tecnicals.keys())
            
        elif by.lower() in ['yahoo','y']:
            self.by = 'y'
            self.symbols = set()
            if tecnicals:
                temp = scr.Y_data(symbols, start_date = start_date, end_date=end_date, folder = folder)
                for key in list(temp.keys()):
                    temp[key] = temp[key]['historical']
                self.tecnicals = temp
                self.symbols.union( list(self.tecnicals.keys()))
            if fundamentals:
                self.fundamentals = scr.Y_data(symbols,desider_data, start_date = start_date, end_date=end_date, folder = folder)
                self.symbols.union( list(self.fundamentals.keys()))
                
        elif by.lower() in ['morningstar','m']:
            self.by = 'm'
            self.symbols = set()
            if fundamentals:
                print('Morningstar fundamentals')
                self.fundamentals = scr.MS_data(symbols,desider_data, folder = folder)
                self.symbols = self.symbols.union(list(self.fundamentals.keys()))
            if tecnicals:
                print('\nMorningstar tecnicals')
                temp = scr.MS_data(symbols,['historical'],start_date, end_date, folder = folder)
                for key in list(temp.keys()):
                    temp[key] = temp[key]['historical']
                self.tecnicals = temp
                self.symbols = self.symbols.union(list(self.tecnicals.keys()))
        else:
            raise ValueError('I think you entered an invalid argument for by :')
        
        if fundamentals and self.by != 'q':
            self.big_tree = {}
            for tick in self.fundamentals.keys():
                single = []
                for index in self.fundamentals[tick]:
                    temp = []
                    if type(self.fundamentals[tick][index]) == type({}):
                        for k in self.fundamentals[tick][index].keys():
                            for i in self.fundamentals[tick][index][k].index:
                                temp += ['%s~%s~%s' % (index,k,i)]
                    elif type(self.fundamentals[tick][index]) == type(pd.DataFrame()):
                        for i in self.fundamentals[tick][index].index:
                            temp += ['%s~%s' % (index,i)]
                    single += temp
                self.big_tree[tick] = single
     
#    def real_time(self, )

    def remove(self,symbol):
        self.symbols.remove(symbol)
        self.tecnicals.pop(symbol)
        try:
            self.fundamentals.pop(symbol)
        except:
            pass

    def screener(self,screeners, inplace = False):
        self.screened = {}
        for k,i in screeners.items():
            screen = k
            threshold  = i[0]
            up = i[1]
            if screen in ['Volume','Close','Open','High','Low']:
                # tecnicals
                self.screened['historical'] = {}
                if up:
                    percentile = np.percentile(np.array([self.tecnicals[x][screen].sum() for x in self.symbols]),100-threshold*100)
                    for x in list(self.symbols):
                        if self.tecnicals[x][screen].sum() < percentile and  inplace:
                            self.remove(x)
                        elif self.tecnicals[x][screen].sum() > percentile and not inplace:
                            self.screened['historical'][x] = self.tecnicals[x]
                                
                else:
                    percentile = np.percentile(np.array([self.tecnicals[x][screen].sum() for x in self.symbols]),threshold*100)
                    for x in list(self.symbols):
                        if self.tecnicals[x][screen].mean() > percentile and  inplace:
                            self.remove(x)   
                        elif self.tecnicals[x][screen].sum() < percentile and not inplace:
                            self.screened['historical'][x] = self.tecnicals[x]
            else:
                # fundamentals
                pass
    
            
    def bollinger_bands(self, cat = 'Close', window = 20, dropna = True, notifier = False, output = False, plot = False):
        bollinger_bands = {}
        for symbol in self.tecnicals.keys():
            bollinger_bands[symbol] = fe.bollinger_bands(self.tecnicals[symbol], cat = cat, window = window, dropna = dropna, notifier = notifier)
        self.boll_bands = bollinger_bands
        
        if plot:
            plotter.boll_bands_plot(self.boll_bands, notifier)
        
        if output:
            return bollinger_bands
    
    def EMA(self, windows_list = [35,70], cat = 'Close', plot = False, dropna = True, output = False, notifier = False):
        ema = {}
        for symbol in self.tecnicals.keys():
            ema[symbol] = fe.exp_mov_avg(self.tecnicals[symbol], windows_list = windows_list, cat = cat, dropna = dropna, notifier = notifier)
        self.ema = ema
        
        if plot:
            plotter.mov_avg_plot(ema,notifier)
        
        if output:
            return ema
            
        
    
    def markowits_allocation(self, minimun = 0.01, plot = False):
     
        symbols_list =  list(self.tecnicals.keys())
        prices = pd.concat([self.tecnicals[ticker].Close for ticker in symbols_list],1)
        prices.fillna(method='ffill', inplace = True)
        prices.columns = symbols_list
        log_ret = np.log(prices/prices.shift(1))
        
        constraints = ({'type' : 'eq', 'fun' : lambda x: np.sum(x)-1})
        bounds = [(0,1) for i in range(len(symbols_list))]
        init_guess = [ 1/len(symbols_list) for i in range(len(symbols_list))]
                
        neg_sharpe = lambda x,y : -1 * gt.get_ret_vol_SR(x,y)[2]
        opt_result = minimize(neg_sharpe, init_guess, args=(log_ret), method = 'SLSQP', bounds = bounds, constraints = constraints)
        self.weights  = opt_result.x[opt_result.x>minimun]/sum(opt_result.x)
        self.stocks = list(np.array(symbols_list)[opt_result.x>minimun])
        
        mark_result = pd.concat([pd.Series(self.stocks), pd.Series(self.weights)],1)
        mark_result.columns = ['Stock','Weight']
        mark_result['SR'] = mark_result['Stock'].apply(lambda x: self.tecnicals[x].Close.mean()/self.tecnicals[x].Close.std(),1)
        mark_result.set_index('Stock', inplace = True) 
        mark_result = mark_result.apply(lambda x: round(x,4),0)
        rec = float(mark_result['Weight'].sum())
        mark_result['Weight'] = mark_result['Weight'].apply(lambda x: round((x/rec)*100,2), 0)
        
        if plot:
            plotter.weights_plotter(self.weights,self.stocks,mark_result['SR'])

        
        if opt_result.message == 'Optimization terminated successfully.':
            return mark_result
        else:
            print(opt_result.message)
            return opt_result





























