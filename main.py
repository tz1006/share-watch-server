#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
# filename: main.py

from sharelist import share_list
import sort

share_list = sort.sort_list(share_list)
last_ma = sort.last_ma

from monitor import *
ma_monitor_start(share_list, last_ma)


import code
code.interact(banner = "", local = locals())
