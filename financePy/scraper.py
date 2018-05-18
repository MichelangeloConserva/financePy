import datetime as __dt__
import pandas as __pd__
import quandl as __quandl__
import os as __os__
import re as __re__

from financePy import general_tools as __gt__
from financePy.scrapers.yahoo import tools as __ytools__
from financePy.scrapers.morningstar import tools as __mtools__
from financePy.scrapers.quandl import tools as __qtools__
from financePy.scrapers.reuters import tools as __rtools__
from financePy.scrapers.forge import tools as __ftools__

__TIME_ESTIMATOR__ = 0.6
__TIME_ESTIMATOR_OWN__ = 1.2

def F_data(symbols,path):
    credentials = pd.read_csv(path + 'forge/credential.csv')

    



def MS_data(symbols,desired_data, start_date = [2017,1,1], end_date = False,
            traili_ret_freq = 'd', own_opt =[['OwnershipData'], ['mutualfund']],
            exe_opt = ['keyExecutives'], fin_cat = ['bs'],fin_frequen= 'annual',
            folder = False, folder_path = 'current_data' ): 
    """
        trailing_returns:
            d,m,
        dividens : 
            
        splits:
            
        ownership:
            opt1 = ['OwnershipData','ConcentratedOwners','Buyers','Sellers']
            opt2 = ['mutualfund','institution']     
        executives:
            
        company_profile:
            
        real_time_info      :

        complete_valuation    
                 
        current_valuation
        
        forward_valuation
        
        history_valuation
        
        financials
        
        key_ratio
        
        get_yield
    """
    
    fundamental_comb =  {'key_ratio': ['Profitability','Key Ratios -> Growth','Margins % of Sales','Cash Flow Ratios','Financials','LiquidityFinancial Health','Balance Sheet Items (in %)','Efficiency'],
                         "ownership" : ["('OwnershipData', 'mutualfund')"],
                         'financials'  : ['bs'],
                         'splits' :  ['splitHistory']}
                            
    
    if desired_data == 'all':
        desired_data = ['trailing_returns', 'dividens', 'splits', 'ownership','executives', 'company_profile', 'real_time_info','complete_valuation',
                        'current_valuation', 'forward_valuation', 'history_valuation', 'financials', 'key_ratio', 'get_yield']
    
    if type(desired_data) != type([]):
        raise TypeError('Could you please entry a list for desidered_data? Thank you very much my friend')
        
    if type(symbols) == type(__pd__.Series()):
        symbols = __pd__.DataFrame(symbols).transpose()
    elif type(symbols) != type(__pd__.DataFrame()):
        raise TypeError('Could you please entry a the right pandas Dataframe for symbols? Thank you very much my friend')    
    
#    data = {}    
#    if __os__.path.exists(folder_path+'/'):
#        for ticker in symbols.performanceId.tolist():
#            name = symbols[symbols.performanceId == ticker].securityName.values[0]
#            if  __os__.path.exists(folder_path+'/'+name):
#                for desired in desired_data:
#                    if __os__.path.exists(folder_path+'/'+name +'/'+ desired +'.csv'):
#                        temp = __pd__.read_csv(folder_path+'/'+name +'/'+ desired +'.csv')
##                        temp.set_index(columns = [temp.columns[0]], inplace = True)
#                        data[ticker] = temp
    data = {}
    problems = []
    for ticker in symbols.performanceId.tolist():
        name = symbols[symbols.performanceId == ticker].instrumentId.values[0]
        data[name] = {}

        if  __os__.path.exists(folder_path+'/'+name):
            for desired in desired_data:
                
                if __os__.path.exists(folder_path+'/'+name +'/'+ desired +'.txt'):
                        data[name][desired] = {}
                
                elif desired in fundamental_comb.keys():
                    if __os__.path.exists(folder_path+'/'+name +'/'+ desired ):
                        data[name][desired] = {}

                        for index in fundamental_comb[desired]:
                            if __os__.path.exists(folder_path+'/'+name +'/'+ desired +'/' + index +'.csv' ):
                                temp = __pd__.read_csv(folder_path+'/'+name +'/'+ desired+'/'+ index +'.csv')
                                temp.set_index(temp.columns[0], inplace = True)
                                data[name][desired][index] = temp
                                
                                
                            elif __os__.path.exists(folder_path+'/'+name +'/'+ desired +'/' +index +'.txt' ): 
                                data[name][desired][index] = {}
                else:    
                    if __os__.path.exists(folder_path+'/'+name +'/'+ desired +'.csv'):
                        temp = __pd__.read_csv(folder_path+'/'+name +'/'+ desired +'.csv')
                        temp.set_index(temp.columns[0], inplace = True)
                        if desired == 'historical':
                            temp.index = __pd__.to_datetime(temp.index)
                            temp.index.name = ''
                        else:
                            pass
                        data[name][desired] = temp

        
        
    
    if not __os__.path.exists(folder_path+'/') and folder:
        __os__.makedirs(folder_path+'/')   
                
    l = len(desired_data)*len(symbols)
    print('Estimated time: '+str(l*__TIME_ESTIMATOR__) + 's' if 'ownership' not in desired_data else 'Estimated time: '+str(round(l*__TIME_ESTIMATOR_OWN__,1)) + 's')
    i = 0
    __gt__.printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    
    for ticker in symbols.performanceId.tolist():
        name = symbols[symbols.performanceId == ticker].instrumentId.values[0]

        if folder:
            if not __os__.path.exists(folder_path+'/'+name):
                    __os__.makedirs(folder_path+'/'+name)    
        for desired in desired_data:
            __gt__.printProgressBar(i + 1, l, prefix = 'Getting Morningstar data: %s ' % desired  + ' '*(30-len(desired)), suffix = name, length = 50)
            i += 1   
            if desired not in data[name].keys():
                exec('data[name][desired] = __mtools__.%s(ticker,{"traili_ret_freq":traili_ret_freq,"own_opt":own_opt,"exe_opt":exe_opt,"fin_cat":fin_cat,"fin_frequen":fin_frequen,"start_date":start_date,"end_date":end_date})' % desired )
                if type(data[name][desired]) == type(''):
                    data[name].pop(desired)
                    problems += [name+'/'+desired]
                else:
                    if folder:
                        if type(data[name][desired]) == type({}):
                            if not __os__.path.exists(folder_path+'/'+name+'/'+desired):
                                    __os__.makedirs(folder_path+'/'+name+'/'+desired) 
                            for key in data[name][desired].keys():
                                data[name][desired][key].to_csv(folder_path+'/'+name +'/'+ desired +'/'+str(key).replace('/','') +'.csv')
                        else:
                            data[name][desired].to_csv(folder_path+'/'+name +'/'+ desired +'.csv', header = True)
                        
    for key in list(data.keys()):
        if data[key] == {}:
            data.pop(key)
        else:
            for key_inn in list(data[key].keys()):
                if dict(data[key][key_inn]) == {}:
                    data[key].pop(key_inn)
            
    
     
    if len(problems) != 0:
        for problem in problems:
            f = open( folder_path+'/'+problem+'.txt','a')
            f.close()
            
            
    return data



def R_fundamentals(symbols, country):
    print('THIS MODULE IS IN ALPHA AND MAY NOT WORK')
    fundamentals = {}
    if country.lower().replace(' ','') in ['italy', 'it']:
        
        l = len(symbols)
        i = 0
        __gt__.printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
        
        for sym in symbols:
            fundamentals[sym] = __rtools__.get_financials_IT(sym)
            __gt__.printProgressBar(i + 1, l, prefix = 'Getting Reuters fundamental :', suffix = sym, length = 50)
            i += 1
            return fundamentals
    else:
        raise ValueError('I\' so sorry but I am able to get this data for italian tickers only')

def Q_data(symbols,start_date = [2000,1,1], end_date=False, frequency = '1d', folder = False, folder_path = 'current_data'):
    """
    """
    frequency = frequency.lower()
    if frequency in ['1d','daily']:
        frequency = 'daily'
    elif frequency in ['m','monthly']:
        frequency = 'monthly'
    elif frequency in ['q','quarterly']:
        frequency = 'quarterly'
    elif frequency in ['a','annual']:
        frequency = 'annual'
    else:
        raise ValueError('Wrong frequency, pls visit http://a.memegen.com/jy0j99.gif')

    start_date,end_date = __gt__.dates_checker(start_date,end_date,'-')
        
    if type(symbols) == type(__pd__.Series()):
        symbols = symbols.tolist()
        
    l = len(symbols)
    data = {}

    __gt__.printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for i in range(len(symbols)):
        symb = symbols[i].split('/')[1]
        data[symb] = __quandl__.get(symbols[i], start_date = '2017-01-01', end_date ='2018-01-01', collapse = frequency )
        if len(data[symbols[i][5:]].index) == 0:
            data.pop(symb)
        __gt__.printProgressBar(i + 1, l, prefix = 'Getting Quandl historical :', suffix = symbols[i], length = 50)

    if folder:    
        if not __os__.path.exists(folder_path+'/'):
            __os__.makedirs(folder_path+'/')
        
    for df in data.keys():
        data[df].to_csv(folder_path+'/'+df+'.csv',index = False)

    return data



def Y_data(symbols ,desired_data = ['historical'], start_date = [2000,1,1], end_date=False ,frequency = '1d', folder = True, folder_path = 'current_data'):
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
    folder_path : a string
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
    
    if desired_data == 'all':
        desired_data = ['historical','summary', 'similars_score', 'statistics', 'financials']
    
    frequency = frequency.lower()
    if frequency in ['1d','daily']:
        frequency = 'daily'
    elif frequency in ['m','monthly']:
        frequency = 'monthly'
    elif frequency in ['q','quarterly']:
        frequency = 'quarterly'
    elif frequency in ['a','annual']:
        frequency = 'annual'
    else:
        raise ValueError('Wrong frequency, check the doc for the available values')
    
    result = {}
    for symbol in symbols:
        result[symbol] = {}
        if  __os__.path.exists(folder_path+'/'+symbol):
            for fun in desired_data:
                if __os__.path.exists(folder_path+'/'+symbol +'/'+ fun +'.csv'):   
                    temp = __pd__.read_csv(folder_path+'/'+symbol +'/'+ fun +'.csv')
                    temp.set_index(temp.columns[0], inplace = True)
                    try:
                        temp.index = __pd__.to_datetime(temp.index)
                        temp.index.name = ''
                    except:
                        pass
                    result[symbol][fun] = temp
    
            
    if not __os__.path.exists(folder_path+'/') and folder:
        __os__.makedirs(folder_path+'/') 
        
    start_date,end_date = __gt__.dates_checker(start_date,end_date)
    
    problems = []
    symbols = list(map(lambda x: symbols.remove(x) if '.TI' in x else x, symbols))
    while None in symbols:
        symbols.remove(None)
    l = len(symbols) * len(desired_data)
    i = 0
    __gt__.printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)

    for symbol in symbols:
        
        if folder:
            if ( folder_path == None or symbol == None):
                print('\n\n\n')
                print(symbols)
                print(folder_path)
                print('\n\n\n')
            if not __os__.path.exists(folder_path+'/'+symbol):
                    __os__.makedirs(folder_path+'/'+symbol)  
                    
        for fun in desired_data:
            i += 1
            __gt__.printProgressBar(i, l, prefix = 'Getting Yahoo data, %s :' % fun, suffix = symbol , length = 50)
            if fun not in result[symbol].keys():
                exec('result[symbol]["%s"] = __ytools__.%s(symbol,start_date,end_date,frequency)' % (fun,fun))
                if type(result[symbol][fun]) == type(''):
                    problems += [result[symbol][fun]]
                    result[symbol].pop(fun)
                    continue
                if folder:
                    if type(result[symbol][fun]) == type({}):
                            if not __os__.path.exists(folder_path+'/'+symbol+'/'+fun):
                                    __os__.makedirs(folder_path+'/'+symbol+'/'+fun) 
                            for key in result[symbol][fun].keys():
                                try:
                                    result[symbol][fun][key].to_csv(folder_path+'/'+symbol +'/'+ fun +'/'+str(key).replace('/','') +'.csv')
                                except:
                                    return symbol,fun
                    else:
                        result[symbol][fun].to_csv(folder_path+'/'+symbol +'/'+ fun +'.csv')
                    
    for key in list(result.keys()):
        if result[key] == {}:
            result.pop(key)        
    if ['historical'] == desired_data:        
        for key in result.keys():
            temp  = result[key]['historical'].apply( lambda x: sum(x.isna()), 0)
            if sum(temp) > 0:
                result[key]['historical'] = result[key]['historical'].fillna(method = 'ffill')
#        
#    if folder:    
#        for symbol in result.keys():  
#            if not __os__.path.exists(folder_path+'/'):
#                __os__.makedirs(folder_path+'/')
#            for df in result[symbol].keys():
#                if not __os__.path.exists(folder_path+'/'+symbol):
#                    __os__.makedirs(folder_path+'/'+symbol)
#                result[symbol][df].to_csv(folder_path+'/'+symbol +'/'+ df +'.csv')

        f = open(folder_path+'/'+'missing.txt', 'w')
        for missed in problems:
            f.write(missed+'\n')
        f.close()

    return result


# ROBACCIA   
#        if symbol == None:
#            symbols.remove(None)
#        else:
#            num_space = 15-len(symbol)
#            data[symbol] = __gt__.timeout(__ytools__.get_historical, (symbol,start_date,end_date, '1d'), timeout_duration = 5)
#            if type(data[symbol]) == type(__pd__.DataFrame()):
#                i += 1
#                __gt__.printProgressBar(i, l, prefix = 'Progress:', suffix = symbol +' '*num_space+' done', length = 50)
#            elif data[symbol] == -1:
#                data.pop(symbol)
#                i += 1
#                __gt__.printProgressBar(i, l, prefix = 'Progress:', suffix = symbol +' '*num_space+ 'removed', length = 50)            
#            else:
#                data.pop(symbol)
#                not_yet.append(symbol)
#                i += 1
#                __gt__.printProgressBar(i, l, prefix = 'Progress:', suffix = symbol +' '*num_space+ 'not yet', length = 50) 
#            
#    while len(not_yet) >0:
#        if (__dt__.datetime.now() - first).total_seconds() < max_time:
#            print('Time finished\nReturning the dataframe I got')
#            break
#        for symbol in not_yet:
#            data[symbol] = __gt__.timeout(__ytools__.get_historical, (symbol,start_date,end_date, frequency), timeout_duration = 60)
#            if type(data[symbol]) == type(__pd__.DataFrame()):
#                num_space = 15-len(symbol)
#                i += 1
#                __gt__.printProgressBar(i, l, prefix = 'Progress:', suffix = symbol +' '*num_space+ 'done', length = 50) 
#                not_yet.remove(symbol)
#
#    for i in list(data.keys()):
#        if type(data[i]) != type(__pd__.DataFrame()) or not len(data[i]) > 1:
#            data.pop(i)
#    
