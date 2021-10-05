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
from gnuradio import gr
import time
import datetime
import threading
import pmt

IDLE = 0
BCH = 1
# SYNC = 2
PUSCH = 2
GUARD = 3
PROC = 4


class bs_scheduler(gr.sync_block):
    """EPHYL Demo : Base Station 
    - All durations are expressed in millisecond
    """
    def __init__(self, num_slots=5,bch_time=20,
        guard_time=100, Slot_time=50, Proc_time = 50,
        sample_rate=200000, UHD = True,exit_frame=0):
        gr.sync_block.__init__(self,
            name="BS Scheduler",
            in_sig=[np.complex64],
            out_sig=[np.complex64])


        self.message_port_register_out(pmt.intern("bcn"))
        ##################################################
        # Parameters
        ##################################################
        self.num_slots = num_slots
        self.samp_rate = int(sample_rate/1000)
        self.UHD = UHD
        self.exit_frame = exit_frame

        ##################################################
        # Variables
        ##################################################
        self.state = BCH
        # self.state = IDLE  # DEBUG (no uhd)
        # self.state = -1
        self.state_dbg = -1
        self.slot_cnt_dbg = -1
        self.slot_cnt = -1
        self.rx_time = 0
        self.timer = 0
        self.samp_cnt = 0
        self.to_return1 = 0
        self.bcn_sent = False
        self.frame_cnt = 0
        self.bch_time = bch_time

        self.diff = self.left = 0

        ## Here we set states data, 
        ## PS : SYNC has a constant offset of +guard_time to compensate the LISTEN state of the sensor nodes
        ## Have a look at the same variable in the sensor scheduler block
        self.STATES = [range(5) \
            ,['IDLE','BCH','PUSCH','GUARD','PROC'] \
            ,[0,bch_time,Slot_time,guard_time,Proc_time]]

        self.lock = threading.Lock()  

    def to_time(self,n_samp) :
        return n_samp/float(self.samp_rate)

    def to_samples(self,duration) :
        return int(duration*self.samp_rate)

    def next_state(self) :
        # state = self.STATES[0][int((state+1)%len(self.STATES[0]))]
        if self.state < len(self.STATES[0])-1 :
            self.state += 1
        else :
            self.state = 0

    def run_state(self,Input,output1) :

        state_samp = self.to_samples(self.STATES[2][self.state])
        self.diff = state_samp-self.samp_cnt

        ###############################################################################
        ## If the cuurent state cannot run completely, 
        ## i.e the sample count exceeds the number of samples required for the current state      
        if self.diff < 0 :
            self.samp_cnt = 0
            output1 = np.delete(output1,slice(len(output1)+self.diff,len(output1)))    # Since diff is negative

            if self.state == BCH :
                self.slot_cnt += 1

            elif self.state == PUSCH : 
                output1[:] = Input[:len(output1)]
            
            elif self.state == GUARD :
                self.slot_cnt += 1
                if self.slot_cnt < self.num_slots :
                    # Return to PUSCH
                    self.state -= 2
                else :
                    self.slot_cnt = -1

            elif self.state == PROC : 
                if self.exit_frame == 0 or self.frame_cnt <= self.exit_frame:
                    self.next_state()   # In order to jump the idle state
                else :
                    return -1

            elif self.state not in self.STATES[0] :
                print("STATE ERROR")
                exit(1)
            
            else :
                output1[:] = [0]*len(output1)

            self.next_state()
            
            # Add tags for each state
            offset = self.nitems_written(0)+len(output1)
            if self.state == PROC :
                key = pmt.intern("FRAME")
                value = pmt.to_pmt(self.frame_cnt)
                self.frame_cnt += 1
                self.bcn_sent = False
            else :
                key = pmt.intern(self.STATES[1][self.state])
                value = pmt.to_pmt(self.slot_cnt)
            self.add_item_tag(0,offset, key, value)
            if self.state == PROC :
                print "[BS] ================= FRAME " + str(self.frame_cnt-1) + " FINISH ================="

        ###############################################################################
        ## If the cuurent state can still run completely one more time
        else :
            self.samp_cnt -= len(output1)

            if self.state == PUSCH :
                output1[:] = Input[:]

            elif self.state == BCH :
                if not(self.bcn_sent) :
                    offset = 0
                    if self.UHD :
                        # offset = self.nitems_read(0)
                        # if self.num_slots < 4:
                        offset = self.nitems_read(0)-60000*self.num_slots
                    #     elif self.num_slots >= 4 and self.num_slots < 8:
                    #         offset = self.nitems_read(0)-5000*self.num_slots
                    #     elif self.num_slots >= 8 and self.num_slots < 16:
                    #         offset = self.nitems_read(0)-2000*self.num_slots
                    #     elif self.num_slots >= 16:
                    #         offset = self.nitems_read(0)-500*self.num_slots                            
                    else:
                        offset = self.nitems_read(0)+1000

                    '''
                    We have to deconstruct the offset before appending it,
                    because it can get big and we have to send it in a u8vector form (<255)
                    To recover the offset value in the sensor scheduler, 
                    we will simply convert what's after the 8 first elements
                    '''
                    msg = 'corr_est' + '\t' + str(self.frame_cnt) + '\t' + str(offset)
                    d = [ord(e) for e in msg]

                    trig_msg = pmt.cons(pmt.make_dict(), pmt.init_u8vector(len(d),d))
                    self.message_port_pub(pmt.to_pmt("bcn"), trig_msg)
                    self.bcn_sent = True

                    output1[:] = [0]*len(output1)
                else : 
                    output1[:] = [0]*len(output1)

            else :
                output1[:] = [0]*len(output1)

            self.samp_cnt += len(output1)
        ###############################################################################

        if self.state != BCH :
            output1[:] = Input[:len(output1)]

        self.to_return1 = len(output1)

    def work(self, input_items, output_items):
        with self.lock :
            self.samp_cnt += len(output_items[0])
            # if self.state_dbg != self.state :
            #     self.state_dbg = self.state
            #     print "[BS] STATE " + self.STATES[1][self.state] + " START : " + str(self.to_time(self.to_return1))
            #     print "[BS] STATE " + self.STATES[1][self.state] + " START : " + str(self.to_time(self.samp_cnt_abs))
                
                # if (self.state == PUSCH) :
                #     print "[BS] STATE PUSCH @ SLOT : " + str(self.slot_cnt)
                # self.samp_cnt = 0

            self.run_state(input_items[0],output_items[0])

            return self.to_return1

