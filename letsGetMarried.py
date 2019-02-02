#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import pandas as pd
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.options.display.max_rows = 100

def main():
  """ Main program """
  mediaPlan = pd.read_csv('output/mediaPlanCleaned.csv', sep=',', header=0)
  #print(mediaPlan)

  joined = pd.read_csv('output/joined.csv', sep=',', header=0)
  #print(joined)

  left = mediaPlan
  right = joined
  hitched = pd.merge(left, right, how='inner', left_on="TX DATE", right_on="visitStartTime_x")

  hitched.to_csv('output/hitched.csv', header=True, date_format='%Y-%m-%d %H:%M:%S')


if __name__ == "__main__":
  main()