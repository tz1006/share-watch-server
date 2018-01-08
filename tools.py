#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
# filename: tools.py


# 工具集
import sqlite3
import requests

timeout = 3

########--Tools--########

def sscode(code):
    code = str(code)
    if code[0]+code[1] =='60':
        code = 'sh%s' % code
    else:
        code = 'sz%s' % code
    return code

def share_name(code):
    s = requests.session()
    s.keep_alive = False
    url = 'http://hq.sinajs.cn/list=%s' % sscode(code)
    r = None
    while r == None:
        r = s.get(url, timeout=timeout)
    name = r.text.split("\"")[1].split(",",1)[0]
    return name

def share_market(code):
    code = str(code)
    if code[0] =='6':
        return('沪市主板')
    elif code[0] =='3':
        return('创业板')
    else:
        if code[2] == '0':
            return('深市主板')
        else:
            return('中小板')

def share_market_code(code):
    code = str(code)
    if code[0] =='6':
        return('SHA')
    elif code[0] =='3':
        return('SZCY')
    else:
        if code[2] == '0':
            return('SZA')
        else:
            return('SZZX')


#######---get-data---#######

def price_now(stock_code):
    s = requests.session()
    s.keep_alive = False
    url = 'http://api.finance.ifeng.com/aminhis/?code=%s&type=five' % sscode(stock_code)
    r = None
    while r == None:
        try:
            r = s.get(url, timeout=timeout)
        except:
            pass
    if r.text == '':
        print('无法获取 %s 价格。' % stock_code)
        price = ''
        average = ''
    else:
        now = r.json()[-1]['record'][-1]
        # Price
        price = float(now[1])
        # Average
        average = float(now[4])
    return (price, average)

def ma_now(stock_code, debug=0):
    today = date.today()
    span = '%s%02d%02d' % (today.year, today.month, today.day)
    #print(span)
    url = 'http://pdfm.eastmoney.com/EM_UBG_PDTI_Fast/api/js?id=%s1&TYPE=k&rtntype=1&QueryStyle=2.2&QuerySpan=%s%%2C1&extend=ma' % (stock_code, span)
    s = requests.session()
    s.keep_alive = False
    r = None
    while r == None:
        try:
            r = s.get(url, proxies=proxies, timeout=timeout)
        except:
            pass
    if debug != 0:
        return r
    if r.text == '({stats:false})':
        ma5 = ''
        ma10 = ''
        ma20 = ''
    else:
        ma_data = r.text.split('[')[1].split(']')[0].split(',')
        ma5 = float(ma_data[0])
        ma10 = float(ma_data[1])
        ma20 = float(ma_data[2])
    #print(ma5, ma10)
    return(ma5, ma10, ma20)
 
def ma_hist(stock_code, days=10, debug=0):
    #ua_mo = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_1 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0 Mobile/15B150 Safari/604.1'
    #header = {'User-Agent':ua_mo}
    s = requests.session()
    s.keep_alive = False
    url = 'http://api.finance.ifeng.com/akdaily/?code=%s&type=last' % sscode(stock_code)
    r = None
    while r == None:
        try:
            r = s.get(url, proxies=proxies, timeout=timeout)
        except:
            pass
    if debug != 0:
        return r
    ma = r.json()['record']
    ma5 = []
    ma10 = []
    ma20 = []
    date = []
    if ma == {}:
        pass
    else:
        if len(ma) < days:
            pass
        else:
            for l in range(days):
                ma5.append(float(ma[-l-1][8]))
                ma10.append(float(ma[-l-1][9]))
                ma20.append(float(ma[-l-1][10]))
                date.append(datetime.strptime(ma[-l-1][0], '%Y-%m-%d').strftime("%b-%d"))
                #date.append(ma[-l-1][0].split('-',1)[1])
    return(ma5, ma10, ma20, date)


# HELP

def help():
    print('''
    # tools
    sscode(code)
    share_name(code)
    share_market(code)
    share_market_code(code)
    # data-tools
    price_now(stock_code)
    ma_now(stock_code)
    ma_hist(stock_code, days=10)
    ''')

