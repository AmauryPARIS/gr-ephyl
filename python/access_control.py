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
    def __init__(self, bs_slots, Control = "random", save_log = False, ID = "Z"):
        gr.sync_block.__init__(self,
            name="access_control",
            in_sig=[],
            out_sig=[])

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
            
            with open(self.filename,"a+") as f:
                template =                                          \
                "SN-"+self.ID                                       \
                +"\n"+"======================"                      \
                +"\n"+"Access Policy: "                             \
                +"\n"+self.control                                  \
                +"\n"+"======================"                      \
                +"\n"+"Total frames: "                              \
                +"\n"                                               \
                +"\n"+"======================"                      \
                +"\n"+"Observed activation rate: "                  \
                +"\n"                                               \
                +"\n"+"======================"                      \
                +"\n"+"Active frames: "                             \
                +"\n"                                               \
                +"\n"+"======================"                      \
                +"\n"+"Detection rate: "                            \
                +"\n\n"                                             \
                +"\n"+"======================"                      \
                +"\n"+"PER (Packet Error Rate): "                   \
                +"\n\n"                                             \
                +"\n"+"======================"                      \
                +"\n"+"BER (Bit Error Rate): "                      \
                +"\n"                                               \
                +"\n"+"======================"                      \
                +"\n"
                f.write(template)

    def log(self, log):
        if True:
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

    # Generate random payload
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
        sn_id = data[0]
        payload = data[1]
        new_payload = []
        for i in range(len(payload)):
            if i in range(3):
                new_payload += sequence
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
        # Use all slots
        if self.control == 'all' :
            new_slots = self.bs_slots   
        #################################################################
        elif self.control == 'random' :
            new_slots = np.random.choice(self.bs_slots, 1).tolist()
        #################################################################
        ## Static slots as parameter separated by colon. e.g. '0:2:5:6'
        elif self.control[0].isdigit() :
            tmp_slots = map(int,re.split(r':+', self.control))
            test = [tmp_slots[i] in self.bs_slots for i in range(len(tmp_slots))]
            if False not in test :
                new_slots = tmp_slots
        #################################################################            
        # Increment each frame
        elif self.control == 'increment' :
            new_slots = [int(used_slots[0])]
            if new_slots[0]+1 not in self.bs_slots :
                new_slots = ['0']
            else:
                new_slots = [next]

        #################################################################                
        elif self.control == 'basic' :
            '''
            With basic Control Policy (Othmane):
            If success, keep one of the good usedslots
            If failure, increment
            (old version: find remaining unused slots, if none choose 2 random)
            '''
            if v.count('p') > 0 :
                new_slots = rx[h][1]
            else :
                if remaining :
                    new_slots = np.random.choice(remaining, min(1,len(remaining))).tolist()
                else :
                    new_slots = np.random.choice(self.bs_slots, 1).tolist()

            # if v.count('p') > 0 :
            #     # new_slots = [tx[h][1]]
            #     new_slots = used_slots
            # else :
            #     new_slots = [int(used_slots[0])]
            #     if new_slots[0]+1 not in self.bs_slots :
            #         new_slots = ['0']
            #     else:
            #         new_slots = [next]


        #################################################################
        # With UCB
        elif 'ucb' in self.control:
            #  In this example, nch channels are emulated
            #  then the number of times that this channel is selected is higher.
            try :
                tmp = re.split(r':+', self.control)
                self.alfa = float(tmp[1])
            except:
                print "UCB : Invalid alpha parameter. Setting it to 0.8"
                self.alfa=0.8

            self.watch += 1
            # Emulation of the channel occupancy  (it does not need to be implemented)
            nch=len(self.bs_slots)  # number of channels  
            ratio_global=nch*[0.0]

            # If for example, bs_slots==[0,1,2,3,4] and active_slots==[1,2,4],
            # result is stat_per = [False,True,True,False,True]
            stat_per = [(str(self.bs_slots[i]) in active_slots) for i in self.bs_slots]
            # print "[SN "+self.ID+"] STAT PER : ", stat_per

            for k in xrange(nch):
                if (stat_per[k]==True):
                    self.ratio_ch[k] += 1 
                ratio_global[k]  = float(self.ratio_ch[k])/float(self.watch)

            # print "[SN "+self.ID+"] Ratio of resource occupancy : ", ratio_global

            # UCB learning: it is the function to be included   
            new_indice = self.compute_ucb(nch,stat_per[self.indice],self.watch)

            new_slots = [new_indice]

        #################################################################
        # With No Control Policy, keep old slots
        else :
            self.control == 'NONE'
            new_slots = used_slots
            
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


    def compute_ucb(self, nch, rewards, time_ucb):
        # Input variables: rward(packet detection per slot), 
        # chsel (NumberTimesChannelSelected), 
        # watch(GlobalTime)
        xmean=nch*[0]
        bias=nch*[0]
        x=nch*[0]
        # self.alfa=0.8
        maxval=-1.0
        # Save variables
        self.time_ucb=time_ucb
        if  (rewards==True) : 
            self.rward[self.indice]+=1 
        # For each channel 
        for k in xrange(nch):
            xmean[k]=float(self.rward[k])/float(1+self.chsel[k])
            bias[k]=math.sqrt(  self.alfa*math.log(1+self.time_ucb)/float(1+self.chsel[k]) )
            x[k]=xmean[k]+bias[k]
            if x[k]>maxval:
               maxval=x[k]
               new_indice=k
        self.chsel[new_indice]+= 1 
        self.indice=new_indice

        return  new_indice

        
    def handle_inst(self, msg_pmt):
        with self.lock : 
            if pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("ID"), pmt.PMT_NIL)) == self.ID:
                inst_send = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("SEND"), pmt.PMT_NIL)) 
                inst_sequence = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("SEQUENCE"), pmt.PMT_NIL))
                frame = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("FRAME"), pmt.PMT_NIL))
                self.log("Inst received : %s | %s | %s" % (inst_send, inst_sequence, frame))

                if inst_send == "True":
                    self.send.append({"inst" : SEND, "sequence" : inst_sequence, "frame" : frame})
                elif inst_send == "False":
                    self.send.append({"inst" : IDLE, "sequence" : None, "frame" : frame})
                else:
                    self.send.append({"inst" : NOK, "sequence" : None, "frame" : frame})

    def handle_busy(self, msg_pmt):
        with self.lock :        
            self.busy = pmt.to_python(msg_pmt)

            for inst in self.send:
                if int(inst["frame"]) == int(self.frame_cnt):
                    self.send_inst = inst["inst"]
                    self.sequ_inst = inst["sequence"]

            self.log("BUSY : %s | %s | %s | %s " % (self.frame_cnt, self.busy, self.send_inst, self.send))

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
                    ########################################################################################################
                    ## Scheduler requests payload array to be sent in PHY chain
                        elif self.busy == 'DATA' :
                            self.log("Data send in PHY layer") 
                            ## Data is (node_id + line_i)
                            data = self.lines[self.i][2:]               # Remove frame number and slot number
                            print("Data bf : %s" % data)
                            data = self.add_symb(self.sequ_inst, data)  # Replace first random values by sequence
                            self.lines[self.i][3] = data[1]             # Update packet buffer
                            print("Data af : %s - %s" % (data, self.lines[self.i]))
                            data = '\t'.join(data)
                            OUT = pmt.cons(pmt.make_dict(), pmt.init_u8vector(len(data),[ord(c) for c in data]))    # Data = encrypted node_id + line_i
                            self.message_port_pub(pmt.to_pmt("Data"), OUT) 
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
                            print "[SN "+self.ID+"] ACCESS POLICY: " + self.control + "\n"
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
                                print "[SN "+self.ID+"] Score of Frame " + str(self.frame_cnt) +  " : " + str(result[0]) + "\n"
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
                            ###################### WRITE LOG FILE #########################
                            if self.save_log :    
                                with open(self.filename,"r") as f:
                                    lines = f.readlines()
                                    for i in range(len(lines)):
                                        if 'Total frames' in lines[i]:
                                            lines[i+1] = str(int(self.frame_cnt)+1)+'\n'
                                        if 'Observed activation rate' in lines[i]:
                                            try :
                                                lines[i+1] = str(len(self.detection_list)/(float(self.frame_cnt)-self.frame_offset+1))+'\n'
                                            except :
                                                lines[i+1] = str(len(self.detection_list)/(float(self.frame_cnt)+1))+'\n'
                                        if 'Active frames' in lines[i]:
                                            lines[i+1] = self.frame_cnt + ' ' + lines[i+1]
                                        if 'Detection rate' in lines[i]:
                                            tmp = "{:.2E}".format(self.detection_rate[-1])
                                            lines[i+1] = tmp+'\n'
                                            lines[i+2] = ' '.join(map(str,self.detection_list))+'\n'
                                        if 'PER' in lines[i]:
                                            tmp = "{:.2E}".format(self.PER[-1])
                                            lines[i+1] = tmp+'\n'
                                            lines[i+2] = ' '.join(map(str,self.error_list))+'\n'
                                        if 'BER' in lines[i]:
                                            tmp = "{:.2E}".format(self.BER)
                                            lines[i+1] = tmp+'\n'
                                with open(self.filename,"w") as f:
                                    f.write(''.join(lines))

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
                self.frame_cnt = self.RX[1]
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