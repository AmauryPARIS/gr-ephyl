#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2021 gr-ephyl author.
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
from gnuradio import gr
import pmt, time
from datetime import datetime

class busy_tresh(gr.sync_block):
    """
    docstring for block busy_tresh
    """
    def __init__(self, tresh=5, log=False):
        gr.sync_block.__init__(self,
            name="busy_tresh",
            in_sig=[np.complex64],
            out_sig=[])

        self.message_port_register_out(pmt.to_pmt("feedback"))
        self.power_tresh = tresh

        self.state = ['IDLE','BCH','PUSCH','GUARD','FRAME']
        self.power_per_slot = np.array([])
        self.sample_buffer = np.array([])
        self.compute = False
        self.logged = log
        self.filename_log = "LOG_BS_busy_tresh_"+time.strftime("%d%m%Y-%H%M%S")+".txt"

    def log(self, log):
        if self.logged:
            now = datetime.now().time()
            with open(self.filename_log,"a+") as f_log:
                f_log.write("%s-%s-%s\n" % ("BS_busy_tresh", now, log)) 


    def power(self):
        if self.sample_buffer.size != 0:
            self.log("power : %s \n" % (self.sample_buffer.size))
            samples_power = np.power(np.power(np.real(self.sample_buffer), 2) + np.power(np.imag(self.sample_buffer), 2), 0.5)
            self.power_per_slot = np.append(self.power_per_slot, 10*np.log10(np.mean(samples_power)))
        else:
            self.log("power : no sample \n")
            self.power_per_slot = np.append(self.power_per_slot, 0.0)
        self.sample_buffer = np.array([])

    def feedback(self):
        feedback = []
        for slot_power in self.power_per_slot:
            if slot_power > self.power_tresh:
                feedback.append("BUSY")
            else:
                feedback.append("IDLE")

        self.message_port_pub(pmt.to_pmt("feedback"), pmt.to_pmt(feedback))
        self.power_per_slot = np.array([])


    def work(self, input_items, output_items):
        in0 = input_items[0]
        tags = self.get_tags_in_window(0, 0, len(in0))

        self.log("Work function - tag count : %s - len input : %s, nitems_read : %s\n" % (len(tags), len(in0), self.nitems_read(0)))

        start = None
        stop = None
        frame = None
        stop_compute = False
        send_feedback = False
        

        # Get tags
        for tag in tags:
            key = pmt.to_python(tag.key) 
            value = pmt.to_python(tag.value) 
            if key == 'PUSCH':
                #start = self.nitems_read(0) - tag.offset
                start = tag.offset - self.nitems_read(0)
                self.compute = True
                self.log("PUSCH")

            elif key == 'GUARD':
                #stop = self.nitems_read(0) - tag.offset
                stop = tag.offset - self.nitems_read(0)
                stop_compute = True
                self.log("GUARD")

            elif key == 'FRAME':
                send_feedback = True
                frame = value
                self.log("FRAME")
            
            else:
                self.log("Unknown tag : %s - %s" % (key, value))

        # Define gate for wanted "pusch" samples
        if start == None and self.compute == True:
            start = 0
        if stop == None and self.compute == True:
            stop = len(in0)

        self.log("Start - stop : %s-%s\n" % (start,stop))

        # Get wanted samples
        if start is not None and stop is not None:
            self.sample_buffer = np.append(self.sample_buffer, in0[start:stop])
            self.log("Save %s PUSH samples\n" % (len(in0[start:stop])))

        # Compute dB power for one slot
        if stop_compute:
            self.compute = False
            self.power()
            self.log("Frame power : %s\n" % (self.power_per_slot))

        # Compute IDLE/BUSY slot and send feedback to MSG MUX
        if send_feedback:
            print("BS - Power tresh : Frame %s | Power %s" % (frame, self.power_per_slot))
            self.feedback()
            self.log("End Frame : Send feedback to msg mux\n")

        self.consume(0, len(in0))

        return 0

