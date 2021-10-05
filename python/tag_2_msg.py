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

class tag_2_msg(gr.sync_block):
    """
    2BDone
    """
    def __init__(self,wanted_tag="corr_start"):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Tag detection to Message',   # will show up in GRC
            in_sig=[np.uint8],
            out_sig=[]
        )
        self.wanted_tag = wanted_tag
        self.message_port_register_out(pmt.to_pmt("tag_msg"))
        self.delay = 0

    def work(self, input_items, output_items):

        num_input_items = len(input_items[0])
        nread = self.nitems_read(0)
        tags = self.get_tags_in_range(0, nread, nread+num_input_items)

        # if 1 in input_items[0]:
        # for i in input_items[0]:
        #     if i == 1 :
        #         msg = [self.wanted_tag,1,list(input_items[0]).index(i)]
        #         trig_msg = pmt.cons(pmt.make_dict(), pmt.to_pmt(msg))
        #         self.message_port_pub(pmt.to_pmt("tag_msg"), trig_msg)
        #         break
        # return num_input_items

        for tag in tags:
            msg = [pmt.to_python(tag.key),pmt.to_python(tag.value),tag.offset]

            if msg[0] == "rx_time" :
                # print "HERE"
                # print msg[2]
                # print nread
                # print tags.index(tag)
                # print "=============================="
                self.delay = abs(msg[2] - (nread+tags.index(tag)))

            if msg[0] == self.wanted_tag and any(input_items[0]):
                if self.delay :
                    msg[2] += self.delay
                self.delay = 0
                trig_msg = pmt.cons(pmt.make_dict(), pmt.to_pmt(msg))
                self.message_port_pub(pmt.to_pmt("tag_msg"), trig_msg)
                break
        return num_input_items
