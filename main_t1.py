#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
# filename: main_t1.py

from sharelist_t import share_list
import sort_t

share_list = sort_t.sort_list(share_list)
last_ma = sort_t.last_ma

import monitor1
monitor1.ma_monitor_start(share_list, last_ma)


import code
code.interact(banner = "", local = locals())
