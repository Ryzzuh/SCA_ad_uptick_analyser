#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import pandas as pd
import numpy as np
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows',  150)
pd.set_option('display.width', 1000)
import datetime as dt

stations = [
  "9"
  , "Gem"
  , "Go!"
]


def main():
  """ Main program """
  xlsx = pd.ExcelFile("mediaplan_template.xlsx")
  df = xlsx.parse("July")

  def get_headers_index(dataFrame):
    search_term = "STATUS"
    df = dataFrame
    found = 0
    index = 0
    while not found:
      #print(index)
      #print(list(df.loc[index],))
      if search_term in list(df.loc[index]):
        found = 1
      else:
        index += 1
    return index


  def get_headers(df, header_index):
    #take datafram and header index
    headers = list(df.loc[header_index])
    return headers

  def clean_headers(headers):
    for i, item in enumerate(headers):
      #determine if float and rename if so, this is for creating dictionary object later
      if isinstance(item, np.float64):
        headers[i] = "col_{}".format(i)
    return headers

  def rename_df_columns(df, headers):
    df.columns = headers
    return df

  def get_antiheader_indexes(df):
    search_term = "STATUS"
    antiHeaderIndexes = df.index[df[search_term] == search_term].tolist()
    return antiHeaderIndexes

  def get_booking_groups(df, antiHeaderIndexes):
    bookingGroups = []
    for item in antiHeaderIndexes:
      bookingGroups.append(df.loc[item-1,'SPOT ID'])
    return bookingGroups

  def get_booking_location(bookingGroups):
    bookingLocations = []
    for item in bookingGroups:
      item = item.split(' ')
      if len(item) == 5:
        bookingLocations.append(item[4])
      else:
        bookingLocations.append(" ".join(item[4:]))
    return bookingLocations

  def get_booking_network(bookingGroups):
    bookingNetworks = []
    for item in bookingGroups:
      item = item.split(' ')
      bookingNetworks.append(item[3])
    return bookingNetworks

  def fill_df_w_group_details(df, antiheader_indexes, bookingLocations, bookingNetworks):
    #we also want the eof file to be appended to the antiheader_indexes
    antiheader_indexes.append(len(df.index))
    for i, item in enumerate(antiheader_indexes):
      if i < len(antiheader_indexes) -1:
        df.loc[item + 1:antiheader_indexes[i + 1], 'Country'] = bookingLocations[i]
        df.loc[item+1:antiheader_indexes[i+1], 'Network'] = bookingNetworks[i]
    return df

  def drop_na_rows(df, subset):
    return df.dropna(subset=subset)

  def drop_duplicate_rows(df, subset):
    return df.drop_duplicates(subset = subset, keep=False)

  def correct_dates(df):
    #dates are datetime.datetime where time = 00:00:00
    #time colomn is datetime.time
    #need statement for each case
    dates =  list(df['TX DATE'])
    #print("dates length is: ", len(dates))
    times =  list(df['TX TIME'])
    datetimes = []
    for i, date in enumerate(dates):
      if type(date) == dt.datetime:
        datetimes.append(dt.datetime(date.year, date.month,date.day, times[i].hour, times[i].minute, 0))
      elif type(date) == str:
        dateList = list(map(int, date.split("/")))
        datetimes.append(dt.datetime(dateList[2], dateList[1], dateList[0], times[i].hour, times[i].minute, 0))
      else:
        #append non date value. doesnt seem like a good solution
        datetimes.append(date)
    df['TX DATE'] = datetimes
    return df

  header_index = get_headers_index(df)
  headers = get_headers(df, header_index)
  cleaned_headers = clean_headers(headers)
  df = rename_df_columns(df, cleaned_headers)
  antiheader_indexes = get_antiheader_indexes(df)
  bookingGroups = get_booking_groups(df, antiheader_indexes)
  bookingLocations = get_booking_location(bookingGroups)
  bookingNetworks = get_booking_network(bookingGroups)
  df =  fill_df_w_group_details(df, antiheader_indexes, bookingLocations, bookingNetworks)
  df = drop_na_rows(df, ['TX DATE'])
  df = drop_duplicate_rows(df, ['SPOT ID'])
  df = correct_dates(df)

  #print(df)

  df.to_csv('output/mediaPlanCleaned.csv', header=True, date_format='%Y-%m-%d %H:%M:%S')



if __name__ == "__main__":
  main()