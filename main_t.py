#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
# filename: main_t.py

from sharelist_t import share_list
import sort_t

share_list = sort_t.sort_list(share_list)

import code
code.interact(banner = "", local = locals())