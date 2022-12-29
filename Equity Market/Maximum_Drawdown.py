import numpy as np 
import pandas as pd
import datetime as dt 

import matplotlib.pyplot as plt 
plt.style.use('ggplot')




def Construct_Drawdown(Historical_Values,Variable_Name,DataFrame_Index,Max_Unit):
    """
    # Maximum Drawdown 定義:
    --------------------------
    程式交易中有許多數值來評價一個 策略的特性或表現，其中一個重要的數值 MDD (Max Drawdown) 也稱作 "最大回撤" 或 "最大跌幅" 。

    # Definition from Wikipedia:
    --------------------------
    The drawdown is the measure of the decline from a historical peak in some variable.
    (typically the cumulative profit or total open equity of a financial trading strategy)

    # Parameters Setting:
    --------------------------
    Input_Variable: 
    1.)  Historical values of "one" variable (Astype: List) 
    2.)  Variable Name (Astype: String) 
    3.)  Index for DataFrame --> Daily/Weekly/Monthly/Quarterly (Astype: List) 
    \\
    Output_Variable: 
    Maximum Drawdown Table (Astype: Pandas-DataFrame)
    """

    # Set up Parameters
    drawdown_df = pd.DataFrame()
    peak_values = [ Historical_Values[0] ]
    drawdown_values = [] 

    drawdown_duration = []
    drawdown_day = 0
    count_drawdown_duration = 0

    # Loop over the index range ( record historical peak date and construct maximun drawdown )
    for i in range(len(Historical_Values)):

        # compare wheather current peak values is bigger than the previous one , append the bigger one into the list.
        previous_peak_value = peak_values[i]
        current_value = Historical_Values[i]

        if drawdown_day >= Max_Unit:
            update_peak_value = current_value
        else:
            update_peak_value = max(previous_peak_value , current_value)
        
        peak_values.append( update_peak_value )  
        # lastest peak minus current equity values = current drawdown
        drawdown_values.append( update_peak_value - current_value ) 

        # drawdown duration 
        if update_peak_value - current_value == 0:
            drawdown_day = 0
            count_drawdown_duration += 1
            drawdown_duration.append(count_drawdown_duration)
        else:
            drawdown_day += 1
            # count_drawdown_duration +=1
            drawdown_duration.append(count_drawdown_duration)


    drawdown_df[str(Variable_Name)] = Historical_Values
    drawdown_df['Peak Values'] = peak_values[1:] # drop the first inital values
    drawdown_df['Drawdown Values'] = drawdown_values
    drawdown_df['Drawdown_Period_ID'] = drawdown_duration 
    drawdown_df.index = DataFrame_Index

    return drawdown_df



def Classify_Period_Drawdown(drawdown_df,Variable_Name):
    """
    Parameters Setting:
    --------------------------
    Input Variable: \

    1.) drawdown_df from .Construct_Drawdown() / Astype: pd.DataFrame \

    2.) Variable Name (Astype: String)

    Output Variable: \

    1.) period_df / Astype: pd.DataFrame

    Function Explain:
    --------------------------
    1.) Construct Maximum Drawdown Values in each Drawdown_Period_ID \\
    2.) Number of Day in Drawdown Duration \\
    3.) Variable historical peak date and valley date \\
    4.) Recovery duration \
    """

    period_drawdown_df = drawdown_df.copy()
    period_bottom_df = period_drawdown_df.groupby('Drawdown_Period_ID')['Drawdown Values'].agg('max').reset_index(name='Period Max Drawdown Values')  # Valley Values
    period_bottom_df = pd.merge(period_bottom_df, period_drawdown_df, how='left')
    period_df = period_bottom_df[period_bottom_df['Period Max Drawdown Values'] == period_bottom_df['Drawdown Values']].reset_index(drop=True)

    # Peak_Dates 
    peak_date_df = period_drawdown_df[period_drawdown_df['Drawdown Values']==0]
    period_df['peak_date'] = peak_date_df[['Drawdown_Period_ID']].drop_duplicates().index.to_list()

    # Valley_Dates
    valley_date_df = period_drawdown_df.groupby(['Drawdown_Period_ID'])['Drawdown Values'].transform(max) == period_drawdown_df['Drawdown Values']
    period_df['valley_date'] = period_drawdown_df[valley_date_df].index

    # recovery duration
    period_df['recovery duration'] = period_df['valley_date'] - period_df['peak_date'].shift(-1) 
    period_df['drawdown duration'] = period_df['valley_date'] - period_df['peak_date']

    # Reshape Columns in desire order
    period_df = period_df[['Drawdown_Period_ID','peak_date','Peak Values','Drawdown Values',Variable_Name,'valley_date','drawdown duration','recovery duration']]

    return period_df


