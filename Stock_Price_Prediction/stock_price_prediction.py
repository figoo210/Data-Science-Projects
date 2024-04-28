import numpy as np
import pandas as pd
 
window_period = 14
 

def atr_indicator(atr_period):
  #to add ATR to the df as a new column called atr
  data = pd.read_csv('drive/MyDrive/colab projects/file0.csv')
  
  global df
  df = data.copy()
  print('ATR will be calculated using a period of ',atr_period)
 
  df['cur_high_cur_low'] = df['h'] - df['l']
  df['cur_high_pre_close'] = abs(df['h'] - df['c'].shift(1))
  df['cur_low_pre_close'] = abs(df['l'] - df['c'].shift(1))
 
  df['true_range'] = df[['cur_high_cur_low', 'cur_high_pre_close', 'cur_low_pre_close']].max(axis=1)
 
  df['atr'] = 0
 
  #the first (atr_period) 14-day ATR is the average of the daily TR values for the last 14 days (atr_period).
  df.loc[atr_period-1,'atr'] = sum(df.true_range[:atr_period]) / atr_period
 
  #Current ATR = [(Prior ATR x 13 (atr_period-1)) + Current TR] / 14 (atr_period)
  for i in range(atr_period, df.shape[0]):
      #print(i,'prev ', df.loc[i-1,'atr'], 'same row TR', df.loc[i,'true_range'] )
      df.loc[i,'atr'] = (df.loc[i-1,'atr'] * (atr_period-1) + df.loc[i,'true_range'])/ atr_period
      
  df.drop(columns=['cur_high_cur_low','cur_high_pre_close','cur_low_pre_close'], inplace=True)
  print(df)


def adx_indicator(wperiod):
  #to add ADX to the df as a new column called adx
  
  data = pd.read_csv('drive/MyDrive/colab projects/file0.csv')
  
  global df
  df = data.copy()

  #Calculate True Range
  df['cur_high_cur_low'] = df['h'] - df['l']
  df['cur_high_pre_close'] = abs(df['h'] - df['c'].shift(1))
  df['cur_low_pre_close'] = abs(df['l'] - df['c'].shift(1))

  df['true_range'] = df[['cur_high_cur_low', 'cur_high_pre_close', 'cur_low_pre_close']].max(axis=1)

  df.drop(columns=['cur_high_cur_low','cur_high_pre_close','cur_low_pre_close'], inplace=True)
  #print(df)

  #Calculate Plus Directional Movement (plus_DM) and Minus Directional Movement (minus_DM) for each period.
  #First find the difference between two consecutive lows with the difference between their respective highs.
  df['moveUp'] = df['h'] - df['h'].shift(1)
  df['moveDown'] = df['l'].shift(1) - df['l']

  #then, find the Plus Directional Movement (plus_DM)
  #when the current high minus the prior high is greater than the prior low minus the current low. 
  #(plus_DM) equals the current high minus the prior high, provided it is positive.
  #A negative value would simply be entered as zero.
  df['plus_DM'] = df[['moveUp', 'moveDown']].apply(lambda x: x['moveUp'] if x['moveUp'] > x['moveDown'] and x['moveUp'] > 0 else 0, axis=1)

  #then, find the Minus Directional Movement (minus_DM)
  #when the prior low minus the current low is greater than the current high minus the prior high. 
  #(minus_DM) equals the prior low minus the current low, provided it is positive.
  #A negative value would simply be entered as zero.
  df['minus_DM'] = df[['moveUp', 'moveDown']].apply(lambda x: x['moveDown'] if x['moveDown'] > x['moveUp'] and x['moveDown'] > 0 else 0, axis=1)

  #put the first row of (plus_DM) and (minus_DM) equal none because no previous high or low prices
  df['plus_DM'][0] = None
  df['minus_DM'][0] = None

  #df.drop(columns=['moveUp', 'moveDown'], inplace=True)
  #print(df)

  #Smooth these periodic values True Range (true_range), Plus Directional Movement (plus_DM) and Minus Directional Movement (minus_DM).
  df['smooth_tr'], df['smooth_plus_DM'], df['smooth_minus_DM'] = 0, 0, 0
  #because there are not smooth values during the period. put smooth values equal none till the end of the period
  df['smooth_tr'][:wperiod], df['smooth_plus_DM'][:wperiod], df['smooth_minus_DM'][:wperiod] = None, None, None
  #the first (smooth_tr), (smooth_plus_DM), (smooth_minus_DM) = Sum of first 14 periods of (true_range), (plus_DM), (minus_DM)
  df['smooth_tr'][wperiod] = sum(df['true_range'][1:wperiod+1])
  df['smooth_plus_DM'][wperiod] = sum(df['plus_DM'][1:wperiod+1])
  df['smooth_minus_DM'][wperiod] =sum(df['minus_DM'][1:wperiod+1])
  #Subsequent Values = Prior smoothed values - (Prior smoothed values/period) + Current values not smoothed
  for i in range(wperiod + 1, df.shape[0]):
    #print(i,'prev ', df['smooth_tr'][i - 1], 'same row TR', df['true_range'][i])
    df['smooth_tr'][i] = df['smooth_tr'][i - 1] - (df['smooth_tr'][i - 1] / wperiod) + df['true_range'][i]

    #print(i,'prev ', df['smooth_plus_DM'][i - 1], 'same row Positive direction', df['plus_DM'][i])
    df['smooth_plus_DM'][i] = df['smooth_plus_DM'][i - 1] - (df['smooth_plus_DM'][i - 1] / wperiod) + df['plus_DM'][i]

    #print(i,'prev ', df['smooth_minus_DM'][i - 1], 'same row Negative direction', df['minus_DM'][i])
    df['smooth_minus_DM'][i] = df['smooth_minus_DM'][i - 1] - (df['smooth_minus_DM'][i - 1] / wperiod) + df['minus_DM'][i]
  
  #print(df)


  #Indicator Calculation
  #Divide the 14-day smoothed Plus Directional Movement (smooth_plus_DM) by the 14-day smoothed True Range
  #to find the 14-day Plus Directional Indicator (pos_DI) and multiply by 100
  df['pos_DI'] = (df['smooth_plus_DM'] / df['smooth_tr']) * 100
  #Divide the 14-day smoothed Minus Directional Movement (smooth_minus_DM) by the 14-day smoothed True Range
  #to find the 14-day Minus Directional Indicator (neg_DI)and multiply by 100
  df['neg_DI'] = (df['smooth_minus_DM'] / df['smooth_tr']) * 100

  #The Directional Movement Index (DX) equals the absolute value of Plus Directional Indicator (pos_DI) subtract Minus Directional Indicator (neg_DI)
  #divided by the sum of Plus Directional Indicator (pos_DI) and Minus Directional Indicator (neg_DI) and multiply the result by 100
  df['DX'] = abs(((df['smooth_plus_DM'] - df['smooth_minus_DM']) / (df['smooth_plus_DM'] + df['smooth_minus_DM'])) * 100)

  #df.drop(columns=['smooth_plus_DM', 'smooth_minus_DM'], inplace=True)

  #Calculate the Average Directional Index (ADX)
  df['adx'] = 0
  #the ADX is smoothed each period's DX value so adx_period = window_period + DX_period
  adx_period = wperiod * 2
  #because there are not smooth values during the period. put adx equal none till the end of the period
  df['adx'][:adx_period-1] = None
  #First, calculate an average for the first 14 days as a starting point. First ADX14 = 14 period Average of DX
  df['adx'][adx_period-1] = sum(df['DX'][wperiod:adx_period]) / wperiod
  #The second and subsequent ADX14 = ((Prior ADX14 x wperiod-1) + Current DX Value)/14
  for i in range(adx_period, df.shape[0]):
    #print(i,'prev ', df['adx'][i - 1], 'same row DX', df['DX'][i])
    df['adx'][i] = (df['adx'][i - 1] * (wperiod-1) + df['DX'][i]) / wperiod


  #df.drop(columns=['DX'], inplace=True)
  print(df)



