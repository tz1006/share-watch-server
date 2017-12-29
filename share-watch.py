# !/Python

import requests
import sqlite3
import threading
import time
import os
from bs4 import BeautifulSoup
from datetime import date
from datetime import datetime

############PROXY###########
timeout = 5

proxies = {
    "https": "http://165.227.100.201:80",
    "https": "http://183.235.254.159:8080",
    "https": "http://183.235.254.159:8080"
}
proxies = None

########--Tools--########

# Sqlite
def delete_form(dbname, formname):
    conn = sqlite3.connect('database/%s.db' % dbname)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS %s;" % formname)
    conn.commit()
    conn.close()
    print("成功从数据库 %s 中清除表 %s " % (dbname, formname))


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
    span = '%s%s%s' % (today.year, today.month, today.day)
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
    else:
        ma_data = r.text.split('[')[1].split(']')[0].split(',')
        ma5 = float(ma_data[0])
        ma10 = float(ma_data[1])
        ma20 = float(ma_data[2])
    #print(ma5, ma10)
    return(ma5, ma10)

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
    if ma == {}:
        pass
    else:
        if len(ma) < days:
            pass
        else:
            for l in range(days):
                ma5.append(float(ma[-l-1][8]))
                ma10.append(float(ma[-l-1][9]))
    return(ma5, ma10)

##################---plot---########################
import pylab as pl
from matplotlib.font_manager import FontProperties  
import platform

def plot_ma(stock_code, MA5, MA10, DATE, listname):
    if os.path.exists('MA曲线图/%s' % listname) == False:
        os.makedirs('MA曲线图/%s' % listname)
    if platform.system() == 'Linux':
        font = FontProperties(fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc", size=14)
    elif platform.system() == 'Windows':
        #pl.rcParams['font.sans-serif']=['SimHei']
        font = FontProperties(fname="C:\\Windows\\Fonts\\Microsoft YaHei UI\\msyh.ttc", size=14)
    elif platform.system() == 'Darwin':
        font = FontProperties(fname="/Library/Fonts/STHeiti Medium.ttc", size=14)
    title = '%s %s' % (stock_code, share_name(stock_code))
    pl.title(title, fontproperties=font)
    a, = pl.plot(DATE, MA5, 'r-')
    b, = pl.plot(DATE, MA10, 'b-')
    pl.legend([a, b], ('MA5', 'MA10'), numpoints=1)
    pl.savefig('MA曲线图/%s/%s.png' % (listname, sscode(stock_code)))
    pl.close()
    print('Plot %s success' % title)

def get_ma(stock_code):
    ua_mo = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_1 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0 Mobile/15B150 Safari/604.1'
    header = {'User-Agent':ua_mo}
    ma_url = 'http://api.finance.ifeng.com/akdaily/?code=%s&type=last' % sscode(stock_code)
    now_url = 'http://api.finance.ifeng.com/aminhis/?code=%s&type=five' % sscode(stock_code)
    now = requests.get(now_url, headers = header).json()[-1]['record'][-1]
    ma = requests.get(ma_url, headers = header).json()['record']
    # MA5
    ma5_now = float(now[4])
    ma5_1 = float(ma[-1][8])
    ma5_2 = float(ma[-2][8])
    ma5_3 = float(ma[-3][8])
    ma5_4 = float(ma[-4][8])
    ma5_5 = float(ma[-5][8])
    ma5_6 = float(ma[-6][8])
    ma5_7 = float(ma[-7][8])
    ma5_8 = float(ma[-8][8])
    ma5_9 = float(ma[-9][8])
    ma5_10 = float(ma[-10][8])
    # MA10
    ma10_now = float(now[5])
    ma10_1 = float(ma[-1][9])
    ma10_2 = float(ma[-2][9])
    ma10_3 = float(ma[-3][9])
    ma10_4 = float(ma[-4][9])
    ma10_5 = float(ma[-5][9])
    ma10_6 = float(ma[-6][9])
    ma10_7 = float(ma[-7][9])
    ma10_8 = float(ma[-8][9])
    ma10_9 = float(ma[-9][9])
    ma10_10 = float(ma[-10][9])
    ma5_list = [ma5_1, ma5_2, ma5_3, ma5_4, ma5_5, ma5_6, ma5_7, ma5_8, ma5_9, ma5_10]
    ma10_list = [ma10_1, ma10_2, ma10_3, ma10_4, ma10_5, ma10_6, ma10_7, ma10_8, ma10_9, ma10_10]
    date_list = []
    for i in range(-1, -11, -1):
        date_list.append(ma[i][0].split('-',1)[1])
    return(stock_code, ma5_list, ma10_list, date_list)

def plot_images(CODE, listname):
    a = get_ma(CODE)
    plot_ma(a[0], a[1], a[2], a[3], listname)

def plot_list(listname):
    for i in globals()[str(listname)]:
        try:
            plot_images(i, listname)
        except:
            pass


#######--Create share_list Database--#######
# 创建share_list数据库
def create_share_list_db():
    if os.path.exists('database') == False:
        os.makedirs('database')
    conn = sqlite3.connect('database/share_list.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS SHA
        (CODE TEXT PRIMARY KEY UNIQUE,
        NAME   TEXT);''')
    c.execute('''CREATE TABLE IF NOT EXISTS SZA
        (CODE TEXT PRIMARY KEY UNIQUE,
        NAME   TEXT);''')
    c.execute('''CREATE TABLE IF NOT EXISTS SZZX
        (CODE TEXT PRIMARY KEY UNIQUE,
        NAME   TEXT);''')
    c.execute('''CREATE TABLE IF NOT EXISTS SZCY
        (CODE TEXT PRIMARY KEY UNIQUE,
        NAME   TEXT);''')
    conn.commit()
    conn.close()
    print("成功创建share_list数据库 表SHA，SZA，SZZX，SZCY，等待数据写入。")


# 插入股票代码到数据库share_list
def insert_share_codes_t():
    start_time = datetime.now()
    globals()['share_list'] = list(set(share_list))
    delete_form('share_list', 'SHA')
    delete_form('share_list', 'SZA')
    delete_form('share_list', 'SZZX')
    delete_form('share_list', 'SZCY')
    create_share_list_db()
    threads = []
    for i in share_list:
        a = threading.Thread(target=insert_code, args=(i,))
        threads.append(a)
        while threading.activeCount() >= 30:
            time.sleep(0.5)
        a.start()
    end_time = datetime.now()
    timedelsta = (end_time - start_time).seconds
    print('写入数据库 %s 支股票！耗时 %s 秒。' % (len(share_list), timedelsta))

# 插入股票代码 单线程
def insert_share_codes():
    start_time = datetime.now()
    globals()['share_list'] = list(set(share_list))
    delete_form('share_list', 'SHA')
    delete_form('share_list', 'SZA')
    delete_form('share_list', 'SZZX')
    delete_form('share_list', 'SZCY')
    create_share_list_db()
    conn = sqlite3.connect('database/share_list.db')
    c = conn.cursor()
    for code in share_list:
        name = share_name(code)
        formname = share_market_code(code)
        c.execute("INSERT INTO %s (CODE, NAME) VALUES (?, ?)" % formname,(code, name))
    conn.commit()
    conn.close()
    end_time = datetime.now()
    timedelsta = (end_time - start_time).seconds
    print('单线程写入数据库 %s 支股票！耗时 %s 秒。' % (len(share_list), timedelsta))


# 插入股票代码到数据库share_list 多线程
def insert_share_codes_t():
    start_time = datetime.now()
    globals()['share_list'] = list(set(share_list))
    delete_form('share_list', 'SHA')
    delete_form('share_list', 'SZA')
    delete_form('share_list', 'SZZX')
    delete_form('share_list', 'SZCY')
    create_share_list_db()
    threads = []
    for i in share_list:
        a = threading.Thread(target=insert_code, args=(i,))
        threads.append(a)
        while threading.activeCount() >= 30:
            time.sleep(0.5)
        a.start()
    for t in threads:
        t.join()
    end_time = datetime.now()
    timedelsta = (end_time - start_time).seconds
    print('多线程写入数据库 %s 支股票！耗时 %s 秒。' % (len(share_list), timedelsta))

# 插入股票代码
def insert_code(code):
    name = share_name(code)
    formname = share_market_code(code)
    conn = sqlite3.connect('database/share_list.db')
    c = conn.cursor()
    c.execute("INSERT INTO %s (CODE, NAME) VALUES (?, ?)" % formname,(code, name))
    conn.commit()
    conn.close()


#################--load-pages--####################

def get_sza_page(page_num, afterdate=20171201):
    # print('获取第%s页数据。' % page_num)
    url = 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-FALSE&CATALOGID=1110&TABKEY=tab2&tab2PAGENO=%s' % page_num
    s = requests.session()
    s.keep_alive = False
    r = None
    while r == None:
        try:
            r = s.get(url, timeout=timeout)
        except:
            pass
        else:
            pass
            #print('获取第%s页数据。' % page_num)
    html = r.content
    soup = BeautifulSoup(html, "html.parser")
    source = soup.select('tr[bgcolor="#ffffff"]')
    source1 = soup.select('tr[bgcolor="#F8F8F8"]')
    source += source1
    for l in source:
        code = l.select('td')[2].text
        listing_date = l.select('td')[4].text
        if listing_date != '-':
            d = listing_date.split('-')
            n = int(d[0]+d[1]+d[2])
            if n < afterdate:
                sza.append(code)
        else: 
            sza.append(code)

def get_szzx_page(page_num):
    # print('获取第%s页数据。' % page_num)
    url = 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-FALSE&CATALOGID=1110&TABKEY=tab5&tab5PAGENO=%s' % page_num
    s = requests.session()
    s.keep_alive = False
    r = None
    while r == None:
        try:
            r = s.get(url, timeout=timeout)
        except:
            pass
        else:
            pass
            #print('获取第%s页数据。' % page_num)
    html = r.content
    soup = BeautifulSoup(html, "html.parser")
    source = soup.select('tr[bgcolor="#ffffff"]')
    source1 = soup.select('tr[bgcolor="#F8F8F8"]')
    source += source1
    for l in source:
        code = l.a.u.text
        szzx.append(code)

def get_szcy_page(page_num):
    # print('获取第%s页数据。' % page_num)
    url = 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-FALSE&CATALOGID=1110&TABKEY=tab6&tab6PAGENO=%s' % page_num
    s = requests.session()
    s.keep_alive = False
    r = None
    while r == None:
        try:
            r = s.get(url, timeout=timeout)
        except:
            pass
        else:
            pass
            #print('获取第%s页数据。' % page_num)
    html = r.content
    soup = BeautifulSoup(html, "html.parser")
    source = soup.select('tr[bgcolor="#ffffff"]')
    source1 = soup.select('tr[bgcolor="#F8F8F8"]')
    source += source1
    for l in source:
        code = l.a.u.text
        szcy.append(code)


##############==============================================############
# 导入股票
def get_list():
    load_list()


# 单线程导入
def load_list(listname='share_list'):
    globals()[listname] = []
    start_time = datetime.now()
    get_sha_list()
    get_sza_list()
    get_szzx_list()
    get_szcy_list()
    globals()[listname] = list(set(globals()[listname]))
    end_time = datetime.now()
    timedelsta = (end_time - start_time).seconds
    print('单线程导入，一共导入 %s 支股票，耗时 %s 秒。' % (len(globals()[listname]), timedelsta))
    threading.Thread(target=insert_share_codes, args=()).start()

# 多线程导入
def load_list_t(listname='share_list'):
    globals()[listname] = []
    start_time = datetime.now()
    get_sha_list()
    get_sza_list_t()
    get_szzx_list_t()
    get_szcy_list_t()
    globals()[listname] = list(set(globals()[listname]))
    end_time = datetime.now()
    timedelsta = (end_time - start_time).seconds
    print('多线程导入，一共导入 %s 支股票，耗时 %s 秒。' % (len(globals()[listname]), timedelsta))
    threading.Thread(target=insert_share_codes, args=()).start()

# 导入上海A股列表share_list并去除20171201以后上市的股票
def get_sha_list(listname='share_list', afterdate=20171201):
    global sha
    sha = []
    if listname in globals().keys():
        if listname != 'share_list':
            globals()[listname] = []
    else:
        globals()[listname] = []
    start_time = datetime.now()
    url = 'http://query.sse.com.cn/security/stock/getStockListData2.do?&stockType=1&pageHelp.beginPage=1&pageHelp.pageSize=2000'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0',
        'Referer': 'http://www.sse.com.cn/assortment/stock/list/share/'
    }
    stock_data = requests.get(url, headers = header).json()['pageHelp']['data']
    for i in range(len(stock_data)):
        code = stock_data[i]['SECURITY_CODE_A']
        listing_date = stock_data[i]['LISTING_DATE']
        if listing_date != '-':
            d = listing_date.split('-')
            n = int(d[0]+d[1]+d[2])
            if n < afterdate:
                sha.append(code)
        else: 
            globals()[listname].append(code)
            sha.append(code)
    globals()[listname] += sha
    end_time = datetime.now()
    timedelsta = (end_time - start_time).seconds
    print('从 沪A 成功导入%s支股票，耗时%s秒。' % (len(sha), timedelsta))


###########------单线程导入---------##########
# 导入深圳A股列表share_list并去除20171201以后上市的股票
def get_sza_list(listname='share_list', afterdate=20171201):
    global sza
    sza = []
    if listname in globals().keys():
        if listname != 'share_list':
            globals()[listname] = []
    else:
        globals()[listname] = []
    index_url = 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-FALSE&CATALOGID=1110&TABKEY=tab2&tab2PAGENO=1'
    s = requests.session()
    s.keep_alive = False
    index_html = s.get(index_url).content
    index_soup = BeautifulSoup(index_html, "html.parser")
    index = int(index_soup.select('td')[-3].text.split()[1][1:-1])
    start_time = datetime.now()
    print('正在获取深A列表，一共%s页。' % (index+1))
    for i in range(index):
        i = i + 1
        get_sza_page(i, afterdate)
    globals()[listname] += sza
    end_time = datetime.now()
    timedelsta = (end_time - start_time).seconds
    print('从 深A 成功导入%s %s支股票。本次扫描单线程，耗时%s秒。' % (listname, len(sza), timedelsta))

# 导入深圳中小板share_list
def get_szzx_list(listname='share_list'):
    global szzx
    szzx = []
    if listname in globals().keys():
        if listname != 'share_list':
            globals()[listname] = []
    else:
        globals()[listname] = []
    index_url = 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-FALSE&CATALOGID=1110&TABKEY=tab5&tab5PAGENO=1'
    s = requests.session()
    s.keep_alive = False
    index_html = s.get(index_url).content
    index_soup = BeautifulSoup(index_html, "html.parser")
    index = int(index_soup.select('td')[-3].text.split()[1][1:-1])
    start_time = datetime.now()
    print('正在获取深圳中小板列表，一共%s页。' % (index+1))
    for i in range(index):
        i = i + 1
        get_szzx_page(i)
    globals()[listname] += szzx
    end_time = datetime.now()
    timedelsta = (end_time - start_time).seconds
    print('从 深圳中小板 成功导入%s %s支股票。本次扫描单线程，耗时%s秒。' % (listname, len(szzx), timedelsta))

# 导入深圳创业板share_list
def get_szcy_list(listname='share_list'):
    global szcy
    szcy = []
    if listname in globals().keys():
        if listname != 'share_list':
            globals()[listname] = []
    else:
        globals()[listname] = []
    index_url = 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-FALSE&CATALOGID=1110&TABKEY=tab6&tab6PAGENO=1'
    s = requests.session()
    s.keep_alive = False
    index_html = s.get(index_url).content
    index_soup = BeautifulSoup(index_html, "html.parser")
    index = int(index_soup.select('td')[-3].text.split()[1][1:-1])
    start_time = datetime.now()
    print('正在获取深圳创业板列表，一共%s页。' % (index+1))
    for i in range(index):
        i = i + 1
        get_szcy_page(i)
    globals()[listname] += szcy
    end_time = datetime.now()
    timedelsta = (end_time - start_time).seconds
    print('从 深圳创业板 成功导入%s %s支股票。本次扫描单线程，耗时%s秒。' % (listname, len(szcy), timedelsta))


###########------多线程导入---------##########
# 导入深圳A股列表share_list并去除20171201以后上市的股票
def get_sza_list_t(listname='share_list', afterdate=20171201):
    global sza
    sza = []
    if listname in globals().keys():
        if listname != 'share_list':
            globals()[listname] = []
    else:
        globals()[listname] = []
    index_url = 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-FALSE&CATALOGID=1110&TABKEY=tab2&tab2PAGENO=1'
    s = requests.session()
    s.keep_alive = False
    index_html = s.get(index_url).content
    index_soup = BeautifulSoup(index_html, "html.parser")
    index = int(index_soup.select('td')[-3].text.split()[1][1:-1])
    threads = []
    start_time = datetime.now()
    print('正在获取深A列表，一共%s页。' % (index+1))
    for i in range(index):
        i = i + 1
        a = threading.Thread(target=get_sza_page, args=(i, afterdate,))
        threads.append(a)
        a.start()
    for t in threads:
        t.join()
    globals()[listname] += sza
    end_time = datetime.now()
    timedelsta = (end_time - start_time).seconds
    print('从 深A 成功导入%s %s支股票。本次扫描多线程，耗时%s秒。' % (listname, len(sza), timedelsta))

# 导入深圳中小板share_list
def get_szzx_list_t(listname='share_list'):
    global szzx
    szzx = []
    if listname in globals().keys():
        if listname != 'share_list':
            globals()[listname] = []
    else:
        globals()[listname] = []
    index_url = 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-FALSE&CATALOGID=1110&TABKEY=tab5&tab5PAGENO=1'
    s = requests.session()
    s.keep_alive = False
    index_html = s.get(index_url).content
    index_soup = BeautifulSoup(index_html, "html.parser")
    index = int(index_soup.select('td')[-3].text.split()[1][1:-1])
    threads = []
    start_time = datetime.now()
    print('正在获取深圳中小板列表，一共%s页。' % (index+1))
    for i in range(index):
        i = i + 1
        a = threading.Thread(target=get_szzx_page, args=(i,))
        threads.append(a)
        a.start()
    for t in threads:
        t.join()
    globals()[listname] += szzx
    end_time = datetime.now()
    timedelsta = (end_time - start_time).seconds
    print('从 深圳中小板 成功导入%s %s支股票。本次扫描多线程，耗时%s秒。' % (listname, len(szzx), timedelsta))

# 导入深圳创业板share_list
def get_szcy_list_t(listname='share_list'):
    global szcy
    szcy = []
    if listname in globals().keys():
        if listname != 'share_list':
            globals()[listname] = []
    else:
        globals()[listname] = []
    index_url = 'http://www.szse.cn/szseWeb/FrontController.szse?ACTIONID=7&AJAX=AJAX-FALSE&CATALOGID=1110&TABKEY=tab6&tab6PAGENO=1'
    s = requests.session()
    s.keep_alive = False
    index_html = s.get(index_url).content
    index_soup = BeautifulSoup(index_html, "html.parser")
    index = int(index_soup.select('td')[-3].text.split()[1][1:-1])
    threads = []
    start_time = datetime.now()
    print('正在获取深圳创业板列表，一共%s页。' % (index+1))
    for i in range(index):
        i = i + 1
        a = threading.Thread(target=get_szcy_page, args=(i,))
        threads.append(a)
        a.start()
    for t in threads:
        t.join()
    globals()[listname] += szcy
    end_time = datetime.now()
    timedelsta = (end_time - start_time).seconds
    print('从 深圳创业板 成功导入%s %s支股票。本次扫描多线程，耗时%s秒。' % (listname, len(szcy), timedelsta))

############################==================================##########################
###多线程筛选
def sort_list(listname='share_list', price=18, day=10):
    a = len(globals()[listname])
    sort_price_list(listname, price)
    sort_ma_list(listname, day)
    b = len(globals()[listname])
    print('过滤掉%s支股票，还剩%s支股票' % (a-b, b))

# 筛选价格
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

def sort_price_list(listname='share_list', target_price=18):
    global li
    li = list(globals()[listname])
    threads = []
    print('筛选%s中，价格低于%s元, 一共%s支股票。' % (listname, target_price,len(globals()[listname])))
    for i in globals()[listname]:
        a = threading.Thread(target=sort_price, args=(i, target_price))
        threads.append(a)
        a.start()
    for t in threads:
        t.join()
    a = len(globals()[listname])
    b = len(li)
    globals()[listname] = li
    print('已经从 %s 移除 %s 支股票，列表中还剩 %s' % (listname, a-b, b))

# 筛选MA
def sort_ma(share_code, days=10):
    ma = ma_hist(share_code, days)
    if ma == ([], []):
        print('%s 获取数据失败！' % share_code)
        li.remove(share_code)
    else:
        for l in range(days):
            if ma[0][l] > ma[1][l]:
                li.remove(share_code)
                print('%s 不符合条件：MA10连续%s日大于MA5。' % (share_code, days))
                break
            if l == days-1:
                globals()['ma'+share_code] = (ma[0][0], ma[1][0])
                print('-----成功获取 %s MA5/10历史数据-----' % share_code)

def sort_ma_list(listname='share_list', days=10):
    global li
    li = list(globals()[listname])
    threads = []
    print('筛选%s中MA10连续%s日大于MA5, 一共%s支股票。' % (listname, days, len(globals()[listname])))
    for i in globals()[listname]:
        a = threading.Thread(target=sort_ma, args=(i, days))
        threads.append(a)
        a.start()
    for t in threads:
        t.join()
    a = len(globals()[listname])
    b = len(li)
    globals()[listname] = li
    print('已经从 %s 移除 %s 支股票，列表中还剩 %s' % (listname, a-b, b))

##########################################
# 监视程序
# 启动关闭MA监视
def ma_monitor_start(listname='share_list', count=9999):
    global a
    a = threading.Thread(target=ma_monitor, args=())
    a.start()

def ma_monitor_stop():
    globals()['ma_monitor_status'] = True
    print('监视结束！')

# MA监视循环
def ma_monitor(listname='share_list', count=9999):
    global buy_list
    global ma_monitor_status
    globals()['ma_monitor_status'] = False
    buy_list = []
    create_ma_form('MA')
    c = 0
    print('开始扫描，一共%s次。' % count)
    start_time = datetime.now()
    while c < count:
        while ma_monitor_status != True:
            c += 1
            # time.sleep(10)
            for i in globals()[listname]:
                ma_checker(i)
            end_time = datetime.now()
            timedelsta = (end_time - start_time).seconds
            print('第%s次扫描完成, 一共%s支股票，已找到%s支股票符合。 本次扫描耗时%s秒。' % (c, len(globals()[listname]), len(buy_list), timedelsta))
            start_time = end_time

# Ma监视条件
def ma_checker(stock_code):
    ma = ma_now(stock_code)
    if ma[0] > ma[1]:
        if ma[0] > globals()['ma'+stock_code][0] and  ma[1] > globals()['ma'+stock_code][1]:
            if stock_code not in buy_list:
                buy_list.append(stock_code)
                print('%s买入时机' % stock_code)
                insert_ma_data(stock_code, ma)

# 在数据库'MA'中建立表 '17-12-27'/ CODE/ NAME/ PRICE/ AVERAGE/ TIME/ TIMECROSS/ OTHER
def create_ma_form(dbname):
    if os.path.exists('database') == False:
        os.makedirs('database')
    date = datetime.now().strftime('\"%y-%m-%d\"')
    conn = sqlite3.connect('database/%s.db' % dbname)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS %s
        (CODE TEXT PRIMARY KEY UNIQUE,
        NAME   TEXT,
        PRICE  TEXT,
        AVERAGE  TEXT,
        MA5  TEXT,
        MA10  TEXT,
        TIME   TEXT,
        TIMECROSS   TEXT,
        MARKET   TEXT);''' % date)
    conn.commit()
    conn.close()
    print("Form %s Created in %s!" % (date, dbname))

# 在数据库'MA'，表'17-12-27'中 写入 / CODE/ NAME/ PRICE/ AVERAGE/ TIME/
def insert_ma_data(stock_code, ma_now):
    prices = price_now(stock_code)
    price = str(prices[0])
    average = str(prices[1])
    name = share_name(stock_code)
    ma5 = ma_now[0]
    ma10 = ma_now[1]
    time = datetime.now().strftime('%H:%M:%S')
    formname = datetime.now().strftime('\"%y-%m-%d\"')
    conn = sqlite3.connect('database/MA.db')
    c = conn.cursor()
    print(stock_code, name, price, average, time)
    c.execute("INSERT OR IGNORE INTO %s (CODE, NAME, PRICE, AVERAGE, MA5, MA10, TIME, MARKET) VALUES (?, ?, ?, ?, ?, ?, ?, ?)" % formname,(stock_code, name, price, average, ma5, ma10, time, share_market(stock_code)))
    conn.commit()
    conn.close()
    print('写入 %s 数据成功！' % stock_code)

def help():
    print('''
    get_list()
        load_list()
            get_sha_list()
            get_sza_list()
            get_szzx_list()
            get_szcy_list()
        load_list_t()
            get_sha_list()
            get_sza_list_t()
            get_szzx_list_t()
            get_szcy_list_t()
        *insert_share_codes()
        *insert_share_codes_()
    
    sort_list()
        sort_price_list
        sort_ma_list
    ma_monitor_start()
    ma_monitor_stop()
    -plot_list('listname')
    ''')

help()

import code
code.interact(banner = "", local = locals())
