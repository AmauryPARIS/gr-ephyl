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
from gnuradio import gr, uhd
import time
import datetime
import threading
import pmt
from datetime import datetime
import json

IDLE = 0
BCH = 1
# SYNC = 2
PUSCH = 2
GUARD = 3
PROC = 4

STATES = ["IDLE", "BCH", "PUSCH", "GUARD", "PROC"]

class bs_scheduler(gr.sync_block):
    """EPHYL Demo : Base Station 
    - All durations are expressed in millisecond
    """
    def __init__(self, num_slots=5,bch_time=20,
        guard_time=100, Slot_time=50, Proc_time = 50,
        sample_rate=200000, UHD = True,exit_frame=0, list_sensor = "AB", log=False):
        gr.sync_block.__init__(self,
            name="BS Scheduler",
            in_sig=[np.complex64],
            out_sig=[np.complex64])

        self.message_port_register_out(pmt.intern("bcn"))
        self.message_port_register_out(pmt.intern("DLCCH"))

        self.message_port_register_in(pmt.intern("inst"))
        self.set_msg_handler(pmt.intern("inst"), self.handle_inst) 

        ##################################################
        # Parameters
        ##################################################
        self.num_slots = num_slots
        self.samp_rate = int(sample_rate/1000)
        self.UHD = UHD
        self.exit_frame = exit_frame
        self.logged = log

        ##################################################
        # Variables
        ##################################################
        self.state = BCH
        self.list_sensor = list_sensor
        self.filename_log = "LOG_BS_sched_"+time.strftime("%d%m%Y-%H%M%S")+".txt"
        self.filename_log_state = "STATE_BS.txt"
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
        self.list_dlcch = []
        self.topblock = None

        self.diff = self.left = 0
        self.inst_request_send = False
        self.dlcch_send = False
         

        ## Here we set states data, 
        ## PS : SYNC has a constant offset of +guard_time to compensate the LISTEN state of the sensor nodes
        ## Have a look at the same variable in the sensor scheduler block
        self.STATES = [range(5) \
            ,['IDLE','BCH','PUSCH','GUARD','PROC'] \
            ,[0,bch_time,Slot_time,guard_time,Proc_time]]

        self.lock = threading.Lock()  

    def to_time(self,n_samp) :
        return n_samp/float(self.samp_rate)

    def log(self, log):
        if self.logged:
            now = datetime.now().time()
            with open(self.filename_log,"a+") as f_log:
                f_log.write("%s-%s-%s-%s\n" % ("BS", self.frame_cnt, now, log)) 

    def log_state(self, offset):
        if self.logged:
            now = datetime.now().time()
            with open(self.filename_log_state,"a+") as f_log:
                f_log.write("%s-%s-%s-%s-%s\n" % ("BS", self.frame_cnt, now, STATES[self.state], offset)) 

    def to_samples(self,duration) :
        return int(duration*self.samp_rate)

    def next_state(self) :
        # state = self.STATES[0][int((state+1)%len(self.STATES[0]))]
        if self.state < len(self.STATES[0])-1 :
            self.state += 1
        else :
            self.state = 0

    def set_top_block(self, topblock):
        if self.topblock == None:
            self.topblock = topblock


    def handle_inst(self, msg_pmt):
        with self.lock :
            msg_pmt = pmt.deserialize_str(pmt.to_python(msg_pmt))
            frame = int(pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("FRAME"), pmt.PMT_NIL)))
            for dlcch_inst in pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("DLCCH"), pmt.PMT_NIL)) :
                
                dlcch_inst_norm = {"sensor" : dlcch_inst[0], "frame" : frame, "content" : dlcch_inst[1], "send" : False}
                # if frame == self.frame_cnt:
                #     self.message_port_pub(pmt.to_pmt("DLCCH"), self.create_cch_msg(dlcch_inst_norm["sensor"], dlcch_inst_norm["content"]))
                #     dlcch_inst_norm["send"] = True
                self.list_dlcch.append(dlcch_inst_norm)
                self.log("Received new DLCCH instruction : %s" % (self.list_dlcch))


    def create_cch_msg(self, sn_id, payload):
        self.log("Send DLCCH on error free channel : %s | %s | %s | %s" % ("BS", sn_id, self.frame_cnt, payload))
        msg = pmt.make_dict()
        msg = pmt.dict_add(msg, pmt.to_pmt("SRC"), pmt.to_pmt("BS"))
        msg = pmt.dict_add(msg, pmt.to_pmt("DST"), pmt.to_pmt(sn_id))
        msg = pmt.dict_add(msg, pmt.to_pmt("FRM"), pmt.to_pmt(self.frame_cnt))
        msg = pmt.dict_add(msg, pmt.to_pmt("CCH"), pmt.to_pmt(payload))
        return msg

    def end_frame_beacon(self):
        msg = 'end_frame' + '\t' + str(self.frame_cnt-1)
        d = [ord(e) for e in msg]
        trig_msg = pmt.cons(pmt.make_dict(), pmt.init_u8vector(len(d),d))
        self.message_port_pub(pmt.to_pmt("bcn"), trig_msg)
        self.log("Send end message beacon")

    def run_state(self,Input,output1) :
        self.log("State %s - nread_items %s" % (STATES[self.state], self.nitems_read(0)))   
        
        if self.frame_cnt == 0 and not self.inst_request_send:
            for sn in self.list_sensor:
                self.message_port_pub(pmt.to_pmt("DLCCH"), self.create_cch_msg(sn, "START"))
            self.inst_request_send = True

        state_samp = self.to_samples(self.STATES[2][self.state])
        self.diff = state_samp-self.samp_cnt


        ###############################################################################
        ## If the cuurent state cannot run completely, 
        ## i.e the sample count exceeds the number of samples required for the current state      
        if self.diff < 0 :
            self.samp_cnt = 0
            if self.state == PUSCH:
                output1[:] = Input[:]
            else:
                output1[:] = [0.01]*len(output1)
            output1 = np.delete(output1,slice(len(output1)+self.diff,len(output1)))    # Since diff is negative

            if self.state == BCH :
                output1[:] = [0.01]*len(output1)
                self.slot_cnt += 1

            elif self.state == PUSCH : 
                output1[:] = Input[:len(output1)]
                for elem in range(0,len(self.list_dlcch)):
                    if self.list_dlcch[elem]["send"] == False and self.list_dlcch[elem]["frame"] == self.frame_cnt:
                        self.message_port_pub(pmt.to_pmt("DLCCH"), self.create_cch_msg(self.list_dlcch[elem]["sensor"], self.list_dlcch[elem]["content"]))
                        self.list_dlcch[elem]["send"] = True

            elif self.state == GUARD :
                output1[:] = [0.01]*len(output1)
                self.slot_cnt += 1
                if self.slot_cnt < self.num_slots :
                    # Return to PUSCH
                    self.state -= 2
                else :
                    self.slot_cnt = -1

            elif self.state == PROC : 
                output1[:] = [0.01]*len(output1)
                if self.exit_frame == 0 or self.frame_cnt <= self.exit_frame:
                    self.next_state()   # In order to jump the idle state
                else :
                    return -1

            elif self.state not in self.STATES[0] :
                print("STATE ERROR")
                exit(1)

            else :
                output1[:] = [0.01]*len(output1)

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
            self.log_state(offset)

            if self.state == PROC :
                print "[BS] ================= FRAME " + str(self.frame_cnt-1) + " PROCESSING ================="
                self.end_frame_beacon()
            elif self.state == BCH and self.UHD:
                self.time_BCH = self.topblock.uhd_usrp_source_0_0.get_time_now()       
                

        ###############################################################################
        ## If the cuurent state can still run completely one more time
        else :
            self.samp_cnt -= len(output1)

            if self.state == PUSCH :
                output1[:] = Input[:]
                for elem in range(0,len(self.list_dlcch)):
                    if self.list_dlcch[elem]["send"] == False and self.list_dlcch[elem]["frame"] == self.frame_cnt:
                        self.message_port_pub(pmt.to_pmt("DLCCH"), self.create_cch_msg(self.list_dlcch[elem]["sensor"], self.list_dlcch[elem]["content"]))
                        self.list_dlcch[elem]["send"] = True

            elif self.state == BCH :
                if not(self.bcn_sent):
                    offset = 0
                    if self.UHD :
                        # offset = self.nitems_read(0)-60000*self.num_slots # Legacy
                        if self.frame_cnt == 0:
                            self.time_BCH = self.topblock.uhd_usrp_source_0_0.get_time_now()

                        length_bch_ms = self.STATES[2][BCH]
                        time_tx = self.time_BCH + uhd.time_spec(0,float(length_bch_ms)/1000) # [full_scd, frac_scd]
                        offset = [time_tx.get_full_secs(), time_tx.get_frac_secs()]
                        self.log("ON AIR - offset : %s - now %s,%s" % (offset, self.time_BCH.get_full_secs(), self.time_BCH.get_frac_secs()))
                                             
                    else:
                        offset = self.nitems_read(0)+1000
                        #offset = self.nitems_read(0)+20000


                    '''
                    We have to deconstruct the offset before appending it,
                    because it can get big and we have to send it in a u8vector form (<255)
                    To recover the offset value in the sensor scheduler, 
                    we will simply convert what's after the 8 first elements
                    '''
                    
                    msg = 'corr_est' + '\t' + str(self.frame_cnt) + '\t' + json.dumps(offset) 
                    d = [ord(e) for e in msg]

                    trig_msg = pmt.cons(pmt.make_dict(), pmt.init_u8vector(len(d),d))

                    self.message_port_pub(pmt.to_pmt("bcn"), trig_msg)
                    self.log("Send BCH beacon - msg : %s" % (str(msg)))
                    self.bcn_sent = True

                    if self.frame_cnt != 0:
                        print("\n")
                        print "[BS] ================= FRAME " + str(self.frame_cnt) + " START ================="
                    elif self.frame_cnt == 0 and self.UHD:
                        self.topblock.uhd_usrp_source_0_0.set_time_next_pps(uhd.time_spec(0, 0))

                    output1[:] = [0.01]*len(output1)
                else : 
                    output1[:] = [0.01]*len(output1)

            else :
                output1[:] = [0.01]*len(output1)

            self.samp_cnt += len(output1)
        ###############################################################################

        # if self.state != BCH :
        #     self.log("Weird transmit data at %s" % (str(STATES[self.state])))
        #     output1[:] = Input[:len(output1)]

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