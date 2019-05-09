#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyjq
import requests
from datetime import datetime
from datetime import timedelta
import locale
import sys
import re


def lunch():
    sv_date("sv_SE.utf-8")
    num_of_restaurants = 4
    num_of_days = get_param()
    menu = {}

    for i in range(num_of_restaurants):
        data = get_data(i, num_of_days)
        map_data(menu, data, i, num_of_restaurants)

    print_data(menu)


def get_data(api, num_of_days):
    keys = ['3d519481-1667-4cad-d2a3', '21f31565-5c2b-4b47-d2a1',
            'b672efaf-032a-4bb8-d2a5', '3ac68e11-bcee-425e-d2a8']
    dates = get_dates(num_of_days)
    req = requests.get(
        'http://carbonateapiprod.azurewebsites.net/'
        'api/v1/mealprovidingunits/'+keys[api]+'-08d558129279/dishoccurrences?'
        'startDate='+dates[0]+'&endDate='+dates[1])

    return pyjq.all(
        '.[] | .startDate, .displayNames[0].dishDisplayName', req.json())


def map_data(menu, data, res, num_of_res):
    length = len(data)
    for i in range(0, length, 2):

        date = data[i]
        food = data[i+1]
        formated = format_date(date)

        if formated in menu:
            menu[formated][res].append(food)
        else:
            disharr = [[] for i in range(num_of_res)]
            disharr[res].append(food)
            menu[formated] = disharr


def print_data(menu):
    for key in sorted(menu):
        print_line()
        print_date(key)

        for index, arr in enumerate(menu[key]):
            print_restaurant(arr, index)

            for elem in arr:
                print_element(elem)
    print_line()


def get_param():
    try:
        param = sys.argv[1:][0]
        if is_int(param):
            if 0 <= param:
                return int(param)
        return 0
    except IndexError:
        return 0


def is_int(param):
    try:
        int(param)
        return True
    except ValueError:
        return False


def find_index(reg):
    try:
        index = reg.start()
        return index
    except AttributeError:
        return -1


def get_dates(num_of_days):
    today = datetime.today()
    end_date = (today + timedelta(days=num_of_days)).strftime('%Y-%m-%d')
    start_date = today.strftime('%Y-%m-%d')
    return [start_date, end_date]


def sv_date(code):
    locale.setlocale(locale.LC_TIME, code)


def format_date(date):
    return datetime.strptime(
        date[:-3], '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d')


def print_date(date):
    print style.BOLD + style.GREEN + datetime.strptime(
        date, '%Y-%m-%d').strftime('%a') + style.DEFAULT


def print_element(elem):
    word = "köttbullar".decode("utf-8")
    ans = re.search(r'\b' + re.escape(word) + r'\b', elem, re.IGNORECASE)

    index = find_index(ans)
    if index == -1:
        print " - " + elem
        return

    length = (index+len(word))

    head = elem[0:index]
    body = elem[index:length]
    tail = elem[length:]

    print " - " + head + style.BOLD + style.BLINK + body + style.DEFAULT + tail


def print_restaurant(arr, index):
    restaurants = ["Expressen", "Kårrestaurangen", "Linsen", "S.M.A.K"]
    print style.BLUE + restaurants[index] + style.DEFAULT
    if not arr:
        print " - Ingen meny"


def print_line():
    line = "-"*50
    print style.DIM + line + style.DEFAULT


class style():
    DIM = '\033[2m'
    DEFAULT = '\033[0m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    BOLD = "\033[1m"
    BLINK = '\33[5m'


lunch()
