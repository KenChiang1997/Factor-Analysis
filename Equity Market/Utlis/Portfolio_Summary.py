import numpy as np 
import pandas as pd 
import datetime as dt
import statsmodels.api as sm
from pandas_datareader import data as pdr 

import matplotlib.pyplot as plt
import matplotlib.dates as mdates 

# ------------------------- Portfolio Summary Raio ------------------------ 

class Portfolio_Summary():

    def Annual_Return(Daily_Returns):
        
        return np.mean(Daily_Returns) * 252

    def Annual_Volitiliy(Daily_Returns):

        return np.std(Daily_Returns) * np.sqrt(252)

    def Cumulative_Return(Daily_Returns):

        return np.cumsum(Daily_Returns)[-1]

    def Sharpe_Ratio(Daily_Returns):

        u = np.mean(Daily_Returns) * 252
        sigma = np.std(Daily_Returns) * np.sqrt(252)

        sharpe_ratio = u/sigma

        return sharpe_ratio
        
    def Maximun_drawdown(Daily_Returns):

        max_drawdown = max(pd.Series(np.cumsum(Daily_Returns)).cummax().values - np.cumsum(Daily_Returns))
        
        return max_drawdown

    def Calmar_Ratio(Daily_Returns):

        u = np.mean(Daily_Returns) * 252
        max_drawdown = max(pd.Series(np.cumsum(Daily_Returns)).cummax().values - np.cumsum(Daily_Returns))

        Calmar_Ratio = u/max_drawdown

        return Calmar_Ratio

    def Omega_Ratio(Daily_Returns,benchmark):

        Number_of_Win = len(np.where(Daily_Returns - benchmark > 0)[0])
        Number_of_Loss = len( np.where(Daily_Returns - benchmark < 0)[0])

        return Number_of_Win / Number_of_Loss

    def Sortino_Ratio(Daily_Returns,benchmark):

        Adjusted_Return = np.mean(Daily_Returns - benchmark) * 252
        benchmark_std   = np.std(benchmark) * np.sqrt(252)
        Sortino_Ratio   = Adjusted_Return / benchmark_std

        return Sortino_Ratio 

    def Value_at_Risk(Daily_Returns,confidence_level=0.95):

        type_1 = 1 - confidence_level
        var    = np.quantile(Daily_Returns,type_1)
            
        return  var

def Backtest_Summay_DF(start_date,end_date,Daily_Returns,Benchmark_Returns):


    BackTesint_Summary_Df = pd.DataFrame({

        "Start Date"        : [start_date] , 
        "End   Date"        : [end_date]   , 
        "-"                 : ["-"] ,
        "Annual Return"     : [Portfolio_Summary.Annual_Return(Daily_Returns)]         , 
        "Annual Volitiliy"  : [Portfolio_Summary.Annual_Volitiliy(Daily_Returns)]      , 
        "Cumulative Return" : [Portfolio_Summary.Cumulative_Return(Daily_Returns)]     ,
        "Sharpe Ratio"      : [Portfolio_Summary.Sharpe_Ratio(Daily_Returns)]          ,
        "Calmar Ratio"      : [Portfolio_Summary.Calmar_Ratio(Daily_Returns)]          ,
        "Omega Ratio"       : [Portfolio_Summary.Omega_Ratio(Daily_Returns,Benchmark_Returns)]           ,
        "Sortino Ratio"     : [Portfolio_Summary.Sortino_Ratio(Daily_Returns,Benchmark_Returns)]         ,

        "Daily Value at Risk"   : [ Portfolio_Summary.Value_at_Risk(Daily_Returns,confidence_level=0.95)    ]     ,
        "Maximum Drawdown"      : [ Portfolio_Summary.Maximun_drawdown(Daily_Returns)]                            ,
        

    },index=["Backtest"])


    return  BackTesint_Summary_Df.T

# ------------------------- Market'Beta (Fama-franch + Momentum) ------------------------- 

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

        factors = research_factors.join(momentum_factor).dropna()
        factors /= 100.
        factors.index   = factors.index.tz_localize('utc')

        factors.columns = factors.columns.str.strip()

        self.factors = pd.DataFrame(factors)
        self.factors = self.factors.reset_index()
        self.factors['Date'] = self.factors.apply(lambda x : self.Address_Date(x['Date']),axis=1)
        self.factors.index   = self.factors['Date']
        self.factors         = self.factors.drop(['Date'],axis=1)
        
        return self.factors
    
    def Address_Date(self,date):
        
        date = str(date)
        return date[:10]
        

    def __len__(self):
        return self.five_factors.shape[0]

def Address_Date(date):
    
    date = str(date)
    
    return date[:10]

def Construct_Regression_Df(BacKTesting_DF): 
    
    # Fama French Data
    Fama_French   = Ken_French_Library(start=dt.datetime(2018,1,2),periods='Daily')
    FF_DF         = Fama_French.get_data().reset_index()

    # Regression Data
    Portfolio_Returns_df          = BacKTesting_DF['Portfolio Daily Return'].dropna().reset_index(name='Portfolio Daily Returns')
    Portfolio_Returns_df ['Date'] = Portfolio_Returns_df .apply(lambda x : Address_Date(x['Date']),axis=1)
    Portfolio_Returns_df .index   = Portfolio_Returns_df['Date']
    Portfolio_Returns_df          = Portfolio_Returns_df .drop(['Date'],axis=1)
    
    Regression_df         = pd.merge(FF_DF,Portfolio_Returns_df,left_on='Date',right_on='Date')
    Regression_df.index   = Regression_df['Date']
    Regression_df         = Regression_df.drop(['Date'],axis=1)

    return Regression_df

def Rolling_Factor(Regression_df,Windows):

    Factor = ['Mkt-RF','SMB','HML','Mom']

    Y_rolling = Regression_df['Portfolio Daily Returns'].rolling(window=Windows)
    X_rolling = Regression_df[Factor].rolling(window=Windows)

    Market_Factor_Beta = pd.DataFrame()
    Index = []

    for x,y in zip(X_rolling,Y_rolling) :

        x = sm.add_constant(x.values)
        index = y.index[-1]
        y     = y.values 


        if x.shape[0] >= Windows : 

            Index.append(index)
            model  = sm.OLS(y,x)
            res    =  model.fit()
            params = res.params
            params = pd.Series(params)
            Market_Factor_Beta = Market_Factor_Beta.append(params,ignore_index=True)


    cols = ['Alpha']
    cols.extend(Factor)

    Market_Factor_Beta.columns = cols
    Market_Factor_Beta.index   = Index  

    return Market_Factor_Beta

def Plot_Market_Beta(Market_Factor_Beta):

    plt.subplots(figsize=(23,10))
    cols   = Market_Factor_Beta .columns
    ax1 = plt.subplot2grid((6,1),(0,0),rowspan=4,colspan=1)

    ax1.title.set_text( 'Rolling Factor : '+str(cols.to_list()) )
    for i in range(1,Market_Factor_Beta.shape[1]):
        ax1.plot(Market_Factor_Beta.index , Market_Factor_Beta[str(cols[i])],label=str(cols[i]))

    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=50))
    plt.axhline(0,linestyle="--",color='black',alpha=0.5)
    plt.ylabel('Market Beta')
    plt.legend()

    ax2 = plt.subplot2grid((6,1),(4,0),rowspan=3,colspan=1)
    ax2.plot(Market_Factor_Beta.index , Market_Factor_Beta[str(cols[0])],label=str(cols[0]))

    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=50))
    plt.axhline(0,linestyle="--",color='black',alpha=0.5)
    plt.ylabel('Alpha')
    plt.xlabel('Date')
    plt.legend()
    plt.show()

def Portfolio_Beta(BacKTesting_DF,Windows):

    Regression_df      = Construct_Regression_Df(BacKTesting_DF)
    Market_Factor_Beta = Rolling_Factor(Regression_df,Windows)
    Plot_Market_Beta(Market_Factor_Beta)

# ------------------------- Portfolio Drawdown ------------------------ 

def Check_Date_Valid(date):
    
    if date > dt.datetime.now():
        
        return "Not Yet Recover"

    else :

        return str(date)[:10]

def create_drawdowns(equity_curve):

    """
    Calculate the largest peak-to-trough drawdown of the PnL curve
    as well as the duration of the drawdown. Requires that the 
    pnl_returns is a pandas Series.

    Parameters :
    peak          - A pandas Series representing period percentage returns.
    equity_curve  - portfolio market values
    hwm           - portfolio market values peak values
    cur_hwm       - updated newest market values peak

    Function Return :

    drawdown_df            - Contain Daily drawdown , Daily Last Peak Portfolio Values , Whether Recovery ( Recovery Date )
    Top_5_Periods_Drawdown - Sort drawdown_df values by drawdown values , and Select Top 5 .

    """

    # Calculate the cumulative returns curve 
    # Then create the drawdown and duration series
    peak    = [0]
    eq_idx = equity_curve.index

    
    peak_dates          = [np.NAN]
    peak_values         = pd.Series(index = eq_idx)

    drawdown            = pd.Series(index = eq_idx)
    drawdown_duration   = pd.Series(index = eq_idx)
    recovery_duration   = [0]

    # Loop over the index range ( record historical peak date and construct maximun drawdown )
    for t in range(1, len(eq_idx)):

        peak.append( max(peak[t-1] , equity_curve[t]) )                                   # compare wheather current peak values is bigger than the previous one 

        peak_values[t]          = peak[t]
        drawdown[t]             = peak[t] - equity_curve[t]                               # lastest peak minus current equity values = current drawdown
        drawdown_duration[t]    = 0 if drawdown[t] == 0 else drawdown_duration[t-1] + 1   # updated duration periods 

        # (1.) recovery_duration
        recovery_duration.append(drawdown_duration[t])
        if drawdown_duration[t] == 0 :

            periods_duration = drawdown_duration[t-1]
   
            if periods_duration != 0 :
                
                try:
                    recovery_duration[t-int(periods_duration):t] = reversed(recovery_duration[t-int(periods_duration):t])
                except:
                    pass
            
    
        # (2.) find peak date 
        peak_index     = equity_curve.to_list().index(peak[t])
        peak_dates .append( equity_curve.reset_index().iloc[peak_index].Date )
        


    # ---- output df 
    drawdown_df = pd.DataFrame()
    drawdown_df['Equity Values']         = equity_curve
    drawdown_df['Drawdown Value']        = drawdown
    drawdown_df['Drawdown Percentage']   = (drawdown / peak_values) * 100 
    drawdown_df['Drawdown duration']     = drawdown_duration
    drawdown_df['Peak Date']             = peak_dates
    drawdown_df['Peak Equity Values']    = peak_values
    drawdown_df['Recovery duraton']      = recovery_duration
    
    drawdown_df                  = drawdown_df.reset_index()
    recover_date                 = [ drawdown_df['Date'][i] + pd.Timedelta(days=drawdown_df['Recovery duraton'][i]) for i in range(drawdown_df.shape[0]) if type(drawdown_df['Recovery duraton'][i]) != np.NaN ]
    drawdown_df['Recovery Date'] = recover_date

    # ---- Top 5 drawdown periods 
    Top_5_Drawdown = pd.merge(drawdown_df.reset_index(drop=True),drawdown_df.groupby(['Peak Date'])['Drawdown Value'].max().reset_index(name='Drawdown Value')).sort_values(by='Drawdown Value',ascending=False).reset_index(drop=True)[:5]
    Top_5_Drawdown['Recovery Date'] = Top_5_Drawdown.apply(lambda x : Check_Date_Valid(x['Recovery Date']),axis=1)

    return drawdown_df , Top_5_Drawdown

def Underwater_Plot(drawdown_df):

    plt.style.use('ggplot')
    fig , ax = plt.subplots(figsize=(23,6))
    ax.set_title("UnderWater Plot")
    # ax.plot(長期持有_BacKTesting_DF['Portfolio Market Values'],label='equity curve')
    ax.plot(drawdown_df['Date'],drawdown_df['Drawdown Value']*-1,label='drawdown',color='blue')
    
    plt.fill_between(drawdown_df['Date'],0,drawdown_df['Drawdown Value']*-1,color='blue',alpha=0.6)
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=30))
    plt.xticks(rotation=-45)
    ax.set_ylabel("Drawdown")
    ax.set_xlabel("Date")
    ax.legend()
    plt.show()