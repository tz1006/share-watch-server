#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
# filename: monitor.py

import sms
from tools import *
from datetime import datetime
from pytz import timezone
import threading
import os
import sqlite3

##########################################
# 监视程序
# 启动关闭MA监视
def ma_monitor_start(l, dic, count=9999):
    global last_ma
    last_ma = dic
    a = threading.Thread(target=ma_monitor, args=(l, count,))
    a.start()

def ma_monitor_stop():
    globals()['ma_monitor_status'] = False
    print('监视结束！')

# MA监视循环
def ma_monitor(l, count=9999):
    global buy_list
    global ma_monitor_status
    globals()['ma_monitor_status'] = True
    buy_list = []
    create_ma_form('MA')
    c = 0
    print('开始扫描，一共%s次。' % count)
    sms.send_sms(16267318573, '开始扫描')
    start_time = datetime.now()
    while c < count:
        while globals()['ma_monitor_status'] != False:
            c += 1
            # time.sleep(10)
            for i in l:
                ma_checker(i)
            end_time = datetime.now()
            timedelsta = (end_time - start_time).seconds
            print('第%s次扫描完成, 一共%s支股票，已找到%s支股票符合。 本次扫描耗时%s秒。' % (c, len(l), len(buy_list), timedelsta))
            start_time = end_time

# Ma监视条件
def ma_checker(stock_code):
    ma = ma_now(stock_code)
    # MA5大于MA10
    if ma[0] >= ma[1]:
        if ma[0] >= last_ma[stock_code][0] and ma[1] >= last_ma[stock_code][1]:
            if ma[0] >= ma[2]:
                if stock_code not in buy_list:
                    buy_list.append(stock_code)
                    time_now = datetime.now(timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
                    text = '%s交叉预警 %s' % (stock_code, time_now)
                    sms.send_sms(16267318573, text)
                    print('%s买入时机' % stock_code)
                    insert_ma_data(stock_code, ma)


############################################
# 数据库部分
# 在数据库'MA'中建立表 '17-12-27'/ CODE/ NAME/ PRICE/ AVERAGE/ MA5/ MA10/ MA20/ MA30/ TIME/ TIMECROSS/ MARKET
def create_ma_form(dbname):
    if os.path.exists('database') == False:
        os.makedirs('database')
    date = datetime.now(timezone('Asia/Shanghai')).strftime('\"%y-%m-%d\"')
    conn = sqlite3.connect('database/%s.db' % dbname)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS %s
        (CODE TEXT PRIMARY KEY UNIQUE,
        NAME   TEXT,
        PRICE  TEXT,
        AVERAGE  TEXT,
        MA5  TEXT,
        MA10  TEXT,
        MA20  TEXT,
        MA30  TEXT,
        TIME   TEXT,
        TIMECROSS   TEXT,
        MARKET   TEXT);''' % date)
    conn.commit()
    conn.close()
    print("Form %s Created in %s!" % (date, dbname))

# 在数据库'MA'，表'17-12-27'中 写入 / CODE/ NAME/ PRICE/ AVERAGE/ MA5/ MA10/ MA20/ MA30/ TIME/ TIMECROSS/ MARKET
def insert_ma_data(stock_code, ma_now):
    prices = price_now(stock_code)
    price = str(prices[0])
    average = str(prices[1])
    name = share_name(stock_code)
    ma5 = ma_now[0]
    ma10 = ma_now[1]
    ma20 = ma_now[2]
    ma30 = ma_now[3]
    time = datetime.now(timezone('Asia/Shanghai')).strftime('%H:%M:%S')
    formname = datetime.now(timezone('Asia/Shanghai')).strftime('\"%y-%m-%d\"')
    conn = sqlite3.connect('database/MA.db')
    c = conn.cursor()
    print(stock_code, name, price, average, time)
    c.execute("INSERT OR IGNORE INTO %s (CODE, NAME, PRICE, AVERAGE, MA5, MA10, MA20, MA30, TIME, MARKET) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" % formname,(stock_code, name, price, average, ma5, ma10, ma20, ma30, time, share_market(stock_code)))
    conn.commit()
    conn.close()
    print('写入 %s 数据成功！' % stock_code)



def help():
    print('''
    ma_monitor_start(list, count=9999)
    ma_monitor_stop()
      ma_monitor(l, count=9999)
        ma_checker(stock_code)

    help()
    ''')

help()
