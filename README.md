# financePy
A very high-level finance package

if you want the plotter to work correctly you need to manually install
```
pip3 install https://github.com/matplotlib/mpl_finance/archive/master.zip
```
you might need to install:
```
sudo apt-get install python3-tk
```


The raccomeded installation commandand is:
```
sudo python3 -m pip install git+https://github.com/MichelangeloConserva/financePy.git --user
```


# This is an example of using the package


## SCRAPER TOOL

The needed imports are:
~~~~
from financePy import scraper as scr
from financePy import snagglers as sna
from financePy.scrapers.yahoo import tools as __ytools__
from financePy.scrapers.morningstar import tools as __mtools__
from financePy.scrapers.quandl import tools as __qtools__
~~~~
### Morningstar

the available tickers for this source are:
* 'united states'
* 'italy'
* 'germany'

I' add others asap

~~~~
ita_tickers = __mtools__.tickers('italy')                    # using the API to get all the tickers in italy
test_tickers = ita_tickers.iloc[[1,123,100,45,10,5], : ]     # choosing some
start_date,end_date = '2017-1-1','2018-04-10'                # defining start and stop
desired = ['key_ratio','historical', 'dividens', 'splits', 'ownership','executives', 'company_profile', 'real_time_info','complete_valuation', 'current_valuation', 'forward_valuation', 'history_valuation']   # these are the information we want to scrape
m_scraped = scr.MS_data(test_tickers,desired)   
~~~~


## yahoo

Almost all tickers on yahoo finance are available

~~~~
yahoo = __ytools__.tickers()                         # getting a pandas dataframe containing more than 100000 tickers informations
usa_yahoo = yahoo[yahoo.country == 'USA'].ticker            # you can get tickers from a specific country
ita_yahoo = yahoo[yahoo.country == 'Italy'].ticker
china_yahoo =  yahoo[yahoo.country == 'China'].ticker  
test = ['EURUSD=X','AAPL','AATL.MI']                         #or you can define your list of tickers by yourself
china_test = china_yahoo.iloc[[1,3,4,76,45,500,36]].tolist()
start_date,end_date = '2017-1-1','2018-04-10'
y_scraped = scr.Y_data(china_test,'all',start_date,end_date)
~~~~

## quandl
~~~~
quandl_tickers = __qtools__.tickers()                # pandas dataframe for all quandl tickers
quandl_test = quandl_tickers.iloc[[1,2,3,234,543,2,345,678,532],0].tolist()
start_date,end_date = '2017-1-1','2018-04-10'
q_scraped = scr.Q_data(quandl_test,start_date)
~~~~



### SNAGGLER ###
Snaggler is a tool which let you create in a very simple way a portfolio of tickers you are interested in and let you do simple analysis and plot

### morningstar
~~~~
usa_tickers = __mtools__.tickers('united states')      
test_tickers = usa_tickers.iloc[[1,2,32,233,3,4,32,11,23,4444], : ] 
start_date,end_date = '2017-1-1','2018-04-10'
portfolio = sna.Portfolio(test_tickers,start_date,end_date,'m','all', fundamentals=True)
symbols = list(portfolio.symbols)
m_tecn = portfolio.tecnicals
m_fund = portfolio.fundamentals

portfolio.bollinger_bands(notifier = True , plot = True)
portfolio.EMA(notifier = True, plot = True)
plotter.candle_plot(portfolio.tecnicals[symbols[3]])
m_markowitz_alloc = portfolio.markowits_allocation(plot = True)
~~~~

### yahoo
~~~~
yahoo_ticker = __ytools__.tickers()
test_tickers = yahoo_ticker.iloc[[1,103835,60000,70000,80000,90010,221,345,22,333,4321,554]]
start_date,end_date = '2017-1-1','2018-04-10'
portfolio = sna.Portfolio(test_tickers.ticker,start_date,end_date,'yahoo','all', folder = True)
y_tecn = portfolio.tecnicals
y_fund= portfolio.fundamentals
portfolio.bollinger_bands(notifier = True , plot = True)
portfolio.EMA(notifier = True, plot = True)
y_markowitz_alloc = portfolio.markowits_allocation(plot = True)
~~~~

### quandl
~~~~
quandl_tickers = __qtools__.tickers()
start_date,end_date = '2017-1-1','2018-04-10'
test_ticker = quandl_tickers.iloc[[1,2,500,233,3,4,32,11,23,22], 0 ] 
portfolio = sna.Portfolio(test_ticker,start_date,end_date,'q','all', folder = True)
q_tecn = portfolio.tecnicals
portfolio.bollinger_bands(notifier = True , plot = True)
portfolio.EMA(notifier = True, plot = True)
q_markowitz_alloc = portfolio.markowits_allocation(plot = True)
~~~~





I'm working on tons of other features and I'm quite excited about the results I achieved until now.
The only thing I ask you is to send me e-mail michelangelo.conserva@protonmail.com or add me on facebook www.facebook.com/michelangelo.conserva to tell me your opinion and give suggestions.







