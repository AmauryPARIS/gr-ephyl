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
import threading
from gnuradio import gr, gr_unittest, blocks
import string
import re

SLOT_READ=0
IDLE=1
PKT_GEN=2
LISTEN=3
BCH=4
EMIT=5
GUARD =6
PROC = 7


class sn_scheduler(gr.basic_block):
    """
    EPHYL Sensor Scheduler
    """
    def __init__(self, phy_option=0,
        num_slots=5, bch_time=20, guard_time=100, Slot_time=50, Proc_time = 50, 
        wanted_tag="corr_start",length_tag_key="packet_len2",samp_rate = 32000):
        gr.basic_block.__init__(self,
            name="Sensor Scheduler",
            in_sig=[],
            out_sig=[np.complex64])

        self.key = None
        self.Id = random.choice(string.ascii_letters) 
        self.phy_option = phy_option
        self.num_slots = num_slots
        self.length_tag_key = length_tag_key
        self.samp_rate = int(samp_rate/1000)

        ## Here we set states data, 
        ## PS : LISTEN has a constant pseudo infinite duration to avoid timing/buffer overflow
        ## Processing time (PROC state) for sensor only serves to reset variables, that's why it lasts Proc_time/2 
        self.STATES = [range(8) \
            ,['SLOT_READ','IDLE','PKT_GEN','LISTEN','BCH','EMIT','GUARD','PROC'] \
            ,[0,0,0,float("inf"),bch_time,Slot_time,guard_time,Proc_time/2]]

        self.wanted_tag = wanted_tag
        self.message_port_register_in(pmt.intern("in"))
        self.message_port_register_in(pmt.intern("trig"))
        self.set_msg_handler(pmt.intern("in"), self.handle_msg)
        self.set_msg_handler(pmt.intern("trig"), self.handle_trig)

        self.message_port_register_in(pmt.intern("slot"))
        self.set_msg_handler(pmt.intern("slot"), self.handle_slot)
        
        self.message_port_register_out(pmt.intern("busy"))

        self.samp_cnt = 0
        self.delay = self.delay_t = 0

        self.pdu_cnt = 0
        self.slot_cnt = 0
        
        self.test = 0
        self.msg_out = np.array([])
        self.msg_full = np.array([])

        self.state = SLOT_READ
        self.state_dbg = self.state_tag = -1
        self.trig = ''

        self.active = -1

        self.signal_len = 0
        self.busy = False

        self.slot_msg = np.array([])

        self.slots = []

        self.i = 0

        self.lock = threading.Lock()
        self.frame_cnt = 0
        self.frame_len = self.to_samples(self.STATES[2][BCH]+self.STATES[2][PROC]+self.num_slots*(self.STATES[2][EMIT]+self.STATES[2][GUARD]))

    def to_time(self,n_samp) :
        return n_samp/float(self.samp_rate)

    def to_samples(self,duration) :
        if duration == float("inf") :
            return float(duration*self.samp_rate)
        else :
            return int(duration*self.samp_rate)

    def next_state(self) :
        if self.state < len(self.STATES[0])-1 :
            self.state += 1
        else :
            self.state = 0

    def handle_slot(self, slot_pmt):
        with self.lock : 
            if self.state == SLOT_READ :
                if pmt.to_python(slot_pmt) == "STOP" :
                    self.state = IDLE
                    self.slot_cnt = 0
                    print "[SN "+self.Id+"] SENSOR SLOTS ARE :" + str(self.slots)
                    self.message_port_pub(pmt.to_pmt("busy"), pmt.to_pmt('RESET'))
                elif pmt.to_python(slot_pmt) == "ACTIVE" :
                    self.active = True
                elif pmt.to_python(slot_pmt) == "INACTIVE" :
                    self.active = False
                    self.state = PROC
                else :
                    new_array = pmt.to_python(slot_pmt)
                    # Extract ID coming from slot control block, and remove it from the message
                    self.Id = new_array[2]

                    # Extract Slot
                    tmp_slot = new_array[1]

                    if tmp_slot.isdigit() :  # FOR DEBUG
                        self.slots.append(int(tmp_slot))     # First character is the slot number to be used
                    else :
                        self.slots.append(int(np.random.choice(range(self.num_slots), 1)))
                    
                    if self.slot_cnt != self.slots[-1] :
                        self.slot_msg = np.append(self.slot_msg,['']*(self.slots[-1]-self.slot_cnt))  # Fill unused slots with empty string
                        self.slot_cnt = self.slots[-1]

                    self.slot_msg = ['\t'.join(new_array[2:])]
                    self.slot_cnt += 1

    def handle_msg(self, msg_pmt):
        with self.lock : 
            if self.state == PKT_GEN :
      
                if self.phy_option==0 :     # SC-FDMA PHY option
                    self.signal_len = 2*len(self.slot_msg[0])+12
                    # self.signal_len = 2*len(self.slot_msg[self.slot_cnt])+12
                elif self.phy_option==1 :   # TurboFSK PHY option
                    # /*  OUT = (64*32)+(1+(IN+16)/8)*4*137+(1+int((1+(IN+16)/8)*4/5))*137 */
                    self.signal_len = 4  # TO BE UPDATED

                self.msg_out = np.append(self.msg_out,pmt.to_python(pmt.cdr(msg_pmt)))   # Collect message data, convert to Python format:
                self.pdu_cnt += 1
                if self.pdu_cnt == self.signal_len:   # Signal reconstructed 
                    self.pdu_cnt=0
                    self.msg_full = np.array(self.msg_full.tolist() + [self.msg_out.tolist()])    # Store the N signals in N-dim array, analyze carefully before modifying
                    self.msg_out = np.array([])
                    self.state = IDLE    # Return to IDLE and check for remaining messages
                    self.slot_cnt +=1

    def handle_trig(self, trig_pmt):
        with self.lock : 
            if self.state == LISTEN :
                self.delay = 0
                d = pmt.to_python(pmt.cdr(trig_pmt))    # Collect trig message data, convert to Python format
                l = [chr(e) for e in d]
                l = ''.join(l)
                l = re.split(r'\t+', l)     # l now contains wanted_tag, frame number, and offset
                try :
                    self.frame_cnt = int(l[1])
                    if l[0] == self.wanted_tag:
                        self.state = BCH
                        self.slot_cnt = 0
                        self.msg_out = self.msg_full[self.slot_cnt]     # Init first msg to be sent

                        try:
                            offset = int(l[2])
                        except:
                            print "Offset non valid"
                            offset = 0

                        self.delay = self.nitems_written(0)-offset
                        if self.delay>0:
                            self.samp_cnt = self.delay
                        else:
                            self.samp_cnt= 200000 
                        return 0
                except:
                    pass

    def run_state(self,output) :

        self.samp_cnt += len(output)    # Sample count related to current state
        state_samp = self.to_samples(self.STATES[2][self.state])      
        diff = state_samp - self.samp_cnt       # Act as a timer

        if self.state in (EMIT,GUARD,BCH,PROC):
            self.i += len(output)
        ###############################################################################    
        ## If the cuurent state cannot run completely, 
        ## i.e the sample count exceeds the number of samples required for the current state
        if diff < 0 :  

            if self.state in (EMIT,GUARD,BCH,PROC):
                self.i -= len(output)

            output = np.delete(output,slice(len(output)+diff,len(output)))    # Since diff is negative we use +diff
            
            if self.state in (EMIT,GUARD,BCH,PROC):
                self.i += len(output)

            if self.state == EMIT : 
                if self.slot_cnt in self.slots :
                    if len(output) > len(self.msg_out) :    # In case output buffer is bigger than payload
                        output[:] = np.append(self.msg_out[:len(output)] , [0]*(abs(len(output)-len(self.msg_out))))  # Fill what's left with Sensor Data (if left)
                    else :
                        output[:] = self.msg_out[:len(output)]
                else :
                    output[:] = [0]*len(output)
                self.state = GUARD

            else :    
                if self.state == IDLE :
                    self.msg_out = np.array([])
                    if self.slot_cnt < self.num_slots :
                        if range(self.num_slots)[self.slot_cnt] in self.slots :   # If slot will be used, generate a packet
                            self.message_port_pub(pmt.to_pmt("busy"), pmt.to_pmt('DATA'))    # Request File source to send msg
                            self.state = PKT_GEN
                        else :      # If slot won't be used, append empty signal
                            self.msg_full = np.array(self.msg_full.tolist() + [[]])    # Store Null signal
                            self.slot_cnt += 1
                    else :
                        self.message_port_pub(pmt.to_pmt("busy"), pmt.to_pmt('RESET'))     # Reset reading in 'File source' block
                        self.state = LISTEN         # if all BS slots covered, Jump to LISTEN

                elif self.state == SLOT_READ :
                    if self.active == -1:
                        self.message_port_pub(pmt.to_pmt("busy"), pmt.to_pmt('ACTIVE?'))
                        # self.active = False
                        self.slot_cnt = 0
                    elif self.active == True:
                        self.message_port_pub(pmt.to_pmt("busy"), pmt.to_pmt('ARRAY'))
                    elif self.active == False:
                        self.message_port_pub(pmt.to_pmt("busy"), pmt.to_pmt('RESET_FRAME'))


                elif self.state == LISTEN :
                    output[:] = [0]*len(output)

                elif self.state == BCH :
                    self.slot_cnt = 0
                    self.state = EMIT
                    output[:] = [0]*len(output)
                
                elif self.state == GUARD :
                    self.slot_cnt += 1
                    if self.slot_cnt < self.num_slots :
                        if self.slot_cnt in self.slots :
                            self.msg_out = self.msg_full[self.slot_cnt]     # Update signal slot index
                        else :
                            self.msg_out = []
                        self.state = EMIT
                    else :
                        self.slot_cnt = 0
                        self.message_port_pub(pmt.to_pmt("busy"), pmt.to_pmt('RESET_FRAME')) # Just before the start of PROC
                        self.state = PROC

                elif self.state == PROC :
                    # End of frame --> Reset some variables
                    self.state = SLOT_READ
                    self.msg_full = np.array([])
                    self.msg_out = np.array([])
                    self.slot_msg = np.array([])
                    self.slot_cnt = 0
                    self.slots = []   
                    self.delay_t = 0
                    self.active = -1
                    self.i=0

                elif self.state not in self.STATES[0] :
                    print("STATE ERROR")
                    exit(1)
                
                output[:] = [0]*len(output)

            self.samp_cnt = 0

        ###############################################################################
        # If current state can run one more time
        else :      
            self.samp_cnt -= len(output)
            if self.state==EMIT :
                if self.slot_cnt in self.slots :
                    if len(self.msg_out) == 0 :
                        output[:] = [0]*len(output)
                    else :    
                        max_output = min(len(output), len(self.msg_out))
                        output = output[:max_output]
                        output[:] = self.msg_out[:max_output]
                        self.msg_out = self.msg_out[max_output:]
                else :
                    output[:] = [0]*len(output)

            else :
                output[:] = [0]*len(output)

            self.samp_cnt += len(output)
        ###############################################################################

        # Add tags for each state
        if self.state_tag != self.state :            
            self.state_tag = self.state
            offset = self.nitems_written(0)+len(output)
            key = pmt.intern(self.STATES[1][self.state])
            value = pmt.to_pmt(self.slot_cnt)
            self.add_item_tag(0,offset, key, value)

        return len(output)

    def general_work(self,input_items,output_items):
        with self.lock :

            # if self.state_dbg != self.state :
            #     self.state_dbg = self.state
            #     print "[SN "+self.Id+"] STATE " + self.STATES[1][self.state] + " START"

            retval = self.run_state(output_items[0])
            return retval
