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
from gnuradio import gr, gr_unittest, blocks, uhd
import string
import re
from datetime import datetime
import json

SLOT_READ=0
IDLE=1
PKT_GEN=2
LISTEN=3
BCH=4
EMIT=5
GUARD =6
PROC = 7

STATES = ["SLOT_READ", "IDLE", "PKT_GEN", "LISTEN", "BCH", "EMIT", "GUARD", "PROC"]

class sn_scheduler(gr.basic_block):
    """
    EPHYL Sensor Scheduler
    """
    def __init__(self, phy_option=0, uhd=True, clock_master=True,
        num_slots=5, bch_time=20, guard_time=100, Slot_time=50, Proc_time = 50, 
        wanted_tag="corr_start",length_tag_key="packet_len2",samp_rate = 32000, ID = "Z", log=False, sf=7, cr=4, crc=True):
        gr.basic_block.__init__(self,
            name="Sensor Scheduler",
            in_sig=[],
            out_sig=[np.complex64])

        self.key = None
        self.Id = ID
        self.phy_option = phy_option
        self.num_slots = num_slots
        self.length_tag_key = length_tag_key
        self.samp_rate = int(samp_rate/1000)
        self.logged = log
        self.uhd = uhd
        self.clock_master = clock_master

        self.lora_sf = sf
        self.lora_cr = cr
        self.lora_crc = crc

        ## Here we set states data, 
        ## PS : LISTEN has a constant pseudo infinite duration to avoid timing/buffer overflow
        ## Processing time (PROC state) for sensor only serves to reset variables, that's why it lasts Proc_time/2 
        self.STATES = [range(8) \
            ,['SLOT_READ','IDLE','PKT_GEN','LISTEN','BCH','EMIT','GUARD','PROC'] \
            ,[0,0,0,float("inf"),bch_time,Slot_time,guard_time,Proc_time/2]]

        self.wanted_tag = wanted_tag

        self.message_port_register_in(pmt.intern("in"))
        self.set_msg_handler(pmt.intern("in"), self.handle_msg)

        self.message_port_register_in(pmt.intern("trig"))
        self.set_msg_handler(pmt.intern("trig"), self.handle_trig)

        self.message_port_register_in(pmt.intern("slot"))
        self.set_msg_handler(pmt.intern("slot"), self.handle_slot)

        self.message_port_register_in(pmt.intern("inst"))
        self.set_msg_handler(pmt.intern("inst"), self.handle_inst) 
        
        self.message_port_register_in(pmt.intern("DLCCH"))
        self.set_msg_handler(pmt.intern("DLCCH"), self.handle_dlcch) 

        self.message_port_register_out(pmt.intern("feedback"))
        
        self.message_port_register_out(pmt.intern("busy"))

        self.message_port_register_out(pmt.intern("ULCCH"))
        
        self.ulcch = []
        self.dlcch = None

        self.samp_cnt = 0
        self.delay = self.delay_t = 0

        self.pdu_cnt = 0
        self.slot_cnt = 0
        self.time_tx_scd = 0
        self.time_tx_frac = 0
        
        self.msg_out = np.array([])
        self.msg_full = np.array([])

        self.state = SLOT_READ
        self.state_tag = -1
        self.trig = ''

        self.active = -1

        self.signal_len = 0
        self.busy = False

        self.slot_msg = np.array([])

        self.slots = []
        self.topblock = None

        self.inst_request_send = False

        self.lock = threading.Lock()
        self.frame_cnt = 0
        self.frame_len = self.to_samples(self.STATES[2][BCH]+self.STATES[2][PROC]+self.num_slots*(self.STATES[2][EMIT]+self.STATES[2][GUARD]))

        self.filename_log = "LOG_SN_"+self.Id+"_sched_"+time.strftime("%d%m%Y-%H%M%S")+".txt"

        

    def log(self, log):
        if self.logged:
            now = datetime.now().time()
            with open(self.filename_log,"a+") as f_log:
                f_log.write("%s-%s-%s-%s\n" % (self.Id, self.frame_cnt, now, log)) 

    def to_time(self,n_samp) :
        return n_samp/float(self.samp_rate)

    def to_samples(self,duration) :
        if duration == float("inf") :
            return float(duration*self.samp_rate)
        else :
            return int(duration*self.samp_rate)

    def set_top_block(self, topblock):
        if self.topblock == None:
            self.topblock = topblock

    def handle_slot(self, slot_pmt):
        with self.lock : 
            if self.state == SLOT_READ :
                if pmt.to_python(slot_pmt) == "STOP" :
                    self.state = IDLE
                    self.slot_cnt = 0
                    #print "[SN "+self.Id+"] TX SENSOR SLOTS ARE :" + str(self.slots)
                    self.log("STOP : SENSOR SLOTS ARE :" + str(self.slots))
                    self.message_port_pub(pmt.to_pmt("busy"), pmt.to_pmt('RESET'))

                elif pmt.to_python(slot_pmt) == "ACTIVE" :
                    self.active = True
                    self.log("Active Frame")

                elif pmt.to_python(slot_pmt) == "INACTIVE" :
                    found = False
                    for elem in range(0,len(self.ulcch)): 
                        if int(self.frame_cnt) == int(self.ulcch[elem]["frame"]) and self.ulcch[elem]["packet"] == 'True':
                            self.active = True
                            self.log("Instruction Active Frame")
                            found = True
                    if not found:
                        self.active = False
                        self.state = PROC   
                        self.log("Inactive Frame")
                        self.init_timer()
     
                else :
                    new_array = pmt.to_python(slot_pmt)
                    self.log("Slot control - new_array : %s" % (new_array))
                    # Extract ID coming from slot control block, and remove it from the message
                    #self.Id = new_array[2]

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
                elif self.phy_option==2: # LoRa PHY Option
                    len_msg = len(self.slot_msg[0]) # data to be transmited [bytes]
                    len_crc = 4 if self.lora_crc else 0
                    len_msg = (len_msg * 2) + 5 + len_crc # whitening + header + crc [bytes]
                    len_msg = 8 + (int((len_msg - (self.lora_sf-2))/self.lora_sf)+1) * (4+self.lora_cr) # Interleaver
                    len_msg = (len_msg + 12)*4 + 1  # modulate and preamble - each symbol worth 2**sf samples, except from one symbol in the preamble
                                                    # This symbol is worth 2**sf / 4 samples 
                                                    # The signal is therfore received as pdu of 2**sf / 4 samples
                    self.signal_len = len_msg

                self.msg_out = np.append(self.msg_out,pmt.to_python(pmt.cdr(msg_pmt)))   # Collect message data, convert to Python format:
                self.pdu_cnt += 1
                self.log("Store msg - size : %s - count : %s - slot msg : %s" % (self.signal_len, self.pdu_cnt, self.slot_msg))

                if self.pdu_cnt == self.signal_len:   # Signal reconstructed 

                    self.log("Store msg - signal reconstructed len %s - theorical len %s - sample exemple %s" % (len(self.msg_out), (self.pdu_cnt * (2**self.lora_sf) / 4), self.msg_out[-10]))
                    if len(self.msg_out) > self.to_samples(self.STATES[2][EMIT]):
                        self.log("Store msg - ERROR : signal len is higher than slot len")
                        print("ERROR : signal len is higher than slot len")
                    self.pdu_cnt=0
                    self.msg_full = np.array(self.msg_full.tolist() + [self.msg_out.tolist()])    # Store the N signals in N-dim array, analyze carefully before modifying
                    self.msg_out = np.array([])
                    self.state = IDLE    # Return to IDLE and check for remaining messages
                    self.slot_cnt +=1


    def handle_trig(self, trig_pmt):
        with self.lock : 
            d = pmt.to_python(pmt.cdr(trig_pmt))    # Collect trig message data, convert to Python format
            l = [chr(e) for e in d]
            l = ''.join(l)
            l = re.split(r'\t+', l)     # l now contains wanted_tag, frame number, and offset
            self.log("TRIG received : %s | status listen ? %s | status %s " % (l, self.state == LISTEN, self.state))

            if l[0] == "end_frame":
                self.message_port_pub(pmt.to_pmt("feedback"), self.create_inst_msg(self.dlcch)) 

            elif l[0] == "corr_est":
                self.frame_cnt = int(l[1])

                if self.uhd and self.frame_cnt == 0 and self.clock_master:
                    self.topblock.uhd_usrp_sink_0_0.set_time_next_pps(uhd.time_spec(0, 0))

                # transmit ULCCH
                pop_instr = None
                for elem in range(0,len(self.ulcch)): 
                    if self.frame_cnt == self.ulcch[elem]["frame"] and self.ulcch[elem]["send"] == False:
                        self.message_port_pub(pmt.to_pmt("ULCCH"), self.create_cch_msg(self.ulcch[elem]["content"]))
                        self.ulcch[elem]["send"] = True
                    elif self.ulcch[elem]["frame"] < self.frame_cnt:
                        pop_instr = elem
                if pop_instr is not None:
                    self.ulcch.pop(pop_instr)

                try:
                    offset = json.loads(l[2])
                    if self.uhd:
                        self.time_tx_scd = offset[0]
                        self.time_tx_frac = offset[1]
                        offset = 0
                    else:
                        offset = int(offset)            
                except:
                    print "Offset non valid"
                    if self.uhd: #TODO : add intern time + BCH time
                        self.time_tx_scd = 0
                        self.time_tx_frac = 0
                        offset = 0
                    else:
                        offset = 0

            if self.state == LISTEN :
                
                try :
                    self.log("Trig - Frame : %s" % (self.frame_cnt))
                    if l[0] == self.wanted_tag:
                        self.state = BCH
                        self.slot_cnt = 0
                        self.msg_out = self.msg_full[self.slot_cnt]     # Init first msg to be sent

                        self.delay = self.nitems_written(0)-offset 

                        if self.delay>0: #
                            self.samp_cnt = self.delay
                        else:
                            self.samp_cnt= 200000

                        return 0
                        
                except:
                    pass

    def create_cch_msg(self, payload):
        self.log("Send ULCCH on error free channel : %s | %s | %s | %s" % (self.Id, "BS", self.frame_cnt, payload))
        msg = pmt.make_dict()
        msg = pmt.dict_add(msg, pmt.to_pmt("SRC"), pmt.to_pmt(self.Id))
        msg = pmt.dict_add(msg, pmt.to_pmt("DST"), pmt.to_pmt("BS"))
        msg = pmt.dict_add(msg, pmt.to_pmt("FRM"), pmt.to_pmt(self.frame_cnt))
        msg = pmt.dict_add(msg, pmt.to_pmt("CCH"), pmt.to_pmt(payload))
        return msg

    def create_inst_msg(self, payload):
        self.log("Send feedback to upper layer : %s | %s | %s" % (self.Id, self.frame_cnt, payload))
        msg = pmt.make_dict()
        msg = pmt.dict_add(msg, pmt.to_pmt("NODE"), pmt.to_pmt(self.Id))
        msg = pmt.dict_add(msg, pmt.to_pmt("FRAME"), pmt.to_pmt(int(self.frame_cnt)))
        msg = pmt.dict_add(msg, pmt.to_pmt("DLCCH"), pmt.to_pmt(payload))
        return msg

    def handle_inst(self, msg_pmt):
        with self.lock : 
            msg_pmt = pmt.deserialize_str(pmt.to_python(msg_pmt))
            if pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("ID"), pmt.PMT_NIL)) == self.Id:
                inst_ulcch = {}
                inst_ulcch["content"] = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("ULCCH"), pmt.PMT_NIL)) 
                inst_ulcch["frame"] = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("FRAME"), pmt.PMT_NIL)) 
                inst_ulcch["packet"] = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("SEND"), pmt.PMT_NIL)) 
                if self.frame_cnt == inst_ulcch["frame"]:
                    self.message_port_pub(pmt.to_pmt("ULCCH"), self.create_cch_msg(inst_ulcch["content"]))
                    inst_ulcch["send"] = True
                else:
                    inst_ulcch["send"] = False
                self.ulcch.append(inst_ulcch)
                self.log("Received new ULCCH instruction : %s" % (inst_ulcch))

    def handle_dlcch(self, msg_pmt):
        with self.lock :
            sn_id = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("DST"), pmt.PMT_NIL)) 
            bs_id = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("SRC"), pmt.PMT_NIL)) 
            frame = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("FRM"), pmt.PMT_NIL)) 
            if sn_id == self.Id: 
                self.dlcch = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("CCH"), pmt.PMT_NIL)) 
                # if self.frame_cnt != frame:
                #     self.frame_cnt = frame
                self.log("SN %s : DLCCH received : SRC - %s | Frame - %s | CCH - %s" % (sn_id, bs_id, frame, self.dlcch))
                print("SN %s : DLCCH received : SRC - %s | Frame - %s | CCH - %s" % (sn_id, bs_id, frame, self.dlcch))

                if self.frame_cnt == 0 and not self.inst_request_send:
                    self.log("Send START DLCCH to BS")
                    self.message_port_pub(pmt.to_pmt("ULCCH"), self.create_cch_msg("START"))
                    self.inst_request_send = True

    def blank_transmission(self, len_output):
        if self.uhd:
            return []
        else:
            return [0]*len_output

    def init_timer(self):
        if self.uhd:
            self.start_timer = datetime.now()

    def next_state(self):
        delta = datetime.now() - self.start_timer
        time_limit_ms = (self.STATES[2][PROC] + self.STATES[2][BCH] if self.state == PROC and self.active == True else self.STATES[2][self.state])
        if (delta.total_seconds() * 1000 >= time_limit_ms) or self.state == BCH:
            return True
        else:
            return False

    def run_state(self,output) :

        self.log("State : %s - nitems written %s" % (STATES[self.state], self.nitems_written(0)))
        
        self.samp_cnt += len(output)    # Sample count related to current state
        state_samp = self.to_samples(self.STATES[2][self.state])    
        diff = state_samp - self.samp_cnt       # Act as a timer when in local 
        self.log("Sample count %s - state samp %s - diff %s - len(output) %s" % (self.samp_cnt, state_samp, diff, len(output)))

        if self.uhd and self.state in (GUARD,BCH,PROC) and self.next_state():
            diff = -1
            self.log("UHD - state time exceeded - going to next state")

        ###############################################################################    
        ## If the cuurent state cannot run completely, 
        ## i.e the sample count exceeds the number of samples required for the current state
        if diff < 0 :  
            
            if not self.uhd:
                output[:] = [0]*len(output) # Clear buffer
            output = np.delete(output,slice(len(output)+diff,len(output)))    # Since diff is negative we use +diff

            if self.state == EMIT : 
                
                if self.slot_cnt in self.slots :
                    
                    if len(self.msg_out) == 0:
                        self.log("EMIT final - zeros - len %s" % (len(output)))
                        output[:] = [0]*len(output)
                    elif len(output) > len(self.msg_out) :    # In case output buffer is bigger than payload
                        self.log("EMIT final - data leftover and zeros - len msg %s" % (len(self.msg_out[:len(output)])))
                        output[:] = np.append(self.msg_out[:len(output)] , [0]*(abs(len(output)-len(self.msg_out))))  # Fill what's left with Sensor Data (if left)
                    else :
                        self.log("EMIT final - only data leftover")
                        output[:] = self.msg_out[:len(output)]
                        
                else :
                    output[:] = [0]*len(output)
                self.state = GUARD
                self.init_timer()

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
                        self.slot_cnt = 0  
                        
                    elif self.active == True:
                        self.message_port_pub(pmt.to_pmt("busy"), pmt.to_pmt('ARRAY'))
                    elif self.active == False:
                        self.message_port_pub(pmt.to_pmt("busy"), pmt.to_pmt('RESET_FRAME'))

                # elif self.state == LISTEN :
                #     # If needed 

                elif self.state == BCH :
                    self.slot_cnt = 0
                    self.state = EMIT
                       
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
                        self.init_timer()
                        
                elif self.state == PROC :
                    # End of frame --> Reset some variables
                    self.state = SLOT_READ
                    self.msg_full = np.array([])
                    self.msg_out = np.array([])
                    self.slot_msg = np.array([])
                    self.slot_cnt = 0
                    self.slots = []
                    self.active = -1
                    self.log("RESET proc -> slot_read")

                elif self.state not in self.STATES[0] :
                    print("STATE ERROR")
                    exit(1)
                
                if not self.uhd:
                    output[:] = [0]*len(output)
                else:
                    output = []

            self.samp_cnt = 0

        ###############################################################################
        # If current state can run one more time
        else :      
            self.samp_cnt -= len(output)
            if self.state==EMIT :
                
                if self.slot_cnt in self.slots :
                    if len(self.msg_out) == 0 :
                        output[:] = [0]*len(output)
                        self.log("EMIT ongoing : zeros")
                    else :    
                        max_output = min(len(output), len(self.msg_out))
                        output = output[:max_output]
                        output[:] = self.msg_out[:max_output]
                        self.log("EMIT ongoing : signal")
                        self.msg_out = self.msg_out[max_output:]
                        
                        
                else : # Empty EMIT slots
                    output[:] = [0]*len(output)

            else : 
                if not self.uhd:
                    output[:] = [0]*len(output)
                else:
                    output = []

            self.samp_cnt += len(output)
        ###############################################################################

        # Add tags for each state
        if self.state_tag != self.state :  
            self.state_tag = self.state
            offset = self.nitems_written(0)+len(output)

            if self.uhd and self.state == EMIT : 
                # UHD length tag
                key = pmt.intern(self.length_tag_key)
                value = pmt.to_pmt(self.to_samples(self.STATES[2][EMIT])) 
                self.add_item_tag(0,offset, key, value)

                # UHD time tag (received by BS)
                key = pmt.intern("tx_time")
                slot_time_scd = self.slot_cnt * (float(self.STATES[2][EMIT] + self.STATES[2][GUARD]) / 1000 )
                slot_time_frac_scd = float(slot_time_scd % 1)
                slot_time_full_scd = int(round(slot_time_scd - slot_time_frac_scd))
                value = pmt.to_pmt((self.time_tx_scd + slot_time_full_scd , self.time_tx_frac + slot_time_frac_scd)) 
                self.add_item_tag(0,offset, key, value)

                #LOG
                if self.clock_master:
                    time_now = self.topblock.uhd_usrp_sink_0_0.get_time_now()
                    self.log("Data send to UHD - Current UHD Time : %s - %s - Planned TX time : %s - %s" % (time_now.get_full_secs(), time_now.get_frac_secs(), self.time_tx_scd + slot_time_full_scd, self.time_tx_frac + slot_time_frac_scd))
                else:
                    self.log("Data send to UHD - Planned TX time : %s - %s" % (self.time_tx_scd + slot_time_full_scd, self.time_tx_frac + slot_time_frac_scd))
                    
            elif not self.uhd:
                if self.state == EMIT and self.slot_cnt in self.slots:
                    key = pmt.intern("ACTIF")
                else:
                    key = pmt.intern(self.STATES[1][self.state])
                value = pmt.to_pmt(self.slot_cnt)
                self.add_item_tag(0,offset, key, value)

        return len(output)

    def general_work(self,input_items,output_items):
        with self.lock :

            retval = self.run_state(output_items[0])
            return retval
