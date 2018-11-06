# -*- coding: utf-8 -*-

import statsmodels.api as sm
import pandas as pd
import numpy as np

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from pandas.tseries.offsets import DateOffset


def stationary_check(time_serie):
    pass


def arima_model(time_serie, model = 'additive', plot = True, dropna = False):
    
    decomp = seasonal_decompose(time_serie, model = model)
    if plot:
        decomp.plot()
    if dropna:
            return pd.concat({'Observed' : decomp.observed, 'Trend' : decomp.trend, 'Seasonal' : decomp.seasonal, 'Residual' : decomp.resid}, 1).dropna()
    else:
            return pd.concat({'Observed' : decomp.observed, 'Trend' : decomp.trend, 'Seasonal' : decomp.seasonal, 'Residual' : decomp.resid}, 1)
