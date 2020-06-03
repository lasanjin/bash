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
import six

if six.PY2:  # python2
    from Queue import Queue
    import urllib2
    import httplib

elif six.PY3:  # python3
    from queue import Queue
    import urllib.request
    import urllib.error as urllib2  # urllib2.HTTPError
    import http.client as httplib  # httplib.HTTPException


restaurants = [["Expressen", '3d519481-1667-4cad-d2a3'],
               ["Kårrestaurangen", '21f31565-5c2b-4b47-d2a1'],
               ["Linsen", 'b672efaf-032a-4bb8-d2a5'],
               ["S.M.A.K", '3ac68e11-bcee-425e-d2a8'],
               ["J.A. Pripps", 'http://intern.chalmerskonferens.se/'
                'view/restaurant/j-a-pripps-pub-cafe/RSS%20Feed.rss']]


def main():
    locale.setlocale(locale.LC_ALL, 'sv_SE.utf-8')
    menus = get_menus()
    print_data(menus)


def get_menus():
    menus = dict()

    try:
        arg = int(sys.argv[1:][0]) - 1
        num_of_days = arg if arg >= 0 else 0
    except Exception:
        num_of_days = 0

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
    num_of_restaurants = len(restaurants)

    for restaurant in range(num_of_restaurants):
        queue.put(restaurant)

    return queue


def get_menus_thread(queue, menus, num_of_days):
    while not queue.empty():
        restaurant = queue.get()
        data = request_menu(restaurant, num_of_days)
        r = restaurants[restaurant][0]

        if r == 'J.A. Pripps':
            menu = parse_pripps_menu(data, num_of_days)
        else:
            menu = parse_menu(data)

        map_data(menus, menu, restaurant)
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
    start_date, end_date = get_dates(num_of_days)

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


def map_data(menus, data, restaurant):
    num_of_restaurants = len(restaurants)
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


# -----------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------
def request_menu(restaurant, num_of_days):
    url = get_url(restaurant, num_of_days)

    try:
        if six.PY2:
            return urllib2.urlopen(url).read()
        elif six.PY3:
            return urllib.request.urlopen(url).read().decode('utf-8')

    except urllib2.HTTPError as e:
        print("HTTPError: {}".format(e.code))

    except urllib2.URLError as e:
        print("URLError: {}".format(e.reason))

    except httplib.HTTPException as e:
        print("HTTPException: {}".format(e))

    except Exception as e:
        print("Exception: {}".format(e))


def get_url(restaurant, num_of_days):
    r = restaurants[restaurant][0]

    if r == 'J.A. Pripps':
        return restaurants[restaurant][1]
    else:
        start_date, end_date = get_dates(num_of_days)

        return api.url(
            restaurants[restaurant][1],
            start_date,
            end_date)


def get_dates(num_of_days):
    today = datetime.today()
    end_date = (today + timedelta(days=num_of_days)) \
        .strftime(C.format('Ymd'))
    start_date = today.strftime(C.format('Ymd'))

    return start_date, end_date


def format_date(date):
    return datetime.strptime(
        date[:-3], C.format('mdYHMS')).strftime(C.format('Ymd'))


def append_data(menu, date, dish, dish_type):
    menu.append(date)
    menu.append(dish + color.dim(" (" + dish_type + ")"))


# -----------------------------------------------------------------
# PRINT
# -----------------------------------------------------------------
def print_data(menus):
    if not menus:
        print('INGEN DATA')
        quit()

    for key in sorted(menus):
        print()
        print_date(key)

        for restaurant, menu in enumerate(menus[key]):
            print_restaurant(menu, restaurant)

            for dish in menu:
                print_element(dish)
    print()


def print_date(date):
    dt = datetime.strptime(date, C.format('Ymd')).strftime('%a')
    print(color.BOLD + color.green(dt))


def print_restaurant(menu, restaurant):
    print(color.blue(restaurants[restaurant][0]))
    if not menu:
        print(C.dot() + color.dim('INGEN MENY'))


def print_element(dish):
    ingredient = C.meatballs()
    match = re.search(r'\b' + re.escape(ingredient)
                      + r'\b', dish, re.IGNORECASE)

    try:
        index = match.start()
    except AttributeError:
        print(C.dot() + dish)
        return

    print_match(dish, ingredient, index)


def print_match(dish, ingredient, index):
    l = (index + len(ingredient))
    head = dish[0:index]
    body = dish[index:l]
    tail = dish[l:]
    print(C.dot(), head, color.blink(body), tail)


# -----------------------------------------------------------------
# CONSTANS
# -----------------------------------------------------------------
class api:
    URL = \
        'http://carbonateapiprod.azurewebsites.net/' \
        'api/v1/mealprovidingunits/'

    @staticmethod
    def url(restaurant, start_date, end_date):
        return api.URL + restaurant + \
            '-08d558129279/dishoccurrences?' \
            'startDate=' + start_date + \
            '&endDate=' + end_date


class C:
    @staticmethod
    def dot():
        return C.decode('· ')

    @staticmethod
    def meatballs():
        return C.decode('kötbullar')

    @staticmethod
    def decode(string):
        return string.decode("utf-8") if six.PY2 else string

    @staticmethod
    def format(arg):
        return {
            'Ymd': '%Y-%m-%d',
            'mdYHMS': '%m/%d/%Y %H:%M:%S'
        }[arg]


class color:
    DEFAULT = '\033[0m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    BOLD = "\033[1m"
    BLINK = '\33[5m'
    DIM = '\033[2m'

    @staticmethod
    def dim(output):
        return color.DIM + output + color.DEFAULT

    @staticmethod
    def green(output):
        return color.GREEN + output + color.DEFAULT

    @staticmethod
    def blue(output):
        return color.BLUE + output + color.DEFAULT

    @staticmethod
    def blink(output):
        return color.BLINK + output + color.DEFAULT


if __name__ == "__main__":
    main()
