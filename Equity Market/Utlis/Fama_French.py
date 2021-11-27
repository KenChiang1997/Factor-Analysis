# basic
import numpy as np
import pandas as pd 
import datetime as dt 
from pandas_datareader import data as pdr 




class Ken_French_Library():
    """
    Fama/French 3 Factors [Weekly]
    Fama/French 3 Factors [Daily]
    """

    def __init__(self,start,periods):

        self.start = start 
        self.periods = periods
    
    def get_data(self):

        research_factors = pdr.DataReader('F-F_Research_Data_Factors_'+str(self.periods),
                                      'famafrench', start=self.start)[0] 

        momentum_factor = pdr.DataReader('F-F_Momentum_Factor_daily',
                                     'famafrench', start=self.start)[0]


        five_factors = research_factors.join(momentum_factor).dropna()
        five_factors /= 100.


        five_factors.columns = five_factors.columns.str.strip()
        self.five_factors = pd.DataFrame(five_factors)
        self.five_factors = self.five_factors[["Mkt-RF","SMB","HML","Mom"]]


        return self.five_factors
    

    def __len__(self):
        return self.five_factors.shape[0]



