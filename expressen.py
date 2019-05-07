#!/usr/bin/python

import pyjq
import requests
import datetime
import collections

r = requests.get('http://carbonateapiprod.azurewebsites.net/api/v1/mealprovidingunits/3d519481-1667-4cad-d2a3-08d558129279/dishoccurrences?startDate=2019-05-05&endDate=2019-05-10')
arr = pyjq.all('.[] | .startDate, .displayNames[0].dishDisplayName', r.json())

# map dates to food
# quit()
map = dict()
length = len(arr)
for i in range(0, length, 2):

    date = arr[i]
    food = arr[i+1]
    formated = datetime.datetime.strptime(
        date[:-3], '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d')

    if formated in map:
        map[formated].append(food)
    else:
        map[formated] = [food]

# sort map by dates and print
for key in sorted(map):
    print key
    for elem in map[key]:
        print elem


# tmpdate = None
# length = len(arr)
# for i in range(0, length, 2):
#    date = arr[i]
#    food = arr[i+1]
#    if date != tmpdate:
#        print
#        print datetime.datetime.strptime(
#            date[:-3], '%m/%d/%Y %H:%M:%S').strftime('%a')
#        tmpdate = date

#    print food
# print
