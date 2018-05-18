from mpl_finance import candlestick_ohlc
from matplotlib import dates as mdates
from matplotlib import ticker as mticker
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def candle_plot(data):
    """
    Candlestick plotting for ohlc pandas dataframe


    Parameters
    ----------
    data : a pandas dataframe.
        A pandas dataaframe with ohlc and Adj. Close columns.


    Examples
    --------
    >>> from financePy import plotter
    >>> data = st.get_data_from_list(['AAPL','ATL.MI','BMW.DE'])

    """
    data['Da'] = data.index
    data.reset_index()
    data['date_ax'] = data['Da'].apply(lambda date: mdates.date2num(date))
    data_values = [tuple(vals) for vals in data[['date_ax', 'Open', 'High', 'Low', 'Close']].values]
    

    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    candlestick_ohlc(ax, data_values, width=0.6, colorup='g',colordown='r')
    
    
def scatter_plot(data_list, columns_names = False, cat = 'Close'):
    data_list = [data[cat] for data in data_list]
    df = pd.concat(data_list, axis = 1)
    if columns_names:
        df.columns = columns_names
    else:
        df.columns = ['Series #'+str(i) for i in range(len(data_list))]
    pd.plotting.scatter_matrix(df, alpha=0.2, diagonal='hist')
    
def weights_plotter(weights,tickers,colormapping = False):    
    fig, ax = plt.subplots()
    if type(colormapping) != type(False):
        ax.scatter( [i for i in range(len(weights))], weights, c = colormapping, cmap = 'Spectral')
    else:
        ax.scatter( [i for i in range(len(weights))], weights)
    ax.set_xticks([i for i in range(len(weights))])
    ax.set_xticklabels(tickers)
    ax.set_ylim(0, max(weights)+ np.mean(weights)/4)
    

def mov_avg_plot(ema, notifier = True, indicator = 'arrow'):
    
    for tick,single in list(ema.items()):
        if notifier:
            temp = single  
            min_y = min(temp.Close.min(),temp.iloc[:,0].min())-1
            max_y = max(temp.Close.max(),temp.iloc[:,-2].max())+1
            
            temp['noticool'] = temp.Notifier.diff().fillna(0)
            
            noticool = temp.apply( lambda x: x[temp.columns[0]] if x.noticool in [2,-2] else 0 , 1  )
            fig,ax = plt.subplots()
            temp.drop(columns = ['Notifier','noticool']).plot(ylim = (min_y,max_y), ax = ax, title = tick)
            ax.scatter(temp.index, noticool, c = temp.Notifier, cmap='RdYlGn', s = 50)
            if indicator == 'arrow':
                
                
                for index in noticool.index:
                    width = 12
                    lenght = (max_y-min_y)/15
                    if noticool[index] < temp.Close[index] and noticool[index] != 0:
                        ax.arrow(index,noticool[index],0,temp.Close[index]-noticool[index], head_width=width, head_length=lenght, fc='g', ec='g')
                    elif noticool[index] > temp.Close[index] and noticool[index] != 0:
                        ax.arrow(index,noticool[index],0,temp.Close[index]-noticool[index], head_width=width, head_length=lenght, fc='r', ec='r')
                
            elif indicator == 'line':
                ax.vlines(noticool[noticool != 0].index,min_y,max_y,'b','dashdot', alpha = 0.4, lw = 1 )
            else:
                raise ValueError('You used an inappropiate value for indicator, pls check the doc! (I know it\' boring but you really should)')


        else:
            single.plot(title = tick)

def boll_bands_plot(boll_bands, notifier = True):
    
    for tick,single in list(boll_bands.items()):
        if notifier:
            temp = single  
            min_y = min(temp.Close.min(),temp.iloc[:,0].min())-1
            max_y = max(temp.Close.max(),temp.iloc[:,-2].max())+1
            noticool = temp.apply( lambda x: x.Close+x['Notifier']/2 if x.Notifier == 1 else (x.Close+x.Notifier/2 if x.Notifier == -1 else 0) , 1  )
            fig,ax = plt.subplots()
            temp.drop('Notifier',1).plot(ylim = (min_y,max_y), ax = ax, title = tick)
            ax.scatter(temp.index, noticool, c = temp.Notifier, cmap='RdYlGn', s = 5)
        else:
            single.plot(title = tick)

