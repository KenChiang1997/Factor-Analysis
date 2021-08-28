# basic
import math
import warnings
import numpy as np 
import pandas as pd 
import datetime as dt 
import yfinance as yf 
from pandas_datareader import data as pdr 
warnings.filterwarnings("ignore")

# statsmodel.api 
import statsmodels.api as sm 
from statsmodels import stats

# matplotlib
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates




class Company_Intra_date_Volume_Data():

    def __init__(self,tickers,period,interval):

        self.tickers  = tickers 
        self.period   = period 
        self.interval = interval
    
    def get_data(self,ticker):

        self.data = yf.download(ticker,period=self.period,interval=self.interval ) .reset_index()

        return self.data
    

    
    def get_volume_data(self):

        for i , ticker in enumerate(self.tickers) : 
            
            if i == 0 :
                Volume_DF = self.get_data(ticker)
                Volume_DF = Volume_DF[['Datetime','Volume']]
                Volume_DF.columns = ['Datetime',str(ticker)]

            else:
                Merge_DF = self.get_data(ticker)[['Datetime','Volume']]
                Merge_DF.columns = ['Datetime',str(ticker)]
                Volume_DF = Volume_DF.merge(Merge_DF,how='outer')
        
        Volume_DF       = Volume_DF.fillna(value=0)
        Volume_DF.index = Volume_DF['Datetime']
        Volume_DF       = Volume_DF.drop(['Datetime'],axis=1)
        
        return Volume_DF



period   = '1d'
interval = '5m'
tickers  =  ['FB','AAPL']

# ------------ ------------ ------------ ------------ 

if __name__ == '__main__':

    Volume_Data = Company_Intra_date_Volume_Data(tickers=tickers,period=period,interval=interval)
    Volume_DF   = Volume_Data.get_volume_data()
    print(Volume_DF)

