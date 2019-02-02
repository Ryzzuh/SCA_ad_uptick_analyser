#!/usr/bin/env """ Main program """
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime as dt
#pd.options.display.max_rows = 999

#////////////////////////////////
# This module is the first step in the pipeline
# it reads the bigquery data (later GA and other sources)
# rounds all sessions to the nearest minute and groups them by datetime and location
# saves results to csv with attributes visitStartTime, geoNetwork_city, Sessions_count
# COMMENTS
# - improve accuracy of our model, we need to build a better baseline, either from a time period \
# where no ATL ads were ran, or the previous 8 weeks with the times when the ads were ran removed \
# - Also, allow the user to specify which time period to analyse. Currently the time period is \
# specified at the extract stage in bigquery.
#////////////////////////////////

def main():
  """ Main program """
  # load data file
  df = pd.read_csv('raw_sessions_dat.csv', sep=',', header=0)

  # convert timestamp to date and round to nearest minute
  df['visitStartTime'] = (pd.to_datetime(df['visitStartTime'], unit='s'))
  df['visitStartTime'] = pd.DatetimeIndex(df['visitStartTime']).round('1min')
  #change UTC to Sydney - Note: need to change for each specific timezone
  df['visitStartTime'] = df['visitStartTime'].dt.tz_localize('UTC').dt.tz_convert('Australia/Sydney')


  #extract trailing 9 weeks from year of data
  #set date endpoints
  mostRecentDate = max(df['visitStartTime'])
  #create variable to hold date of 7 days ago
  nineWeekAgoDate = np.datetime64(mostRecentDate) - np.timedelta64(63, "D")
  nineWeekAgoDate = pd.to_datetime(nineWeekAgoDate)
  df = df[(df['visitStartTime'] > nineWeekAgoDate)]
  #///////////////

  #group by city and time
  df = df.groupby([pd.Grouper(key='visitStartTime', freq='60s'), 'geoNetwork_city'])['geoNetwork_city'].count()
  df.drop_duplicates()
  df = df.to_frame()
  # rename sessions count column
  df.columns.values[0] = "Sessions_count"

  # /////////////////
  # output stuff
  df.to_csv('output/1_last_9_weeks.csv', header=True, date_format='%Y-%m-%d %H:%M:%S')



if __name__ == "__main__":
  main()