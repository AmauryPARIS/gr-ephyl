#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2019 <+YOU OR YOUR COMPANY+>.
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

import numpy as np
import pmt
import time
import random
from gnuradio import gr, gr_unittest, blocks


class tag_2_msg_char(gr.sync_block):
    """
    docstring for block tag_2_msg_char
    """


    def __init__(self,wanted_tag="corr_start"):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Slot tag to Message',   # will show up in GRC
            in_sig=[np.uint8],
            out_sig=[]
        )
        self.wanted_tag = wanted_tag
        self.message_port_register_out(pmt.to_pmt("slot_msg"))        

    def work(self, input_items, output_items):

        num_input_items = len(input_items[0])
        nread = self.nitems_read(0)
        tags = self.get_tags_in_range(0, nread, nread+num_input_items)

        for tag in tags:
            msg = pmt.cons(tag.key,tag.value)
            msg_tup = pmt.to_python(msg)
            if msg_tup[0] == self.wanted_tag :
                # print msg
                slot_msg = pmt.cons(pmt.make_dict(), msg)
                self.message_port_pub(pmt.to_pmt("slot_msg"), slot_msg)
                break

        return num_input_items