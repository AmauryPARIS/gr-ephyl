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
import pmt
import time
import random
import threading
import math
from decimal import Decimal
from datetime import datetime


from gnuradio import gr, gr_unittest, blocks

import ntpath
#from Crypto.Cipher import AES
import base64

import string
import re

SEND, IDLE, NOK = 0,1,2


class access_control(gr.sync_block):
    """
    docstring for block access_control
    """
    def __init__(self, bs_slots, Control = "random", save_log = False, ID = "Z", log=False):
        gr.sync_block.__init__(self,
            name="access_control",
            in_sig=[],
            out_sig=[])

        self.logged = log

        self.message_port_register_out(pmt.to_pmt("Array"))
        self.message_port_register_out(pmt.to_pmt("Data"))
        self.message_port_register_out(pmt.to_pmt("PER"))
        self.message_port_register_out(pmt.to_pmt("DLCCH"))

        self.message_port_register_in(pmt.intern("busy"))
        self.set_msg_handler(pmt.intern("busy"), self.handle_busy)
        self.message_port_register_in(pmt.intern("DL"))
        self.set_msg_handler(pmt.intern("DL"), self.handle_DL)    

        self.message_port_register_in(pmt.intern("inst"))
        self.set_msg_handler(pmt.intern("inst"), self.handle_inst)      

        self.lock = threading.Lock()
        self.ID = ID

        self.filename_log = "LOG_SN_"+self.ID+"_access_"+time.strftime("%d%m%Y-%H%M%S")+".txt"
        self.save_detail_log = True

        self.slot_n = -1
        self.data = []
        self.busy = True
        self.lines = []    
        self.i = 0
        self.DL = ''

        self.frame_offset = 0

        self.control = Control

        self.bs_slots = bs_slots
        self.send = []
        self.send_inst = NOK
        self.sequ_inst = None
        self.sequence = None
        self.crc = "wivuopnwusbywu"
        self.active = -1

        self.detection = 0
        self.detection_rate = 64*[0]
        self.detection_list = []

        self.PER = 64*[0]
        self.error_list = []
        self.error = 0
        self.cnt = 0
        self.frame_cnt = 0
        
        self.error_bits = '0'
        self.error_bit_cnt = 0
        self.BER = 0.0

        self.RX = ''
        self.RX_frame = []

        self.watch = 0
        self.stat_per = [True]*len(bs_slots)
        self.ratio_ch =[0]*len(bs_slots)
        self.rward =[0]*len(bs_slots)
        self.chsel =[0]*len(bs_slots)
        self.chsel[0] = 1      # First channel is selected at the beginning
        self.time_ucb = 0
        self.indice = 0

        self.tmp_data = self.rand_data(14)      # Created to keep the same data bits
        ## Generate first payload with: 
        ## Frame nb + ID + 1 Slot + False (i.e. slot 0) + 14 random bytes 
        self.lines = self.gen_rand_pld(self.ID,1,self.rand_slots(1),self.tmp_data)
        result = self.compare_pld(self.lines,4*[''])
        self.lines = self.gen_rand_pld(self.ID,1,result[1],self.tmp_data)
        self.error = 0
        self.detection = 0
        
        self.save_log = save_log
        if self.save_log :
            self.filename = "SN-"+self.ID+"_"+time.strftime("%d%m%Y-%H%M%S")+".txt"
            


    def log(self, log):
        if self.logged:
            now = datetime.now().time()
            with open(self.filename_log,"a+") as f_log:
                f_log.write("%s-%s-%s-%s\n" % (self.ID, self.frame_cnt, now, log)) 

    def rand_slots(self,len) :
        res = [random.choice(self.bs_slots) for _ in xrange(len)]
        return map(str, res)

    def rand_data(self,len) :
        res = ''
        letters = string.ascii_lowercase
        res =  ''.join(random.choice(letters) for i in xrange(len))
        return res 

    # Generate random payload // !! // -> Modified to always use the same sequence (integrity check performed at BS)
    def gen_rand_pld(self,ID,n=1,slots=[0],data=False) :    
        res = []
        if not any(slots) :
            slots = [0]
        #if not data :
            #data = self.rand_data(14)
        data = self.crc
        slots = map(str, slots)
        for j in range(len(slots)):
            ## Small note here, the payload is adapted if the
            ## slot number contains more than two characters
            res += [[str(self.frame_cnt),slots[j], ID, data[:len(data)-len(slots[j])+1]]]
        
        self.log("Generate new payload : %s" % (res))
        return res 

    def add_symb(self, sequence, data):
        self.log("add sym : seq %s - data %s" % (sequence, data))
        sn_id = data[0]
        payload = data[1]
        new_payload = []
        for i in range(len(payload)):
            if i in range(3):
                new_payload += sequence
            elif i == 3:
                new_payload += sn_id
            else:
                new_payload += payload[i]
        return [sn_id, "".join(new_payload)]

    # Compare Tx & Rx PLD
    def compare_pld(self,TX,rx) :    
        v=''
        h = 0
        active_slots = []
        used_slots = []
        new_slots = []
        remaining = []
        ERROR_FREE_BIT = 4
        self.error = 0
        self.detection = 0
        tx = TX

        # Verify that rx and tx frames are arrays, to avoid errors when sweeping
        if len(np.shape(TX)) < 2 :
            tx = [TX]
        if len(np.shape(rx)) < 2 :
            rx = [rx]
        

        # print "===========TX============"
        # print ("TX : %s" % tx)
        # print "===========RX============"
        # print ("RX : %s" % rx)
        # print "===========#TX/RX#============"
        for j in xrange(len(tx)):    
            used_slots = np.append(used_slots,tx[j][1])  

        for f in range(len(rx)) :
            if len(rx[f])>3 :
                active_slots = np.append(active_slots,rx[f][1])
                for j in xrange(len(tx)):
                    self.log("Compare PLD : %s | %s" % (rx[f], tx[j]))
                    # Check frame match
                    if rx[f][0] == tx[j][0]:  
                        v += 'f'
                    ## Check for slot activity
                    if rx[f][1] == tx[j][1]:     
                        v += 's'
                        ## Check for matching id
                    if rx[f][2] == tx[j][2]:     
                        v += 'i'
                        ## Check for matching payload
                        if rx[f][3][:-ERROR_FREE_BIT] == tx[j][3][:-ERROR_FREE_BIT]:    # Some sporadic bug causes the last sample to be (sometimes) corrupted,      
                            v += 'p'                          # Probably a software bug. Unsolved yet
                            self.log("Considered OK")
                        
                        ## Compute BER for detected packets
                        rx_bits = ''.join(format(ord(x), 'b') for x in rx[f][3][:-ERROR_FREE_BIT])
                        tx_bits = ''.join(format(ord(x), 'b') for x in tx[j][3][:-ERROR_FREE_BIT])
                        y = int(rx_bits, 2)^int(tx_bits,2)
                        self.error_bits = bin(y)[2:].zfill(len(tx_bits))

                        h = f 

        if not any(active_slots)  :
            active_slots = ['0']            
        ############################################################################################
        used_slots = list(dict.fromkeys(used_slots))   # Remove duplicates
        remaining = list(set(map(str, self.bs_slots)) - set(active_slots))
        remaining.sort()
        next = str(int(max(used_slots))+1)

        #################################################################
        # Prepare for all slots
        new_slots = self.bs_slots   
            
        ############################################################################################
        # print "[SN "+self.ID+"] Used Slots " + str(used_slots) + "\n"
        # print "[SN "+self.ID+"] Active Slots " + str(active_slots) + "\n"
        # print "[SN "+self.ID+"] Remaining Slots " + str(remaining) + "\n"
        # print "[SN "+self.ID+"] New Slots " + str(new_slots) + "\n"

        if v.count('p') > 0 :
            self.error = 0
        else :
            self.error = 1
        
        # if v.count('s') > 0 and v.count('i') > 0:
        if v.count('s') > 0 and v.count('i') > 0:
            self.detection = 1
        else:
            self.detection = 0

        used_slots = list(set(used_slots))
        used_slots.sort()
        active_slots = list(set(active_slots))
        active_slots.sort()
        new_slots = list(set(new_slots))
        new_slots.sort()

        return [v,new_slots,active_slots,self.error]
        
    def handle_inst(self, msg_pmt):
        with self.lock : 
            msg_pmt = pmt.deserialize_str(pmt.to_python(msg_pmt))
            if pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("ID"), pmt.PMT_NIL)) == self.ID:
                inst_send = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("SEND"), pmt.PMT_NIL)) 
                inst_sequence = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("SEQUENCE"), pmt.PMT_NIL))
                frame = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("FRAME"), pmt.PMT_NIL))
                self.log("Inst received : send - %s | sequence - %s | frame - %s" % (inst_send, inst_sequence, frame))
                print("SN %s - Inst received : send - %s | sequence - %s | frame - %s" % (self.ID, inst_send, inst_sequence, frame))

                if inst_send == "True":
                    self.send.append({"inst" : SEND, "sequence" : inst_sequence, "frame" : frame})
                elif inst_send == "False":
                    self.send.append({"inst" : IDLE, "sequence" : None, "frame" : frame})
                else:
                    self.send.append({"inst" : NOK, "sequence" : None, "frame" : frame})

    def apply_slot_sched(self):
        self.log("BEGIN Apply slot sched - sequ inst %s | lines %s" % (reversed(self.sequ_inst), self.lines))
        if len(self.sequ_inst) == len(self.lines):
            for inst in reversed(self.sequ_inst):
                slot_nbr = int(inst[0])
                sequ = str(inst[1])
                if sequ is "False":
                    self.log("POP Apply slot sched - slot %s | lines %s" % (slot_nbr, self.lines))
                    self.lines.pop(slot_nbr)
            self.log("Apply slot sched - sequ inst %s | lines %s" % (self.sequ_inst, self.lines))
                
    def handle_busy(self, msg_pmt):
        with self.lock :        
            self.busy = pmt.to_python(msg_pmt)

            for inst in self.send:
                if int(inst["frame"]) == int(self.frame_cnt):
                    self.send_inst = inst["inst"]
                    self.sequ_inst = inst["sequence"]

            self.log("BUSY : frame - %s | status - %s | send inst - %s | list inst - %s " % (self.frame_cnt, self.busy, self.send_inst, self.send))

            if self.busy != True :
                if self.i < len(self.lines) :
                    ## Scheduler informs a reset before sending data
                    if self.busy == 'RESET' :
                        self.i = 0
                    ########################################################################################################
                    elif self.busy == 'ACTIVE?':
                        if self.send_inst == SEND:
                            self.message_port_pub(pmt.to_pmt("Array"), pmt.to_pmt("ACTIVE"))
                            self.active = True
                            self.log("Active frame")
                            self.apply_slot_sched()
                        elif self.send_inst == IDLE:
                            self.message_port_pub(pmt.to_pmt("Array"), pmt.to_pmt("INACTIVE"))
                            self.active = False
                            self.log("Inactive frame")
                        elif self.send_inst == NOK:
                            self.message_port_pub(pmt.to_pmt("Array"), pmt.to_pmt("INACTIVE"))
                            self.active = False
                            self.log("Default inactive frame")
                        else:
                            self.log("Unknown active instruction")

                    else :
                    ########################################################################################################
                    ## Scheduler requests node ID and payload array to compute IQ signal length
                        if self.busy == 'ARRAY' :
                            ## ID is removed later by the scheduler
                            tmp = self.lines[self.i]
                            if self.active==True:     # If sensor is active for the current frame
                                self.message_port_pub(pmt.to_pmt("Array"), pmt.to_pmt(tmp))   # Send 1st char of each line (aka slots)
                                self.log("Request slot schedule - slot %s | i %s | lines %s" % (tmp, self.i, self.lines))

                    ########################################################################################################
                    ## Scheduler requests payload array to be sent in PHY chain
                        elif self.busy == 'DATA' :
                            
                            ## Data is (node_id + line_i)
                            data = self.lines[self.i][2:]               # Remove frame number and slot number
                            slot_nbr = int(self.lines[self.i][1])
                            data = self.add_symb(self.sequ_inst[slot_nbr][1], data)  # Replace first random values by sequence
                            self.lines[self.i][3] = data[1]             # Update packet buffer

                            data = '\t'.join(data)
                            OUT = pmt.cons(pmt.make_dict(), pmt.init_u8vector(len(data),[ord(c) for c in data]))    # Data = encrypted node_id + line_i
                            self.message_port_pub(pmt.to_pmt("Data"), OUT) 
                            self.log("Data send in PHY layer - data %s | i %s | lines %s" % (data, self.i, self.lines)) 
                        self.i += 1
                    ########################################################################################################
                    ## Scheduler informs a frame reset (frame finished or new will start)
                    if self.busy == 'RESET_FRAME' :
                        for elem in range(0,len(self.send)):
                            if int(self.send[elem]["frame"]) == int(self.frame_cnt) -2:
                                self.send.pop(elem)
                                break
                        self.log("RESET")

                        self.i=0
                        if self.active == True :
                            #print "[SN "+self.ID+"] ACCESS POLICY: " + self.control + "\n"
                            ##################### PROCESS RECEIVED FRAMES ##############################
                            ## Activity in DL :
                            if any(self.RX_frame) :
                                ## Check if valid + if multiple or single received frame
                                if len(self.RX_frame) >= 4 and len(self.RX_frame)%4 == 0 :
                                    self.RX_frame = np.reshape(self.RX_frame, (-1, 4))      # Sort received frames by rows
                                    result = self.compare_pld(self.lines,self.RX_frame)
                                    ## Generate new payload 
                                    self.lines = self.gen_rand_pld(self.ID,1,result[1],self.tmp_data)
                                    print "[SN "+self.ID+"] Score of Frame " + str(self.frame_cnt) +  " : " + str(result[0]) + "\n"
                                    self.log("[SN "+self.ID+"] Score of Frame " + str(self.frame_cnt) +  " : " + str(result[0]) + "")
                            ## No activity in DL
                            else:
                                result = self.compare_pld(self.lines,[4*['']])
                                # Generate new payload 
                                self.lines = self.gen_rand_pld(self.ID,1,result[1],self.tmp_data)
                                #print "[SN "+self.ID+"] Score of Frame " + str(self.frame_cnt) +  " : " + str(result[0]) + "\n"
                                self.log("[SN "+self.ID+"] Score of Frame " + str(self.frame_cnt) +  " : " + str(result[0]) + "")
                                self.error = 1
                                self.detection = 0
                            ############################################################################################

                            ##################### COMPUTE PER #####################
                            self.error_list = map(int,np.append(self.error_list,self.error))
                            self.cnt = len(self.error_list)   # Number of detected packets
                            self.PER = self.PER[1:] + [0]
                            self.PER[-1] = sum(self.error_list)/float(self.cnt)
                            per_pdu = pmt.cons(pmt.make_dict(), pmt.init_f32vector(64,self.PER))    
                            self.message_port_pub(pmt.to_pmt("PER"), per_pdu)

                            ##################### COMPUTE DETECTION RATE #####################
                            self.detection_list = map(int,np.append(self.detection_list,self.detection))
                            self.detection_rate = self.detection_rate[1:] + [0]
                            self.detection_rate[-1] = sum(self.detection_list)/float(self.cnt)
                            self.detection = 0

                            ##################### COMPUTE BER #####################
                            self.error_bit_cnt += self.error_bits.count('1')
                            self.BER = self.error_bit_cnt/float(self.cnt*len(self.error_bits))
                            # print "BER"
                            # print self.BER
                            # ###################### WRITE LOG FILE #########################
                            # if self.save_log :    
                            #     with open(self.filename,"r") as f:
                            #         lines = f.readlines()
                            #         for i in range(len(lines)):
                            #             if 'Total frames' in lines[i]:
                            #                 lines[i+1] = str(int(self.frame_cnt)+1)+'\n'
                            #             if 'Observed activation rate' in lines[i]:
                            #                 try :
                            #                     lines[i+1] = str(len(self.detection_list)/(float(self.frame_cnt)-self.frame_offset+1))+'\n'
                            #                 except :
                            #                     lines[i+1] = str(len(self.detection_list)/(float(self.frame_cnt)+1))+'\n'
                            #             if 'Active frames' in lines[i]:
                            #                 lines[i+1] = str(self.frame_cnt) + ' ' + lines[i+1]
                            #             if 'Detection rate' in lines[i]:
                            #                 tmp = "{:.2E}".format(self.detection_rate[-1])
                            #                 lines[i+1] = tmp+'\n'
                            #                 lines[i+2] = ' '.join(map(str,self.detection_list))+'\n'
                            #             if 'PER' in lines[i]:
                            #                 tmp = "{:.2E}".format(self.PER[-1])
                            #                 lines[i+1] = tmp+'\n'
                            #                 lines[i+2] = ' '.join(map(str,self.error_list))+'\n'
                            #             if 'BER' in lines[i]:
                            #                 tmp = "{:.2E}".format(self.BER)
                            #                 lines[i+1] = tmp+'\n'
                            #     with open(self.filename,"w") as f:
                            #         f.write(''.join(lines))

                            self.RX_frame = [] 

                        else : 
                            '''
                            If sensor is inactive, it still has to decide for next frame based on
                            the last received frame. It doesn't matter if the latter is empty,
                            since the inactive frame isn't counted for PER
                            '''
                            result = self.compare_pld(self.lines,self.RX_frame)
                            self.lines = self.gen_rand_pld(self.ID,1,result[1],self.tmp_data)


                else :
                    self.message_port_pub(pmt.to_pmt("Array"), pmt.to_pmt("STOP"))
                    self.i = 0 
                    self.log("STOP")

            self.busy = True

    # Here we process all DL data broadcasted by the BS
    def handle_DL(self, msg_pmt):
        with self.lock :        

            self.watch += 1
            self.DL = pmt.to_python(msg_pmt)
            
            l = [chr(c) for c in self.DL[1]]
            l = ''.join(l)
            self.RX = re.split(r'\t+', l)
            self.log("Feedback from BS : %s " % (self.RX))
            if self.RX[0] == 'corr_est':
                self.frame_cnt = int(self.RX[1])
                '''
                In case SN starts way later than BS, 
                frame_cnt will have a start "offset", 
                which has to be taken into account in 
                the computing of the Observed activation rate
                '''
                if int(self.frame_cnt) != 0 and self.frame_offset == 0 :
                    self.frame_offset = int(self.frame_cnt) + 1
                elif int(self.frame_cnt) == 0 :
                    self.frame_offset = 'NaN'

            elif self.RX[0] == 'end_frame':
                self.frame_cnt = int(self.RX[1]) +1
                self.log("Receive end frame bch - Frame n%s" % (self.frame_cnt))

            ## Look for a tab caracter in DL message, to avoid processing beacon message
            else:                
                # Correct a silly bug where a '0' is converted to '\x00', not the optimal correction
                if '\x00' in self.RX[0] :   
                    self.RX = ['0'] + [t.replace('\x00', '') for t in self.RX]

                # If received frame is valid <> 4 fields separated with a \t
                if len(self.RX)%4 == 0 :
                    self.RX_frame = np.append([self.RX_frame],[self.RX])

            self.RX = ''
            self.DL = '' 
