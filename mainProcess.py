#!/Users/rhysall/anaconda/bin/python python
# -*- coding: utf-8 -*-
import pandas as pd
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.options.display.max_rows = 100
import numpy as np
import datetime as dt

import matplotlib.pyplot as plt
plt.style.use('ggplot')


def main():
  """ Main program """
  # Code goes over here.

  #LOAD AND TRANSFORM TYPES/////////////////
  #load data file
  df = pd.read_csv('output/1_last_9_weeks.csv', sep=',', header=0)
  #convert date column to datetime
  df['visitStartTime'] = (pd.to_datetime(df['visitStartTime']))
  #////////////////

  #SET TEMPORAL VARIABLES //////////
  #set date endpoints
  leastRecentDate = min(df['visitStartTime'])
  mostRecentDate = max(df['visitStartTime'])
  #create variable to hold date of 7 days ago
  oneWeekAgoDate = np.datetime64(mostRecentDate) - np.timedelta64(7, "D")
  oneWeekAgoDate = pd.to_datetime(oneWeekAgoDate)
  #///////////////


  #create two data-frames, one for the baseline and one for last week
  baseline_df = df[(df['visitStartTime'] > leastRecentDate) & (df['visitStartTime'] < oneWeekAgoDate)]
  lastweek_df = df[(df['visitStartTime'] > oneWeekAgoDate) & (df['visitStartTime'] < mostRecentDate)]

  #create dataframe for city of interest - refactor to class?
  #create baseline
  brisbaneBLDF = baseline_df.loc[df['geoNetwork_city'] == "Brisbane"]
  brisbaneLWDF = lastweek_df.loc[df['geoNetwork_city'] == "Brisbane"]

  #print(brisbaneBLDF)
  #create dayMinHour column for DFs
  def create_key_column(dataframe, baseline=True):
    #//////// this creates join conditions for each minute of the day of a week iow, baseline
    day = dataframe['visitStartTime'].apply(lambda x: x.weekday())
    hour = dataframe['visitStartTime'].apply(lambda x: x.hour)
    minute = dataframe['visitStartTime'].apply(lambda x: x.minute)
    dataframe['dayMinHour'] = day.astype(str) + ":" + hour.astype(str) + ":" + minute.astype(str)


    # group by dayMinHour key if baseline
    if baseline:
      dataframe['baseline_sessions'] = dataframe.groupby(['dayMinHour'])['Sessions_count'].transform('sum') /8
      dataframe = dataframe.drop_duplicates('dayMinHour')
      dataframe = dataframe.drop('Sessions_count', axis=1)
    return dataframe

  #create Dataframe for each period - previous 8 weeks and last week
  #BL = baseline, LW = lastweek
  brisbaneBLDF = create_key_column(brisbaneBLDF)
  brisbaneLWDF = create_key_column(brisbaneLWDF, False)

  # create a dataframe containing all minutes for the last week
  def get_all_minutes(last_week_DF):
    # get first sessions minutes
    dmin = last_week_DF['visitStartTime'].min()
    dmax = last_week_DF['visitStartTime'].max()
    #get city
    city = last_week_DF['geoNetwork_city'].iloc[1]
    #make dataframe for every minute after firstdate and before lastdate
    LWminutes = pd.DataFrame({'visitStartTime': pd.date_range(dmin, dmax, freq='1min'), 'Sessions_count': 0})
    LWminutes = create_key_column(LWminutes, False)
    #print("foo", LWminutes)
    return LWminutes

  #create DataFrame with all minutes from last weeek
  allminsDF = get_all_minutes(brisbaneLWDF)




  #print(brisbaneBLDF)
  #print(baseline_df)

  #join allmins to baseline
  left = allminsDF
  right = brisbaneBLDF
  joined = pd.merge(left, right, how = 'left', on= "dayMinHour")
  #drop columns
  joined = joined.drop('visitStartTime_y', axis= 1)
  #joined = joined.drop('total sessions_x', axis= 1)
  #joined = joined.drop('Sessions_count_x', axis= 1)

  #print(joined)

  #join with last weeks data
  left = joined
  right = brisbaneLWDF
  joined = pd.merge(left, right, how='left', on="dayMinHour")
  #print(joined)

  #drop columns
  joined = joined.drop('visitStartTime', axis= 1)
  joined = joined.drop('geoNetwork_city_y', axis= 1)
  joined = joined.drop('Sessions_count_x', axis=1)

  #clean up result
  #BLdata
  joined['baseline_sessions'].fillna(0, inplace=True)
  #joined['baseline_sessions'].interpolate(inplace=True)
  #LWdata
  joined['Sessions_count_y'].fillna(0, inplace=True)
  #joined['Sessions_count'].interpolate(inplace=True)
  #joined['total sessions'].interpolate(inplace=True)

  #print(joined)

  #add time lag columns for baseline and last week data
  def create_sum_column(dataFrame, timePeriod):
    #create numpy array for transform
    df = np.array(dataFrame)
    #transform adding timePeriod column
    for i, listItem in enumerate(df):
      df[i] = np.sum(df[i:i+timePeriod])
    return df

  def create_impact_column(df, bl_col_name, lw_col_name):
    baseline = df[bl_col_name]
    lastweek = df[lw_col_name]
    impact = []
    for i, each in enumerate(baseline):
      impact.append(round((lastweek[i] - baseline[i])/baseline[i]*100, 2))

    df['impact'] = impact
    return df

  timePeriod = 15
  timeLagBL = 'baseline_'+ str(timePeriod) + '_mins'
  timeLagLW = 'sessions_count_' + str(timePeriod) + '_mins'
  joined[timeLagBL] = create_sum_column(joined['baseline_sessions'], timePeriod)
  joined[timeLagLW] = create_sum_column(joined['Sessions_count_y'], timePeriod)
  joined = create_impact_column(joined, timeLagBL, timeLagLW)

  #output stuff
  #brisbaneBLDF.to_csv('brisbaneBLDF.csv', header= True, date_format='%Y-%m-%d %H:%M:%S')
  #brisbaneLWDF.to_csv('brisbaneLWDF.csv', header= True, date_format='%Y-%m-%d %H:%M:%S')
  joined.to_csv('output/joined.csv', header=True, date_format='%Y-%m-%d %H:%M:%S')

  #joined = joined[::15]
  #plot WORKING!
  plt.figure(figsize=(20, 6), dpi=600)
  plt.plot(joined['visitStartTime_x'], joined[timeLagLW], color ='y', label = "last week")
  plt.plot(joined['visitStartTime_x'], joined[timeLagBL], color ='r', label = "baseline")
  plt.legend(loc='upper left')
  plt.ylabel('sessions ' + str(timePeriod) + "+ mins")
  plt.xlabel('date')
  plt.savefig('output/myfig.png')


if __name__ == "__main__":
  main()