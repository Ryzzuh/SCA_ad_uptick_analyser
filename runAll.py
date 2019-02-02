#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
print("hi")

process.stdout.readline()
sys.stdout.flush()
sys.stdout.write("\n")
sys.stdout.write("running bigQuery ETL...")
import ETLbiqQueryData
ETLbiqQueryData.main()
sys.stdout.flush()
sys.stdout.write("Done!")

sys.stdout.write("\n")
sys.stdout.write("cleaning media plan...")
import cleanMediaPlan
cleanMediaPlan.main()
sys.stdout.flush()
sys.stdout.write("Done!")

sys.stdout.write("\n")
sys.stdout.write("running main process...")
import mainProcess
mainProcess.main()
sys.stdout.flush()
sys.stdout.write("Done!")

sys.stdout.write("\n")
sys.stdout.write("merging results...")
import letsGetMarried
letsGetMarried.main()
sys.stdout.flush()
sys.stdout.write("Done!")

def main():
  """ Main program """
  # Code goes over here.
  return 0


if __name__ == "__main__":
  main()