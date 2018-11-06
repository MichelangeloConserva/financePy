import snagglers as sna
import scraper as st
import plotter

start_date = [2017,1,1]
end_date = [2018,3,15]

tickers = st.get_yahoo_tickers()
italy = tickers.ticker[tickers.country == 'Italy']

b = sna.Portfolio(['ATL.MI','BRE.MI','ENEL.MI'], start_date, end_date, by = 'yahoo', max_time=10*60 )

prova = st.get_fundamentals_IT(tickers[tickers.ticker == 'ATL.MI'].ticker.tolist()[0])
