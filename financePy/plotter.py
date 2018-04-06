from matplotlib.finance import candlestick_ohlc
from matplotlib.dates import DateFormatter, date2num, WeekdayLocator, DayLocator, MONDAY
import matplotlib.pyplot as plt
import pandas as pd


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
    data['date_ax'] = data['Da'].apply(lambda date: date2num(date))
    data_values = [tuple(vals) for vals in data[['date_ax', 'Open', 'High', 'Low', 'Close']].values]
    
    mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
    alldays = DayLocator()              # minor ticks on the days
    weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
    
    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)
#    ax.xaxis.set_major_locator(mondays)
#    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_formatter(weekFormatter)
    
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
        ax.scatter( [i for i in range(len(weights))], weights, c = colormapping, cmap = 'Reds')
    else:
        ax.scatter( [i for i in range(len(weights))], weights)
    ax.set_xticks([i for i in range(len(weights))])
    ax.set_xticklabels(tickers)
    ax.set_ylim(0, max(weights)+0.01)
    

def mov_avg_plot(ema, notifier = False):
    
    for tick,single in list(ema.items()):
        if notifier:
            fig,ax = plt.subplots(2,1, sharex = True, gridspec_kw = {'height_ratios':[5, 1]})
            fig.subplots_adjust(hspace=0.25)
            ax[0].set_title(tick,{'fontsize': 20})
            ax[0].plot(single.iloc[:,:single.shape[1]-1])
            ax[0].get_xaxis().set_visible(False)
            ax[1].set_title('Notifier', {'fontsize': 10})
            ax[1].scatter(single.index,single.Notifier, s = 1, c = 'red', marker = 's' )
            ax[1].set_ylim(-2,2)
        else:
            single.plot()

def boll_bands_plot(boll_bands, notifier = False):
    
    for tick,single in list(boll_bands.items()):
        if notifier:
            fig,ax = plt.subplots(2,1, sharex = True, gridspec_kw = {'height_ratios':[5, 1]})
            fig.subplots_adjust(hspace=0.25)
            ax[0].set_title(tick,{'fontsize': 20})
            ax[0].plot(single.iloc[:,:3])
            ax[0].get_xaxis().set_visible(False)
            ax[1].set_title('Notifier', {'fontsize': 10})
            ax[1].scatter(single.index,single.Notifier, s = 1, c = 'red', marker = 's' )
            ax[1].set_ylim(-2,2)
        else:
            single.plot()














    