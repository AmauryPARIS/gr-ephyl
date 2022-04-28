#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2022 gr-ephyl author.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr
import numpy as np
import pmt
from datetime import datetime

class tag_check(gr.sync_block):
    """
    docstring for block tag_check
    """
    def __init__(self, title = ""):
        gr.sync_block.__init__(self,
            name="tag_check",
            in_sig=[np.complex64],
            out_sig=None)

        self.title = title 


    def work(self, input_items, output_items):
        in0 = input_items[0]
        tags = self.get_tags_in_window(0, 0, len(in0))        

        # Get tags
        for tag in tags:
            key = pmt.to_python(tag.key) 
            value = pmt.to_python(tag.value) 
            now = datetime.now().time()
            print("%s-%s-%s-%s\n" % (self.title, now, key, value)) 
        
        self.consume_each(len(in0))

        return 0

