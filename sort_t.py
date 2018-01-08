#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
# filename: sort_t.py

import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime
import threading

############PROXY###########
timeout = 3

from tools import *

###多线程筛选
def sort_list(l, price=18, day=10):
    start_time = datetime.now()
    a = len(l)
    l1 = sort_price_list(l, price)
    l2 = sort_ma_list(l1, day)
    b = len(l2)
    end_time = datetime.now()
    timedelsta = (end_time - start_time).seconds
    print('过滤掉%s支股票，还剩%s支股票，耗时%s秒。' % (a-b, b, timedelsta))
    return(l2)

########################### 筛选方法 #############################
### 筛选价格
def sort_price(share_code, target_price=18):
    #print('检查 %s 价格是否低于%s元' % (share_code, target_price))
    price = price_now(share_code)[0]
    if price == '':
        li.remove(share_code)
        print('%s 无法获取价格。' % share_code)
    elif price > target_price:
        li.remove(share_code)
        print('%s 不符合条件。' % share_code)
    else:
        print('%s 符合条件!' % share_code)

# 筛选MA
def sort_ma(share_code, days=10):
    ma = ma_hist(share_code, days)
    if ma == ([], [], [], []):
        print('%s 获取数据失败！' % share_code)
        li.remove(share_code)
    else:
        for l in range(days):
            if ma[0][l] > ma[1][l]:
                li.remove(share_code)
                print('%s 不符合条件：MA10连续%s日大于MA5。' % (share_code, days))
                break
            if l == days-1:
                globals()['ma'+share_code] = (ma[0][0], ma[1][0], ma[2][0])
                print('-----成功获取 %s MA5/10历史数据-----' % share_code)


# 多线程筛选价格
def sort_price_list(l, target_price=18):
    global li
    print('筛选价格中, 一共%s支股票。' % len(l))
    li = list(l)
    threads = []
    for i in l:
        a = threading.Thread(target=sort_price, args=(i, target_price))
        threads.append(a)
        a.start()
    for t in threads:
        t.join()
    a = len(l)
    b = len(li)
    print('移除 %s 支股票价格低于%s元，列表中还剩 %s' % (a-b, target_price, b))
    return(li)

# 多线程筛选MA
def sort_ma_list(l, days=10):
    global li
    print('筛选MA10连续%s日大于MA5, 一共%s支股票。' % (days, len(l)))
    li = list(l)
    threads = []
    for i in l:
        a = threading.Thread(target=sort_ma, args=(i, days))
        threads.append(a)
        a.start()
    for t in threads:
        t.join()
    a = len(l)
    b = len(li)
    print('移除 %s 支股票不符合MA10连续%s日大于MA5，列表中还剩 %s' % (a-b, days, b))
    return(li)



def help():
    print('''
    多线程
    sort_list(list, price=18, day=10)
        sort_price_list(list, target_price=18)
          sort_price()
        sort_ma_list(list, days=10)
          sort_ma()
    help()
    ''')
