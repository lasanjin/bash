#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function  # print python2
from datetime import datetime
from datetime import timedelta
from threading import Thread
import xml.etree.ElementTree as ET
import locale
import json
import sys
import re

PY_VERSION = sys.version_info[0]

if PY_VERSION < 3:
    from Queue import Queue
    import urllib2
elif PY_VERSION >= 3:
    from queue import Queue
    import urllib.request as urllib2


RESTAURANTS = [["Expressen", '3d519481-1667-4cad-d2a3'],
               ["Kårrestaurangen", '21f31565-5c2b-4b47-d2a1'],
               ["Linsen", 'b672efaf-032a-4bb8-d2a5'],
               ["S.M.A.K", '3ac68e11-bcee-425e-d2a8'],
               ["J.A. Pripps", 'http://intern.chalmerskonferens.se/'
                'view/restaurant/j-a-pripps-pub-cafe/RSS%20Feed.rss']]


def main():
    locale.setlocale(locale.LC_ALL, 'sv_SE.utf-8')
    try:
        arg = int(sys.argv[1:][0]) - 1
        num_of_days = arg if arg >= 0 else 0
    except Exception:
        num_of_days = 0

    info = Utils.style("[INFO]", "green")
    print(info, "FETCHING DATA...")

    menus = get_menus(num_of_days)
    if not menus:
        print(info, 'INGEN DATA')
    else:
        print_data(menus)


def get_menus(num_of_days):
    menus = dict()
    queue = build_queue()

    for i in range(queue.qsize()):
        thread = Thread(target=get_menus_thread,
                        args=(queue, menus, num_of_days))
        thread.daemon = True
        thread.start()

    queue.join()

    return menus


def build_queue():
    queue = Queue()
    num_of_restaurants = len(RESTAURANTS)

    for i in range(num_of_restaurants):
        queue.put(i)

    return queue


def get_menus_thread(queue, menus, num_of_days):
    while not queue.empty():
        i = queue.get()
        restaurant = RESTAURANTS[i][0]
        data = request_menu(i, num_of_days)

        if data is not None:
            if restaurant == 'J.A. Pripps':
                menu = parse_pripps_menu(data, num_of_days)
            else:
                menu = parse_menu(data)

            parse_data(menus, menu, i)

        queue.task_done()


def parse_menu(data):
    rawdata = json.loads(data)
    menu = []

    for i in rawdata:
        menu.append(format_date(i['startDate']))
        menu.append(i['displayNames'][0]['dishDisplayName'])

    return menu


def parse_pripps_menu(data, num_of_days):
    item = ET.fromstring(data).findall('channel/item')
    menu = []
    start_date, end_date = get_date_range(num_of_days)

    for title in item:
        date = title.find("title").text[-10:]

        for description in title:
            for table in description:
                for tr in table:
                    for td in tr:
                        dish = tr.findall("td")[1].text

                        for b in td:
                            dish_type = b.text

                            if start_date <= date <= end_date:
                                append_data(menu,
                                            date,
                                            dish,
                                            dish_type)
    return menu


def parse_data(menus, data, restaurant):
    num_of_restaurants = len(RESTAURANTS)
    length = len(data)

    for i in range(0, length, 2):
        date = data[i]
        dish = data[i+1]

        if date in menus:
            menus[date][restaurant].append(dish)
        else:
            disharr = [[] for i in range(num_of_restaurants)]
            disharr[restaurant].append(dish)
            menus[date] = disharr


def request_menu(i, num_of_days):
    url = build_url(i, num_of_days)

    try:
        return urllib2.urlopen(url, timeout=10).read()
    except Exception as e:
        print("Exception: %s" % e)
        print("URL: %s" % url)
        return None


def build_url(i, num_of_days):
    restaurant = RESTAURANTS[i][0]

    if restaurant == 'J.A. Pripps':
        return RESTAURANTS[i][1]
    else:
        start_date, end_date = get_date_range(num_of_days)
        return Api.url(RESTAURANTS[i][1], start_date, end_date)


def get_date_range(num_of_days):
    today = datetime.today()
    start_date = today.strftime(Utils.format('Ymd'))
    end_date = (
        today + timedelta(days=num_of_days)).strftime(Utils.format('Ymd'))

    return start_date, end_date


def format_date(date):
    return datetime.strptime(
        date[:-3], Utils.format('mdYHMS')).strftime(Utils.format('Ymd'))


def append_data(menu, date, dish, dish_type):
    menu.append(date)
    menu.append(dish + Utils.style(" (" + dish_type + ")", None, ['dim']))


def find_match(dish):
    match = re.search(
        r'\b' + Utils.decode('(köttbullar|meatballs)') + r'\b', dish, re.IGNORECASE)
    try:
        index = match.start()
        _len = (index + len(match.group(0)))
        return index, _len
    except AttributeError:
        return None, None


class Api:
    URL = \
        'http://carbonateapiprod.azurewebsites.net/' \
        'api/v1/mealprovidingunits/'

    @staticmethod
    def url(restaurant, start_date, end_date):
        return Api.URL + restaurant + \
            '-08d558129279/dishoccurrences?' \
            'startDate=' + start_date + \
            '&endDate=' + end_date


class Utils:
    @staticmethod
    def decode(string):
        return string.decode("utf-8") if PY_VERSION < 3 else string

    @staticmethod
    def format(arg):
        return {
            'Ymd': '%Y-%m-%d',
            'mdYHMS': '%m/%d/%Y %H:%M:%S'
        }[arg]

    @staticmethod
    def style(output, color, styles=[]):
        if color is not None:
            output = {
                'green': '\033[92m%s',
                'blue': '\033[94m%s',
            }[color] % output

        for style in styles:
            output = {
                'blink': '\33[5m%s',
                'bold': '\033[1m%s',
                'dim': '\033[2m%s'
            }[style] % output

        return output + '\033[0m'  # default


# -----------------------------------------------------------------
# PRINT
# -----------------------------------------------------------------
def print_data(menus):
    # print menu
    dot = Utils.decode('· ')
    for date in sorted(menus):
        print()
        day = datetime.strptime(date, Utils.format('Ymd')).strftime('%a')
        print(Utils.style(day, 'green', ['bold']))
        # print restaurant
        for restaurant, menu in enumerate(menus[date]):
            print(Utils.style(RESTAURANTS[restaurant][0], 'blue'))
            if not menu:
                print(dot + Utils.style('INGEN MENY', None, ['dim']))
            else:
                # print dish
                for dish in menu:
                    index, _len = find_match(dish)
                    # print dish
                    if index is None:
                        print(dot + dish)
                    # print match
                    else:
                        head = dish[0:index]
                        body = dish[index:_len]
                        tail = dish[_len:]
                        print(
                            dot + head + Utils.style(body, None, ['blink']) + tail)
    print()


if __name__ == "__main__":
    main()
