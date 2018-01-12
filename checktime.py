#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
# filename: checktime.py

from datetime import datetime, timedelta
from pytz import timezone

def next_trading_date(debug=0):
    now_time = datetime.now(timezone('Asia/Shanghai'))
    # 如果今天周五周六
    if 3 < now_time.weekday() < 6:
        date_diff = 7-now_time.weekday()
    else:
        date_diff = 1
    if debug == 1:
        date_diff = 1
        next_date = now_time + timedelta(days=date_diff)
        return next_date
    next_date = now_time + timedelta(days=date_diff)
    next_year = next_date.year
    next_month = next_date.month
    next_day =  next_date.day
    return(next_year, next_month, next_day)


def check_time():
    now_time = datetime.now(timezone('Asia/Shanghai')).replace(tzinfo=None)
    # 如果今天工作日
    if 0 <= now_time.weekday() < 5:
        # 如果是盘前
        if now_time.hour < 9:
            start_year = now_time.year
            start_month = now_time.month
            start_day = now_time.day
            start_time = datetime.strptime('%s-%s-%s 09:25:00' % (start_year, start_month, start_day), "%Y-%m-%d %H:%M:%S")
            sleep_time = (start_time-now_time).total_seconds()
            sleep_day = sleep_time // 86400
            sleep_hour = (sleep_time % 86400) // 3600
            sleep_second = ((sleep_time % 86400) % 3600) // 60
            print('睡眠%s天%小时%秒后启动程序' % (sleep_day, sleep_hour, sleep_second))
            time.sleep(sleep_time)
        # 如果是盘后
        elif now_time.hour > 14:
            next_date = next_trading_date()
            start_year = next_date[0]
            start_month = next_date[1]
            start_day = next_date[2]
            start_time = datetime.strptime('%s-%s-%s 09:25:00' % (start_year, start_month, start_day), "%Y-%m-%d %H:%M:%S")
            sleep_time = (start_time-now_time).total_seconds()
            sleep_day = sleep_time // 86400
            sleep_hour = (sleep_time % 86400) // 3600
            sleep_second = ((sleep_time % 86400) % 3600) // 60
            print('睡眠%s天%小时%秒后启动程序' % (sleep_day, sleep_hour, sleep_second))
            time.sleep(sleep_time)
        else:
            print('启动程序！')
    else:
        next_date = next_trading_date()
        start_year = next_date[0]
        start_month = next_date[1]
        start_day = next_date[2]
        start_time = datetime.strptime('%s-%s-%s 09:25:00' % (start_year, start_month, start_day), "%Y-%m-%d %H:%M:%S")
        sleep_time = (start_time-now_time).total_seconds()
        sleep_day = sleep_time // 86400
        sleep_hour = (sleep_time % 86400) // 3600
        sleep_second = ((sleep_time % 86400) % 3600) // 60
        print('睡眠%s天%小时%秒后启动程序' % (sleep_day, sleep_hour, sleep_second))
        time.sleep(sleep_time)


check_time()
