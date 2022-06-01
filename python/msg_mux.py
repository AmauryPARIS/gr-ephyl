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
import re
from datetime import datetime

import base64
# from Crypto.Cipher import AES


class msg_mux(gr.sync_block):
    """

    Concatenates message data coming from inputs (payload, frame & slot number)
    """
    def __init__(self, phy_option=0, list_sensor = ["a", "b"], log=False):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Concatenate Messages',   # will show up in GRC
            in_sig=[],
            out_sig=[]
        )
        self.message_port_register_in(pmt.to_pmt("data"))        
        self.set_msg_handler(pmt.intern("data"), self.handle_data)
        self.message_port_register_in(pmt.to_pmt("slot_n"))
        self.set_msg_handler(pmt.intern("slot_n"), self.handle_slot)
        self.message_port_register_in(pmt.to_pmt("frame_n"))
        self.set_msg_handler(pmt.intern("frame_n"), self.handle_frame)  
        self.message_port_register_in(pmt.intern("ULCCH"))
        self.set_msg_handler(pmt.intern("ULCCH"), self.handle_ulcch)      
        self.message_port_register_in(pmt.intern("detect"))
        self.set_msg_handler(pmt.intern("detect"), self.handle_detect)    
        
        self.message_port_register_out(pmt.to_pmt("final_msg"))
        self.message_port_register_out(pmt.to_pmt("feedback"))

        self.lock = threading.Lock()

        self.sensor_count = len(list_sensor)
        self.list_sensor = list_sensor
        self.phy_option = phy_option

        self.frame_msg = 0
        self.frame_n = 0
        self.slot_n = ''
        self.data = ''
        self.filename = "BS_mux_"+time.strftime("%d%m%Y-%H%M%S")+".txt"
        self.filename_log = "LOG_BS_mux_"+time.strftime("%d%m%Y-%H%M%S")+".txt"
        self.filename_log_status = "RX_BS.txt"

        self.received_packet = []
        self.received_ulcch = []
        self.crc = "wivuopnwusbywu"
        self.logged = log


    def log(self, log):
        if self.logged:
            now = datetime.now().time()
            with open(self.filename_log,"a+") as f_log:
                f_log.write("%s-%s-%s-%s\n" % ("BS", self.frame_n, now, log)) 

    def log_status(self, log):
        if self.logged:
            now = datetime.now().time()
            with open(self.filename_log_status,"a+") as f_log:
                f_log.write("%s\n" % (log)) 

    def create_inst_msg(self, frame, payload):
        self.log("Send feedback to upper layer : %s | %s | %s" % ("BS", frame, payload))
        msg = pmt.make_dict()
        msg = pmt.dict_add(msg, pmt.to_pmt("FRAME"), pmt.to_pmt(frame))
        msg = pmt.dict_add(msg, pmt.to_pmt("ULCCH"), pmt.to_pmt(self.received_ulcch))    
        msg = pmt.dict_add(msg, pmt.to_pmt("RX"), pmt.to_pmt(payload))
        self.received_packet = []
        self.received_ulcch = []
        return msg

    def handle_frame(self, msg_pmt):
        with self.lock :
            self.frame_n = str(pmt.to_python(pmt.cdr(msg_pmt))[1])

    def handle_slot(self, msg_pmt):
        with self.lock :
            self.slot_n = str(pmt.to_python(pmt.cdr(msg_pmt))[1])

    def handle_ulcch(self, msg_pmt):
        with self.lock :
            
            sn_id = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("SRC"), pmt.PMT_NIL)) 
            ulcch = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("CCH"), pmt.PMT_NIL)) 
            frame = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("FRM"), pmt.PMT_NIL)) 
            if [sn_id, ulcch] not in self.received_ulcch:
                self.received_ulcch.append([frame, sn_id, ulcch])
                self.log("BS : ULCCH received : SRC - %s | Frame - %s | CCH - %s " % (sn_id, frame, ulcch))
                print("BS : ULCCH received : SRC - %s | Frame - %s | CCH - %s " % (sn_id, frame, ulcch))                

    def handle_detect(self, msg_pmt):
        detect = pmt.to_python(msg_pmt)
        rx = []
        log = []
        # Match the detect [IDLE, RX] power status to any received and demodulated packet
        for detect_elem in range(0,len(detect)):
            self.log("MUX slot %s : %s" % (detect_elem, detect[detect_elem]))
            if detect[detect_elem] == "IDLE":
                rx.append([detect_elem, detect[detect_elem]])
                log.append([detect_elem, detect[detect_elem]])
            else:
                packets = None
                found = False
                for msg_elem in range(0,len(self.received_packet)):
                    if int(self.received_packet[msg_elem][1]) == int(detect_elem): # Check for matching slot number
                        found = True
                        if self.received_packet[msg_elem][3] == "BUSY":
                            rx.append([detect_elem, detect[detect_elem]])
                            log.append([detect_elem, detect[detect_elem]])
                        else:
                            detect[detect_elem] = "RX"
                            packets = [self.received_packet[msg_elem][0], self.received_packet[msg_elem][2]] # [sn_id, sequence]
                            rx.append([detect_elem, detect[detect_elem], packets])
                            log.append([detect_elem, packets])
                if len(self.received_packet) == 0 or not found:
                    rx.append([detect_elem, detect[detect_elem]])
        
        # Frame number for the reception of dealt packets
        if len(self.received_ulcch) != 0:
            frame = self.received_ulcch[0][0]
        else:
            frame = self.frame_n
        self.log("End frame info received : %s | %s | %s " % (frame, self.received_ulcch, rx))
        print("BS - feedback : frame - %s | ulcch - %s | rx - %s " % (frame, self.received_ulcch, rx))
        # print("feedback,BS,%s,%s" % (frame,log))

        for i in range(0,len(rx)):
            if len(rx[i]) == 2:
                self.log_status("%s-%s-%s" % (frame, rx[i][0], rx[i][1]))
            else:
                self.log_status("%s-%s-%s-%s-%s" % (frame, rx[i][0], rx[i][1], rx[i][2][0], rx[i][2][1]))

        # Create and send feedback
        self.message_port_pub(pmt.to_pmt("feedback"), self.create_inst_msg(frame, rx))

    def intergity_check(self, sn_id, sequence, crc):
        id_check = False
        sequence_check = False
        crc_check = False

        # Sequence integrity verification
        if sequence[0] == sequence[1] and sequence[1] == sequence[2]:
            sequence_check = True

        # Sensor ID integrity verification
        if sn_id in self.list_sensor:
            id_check = True
        
        # Integrity verification
        og_crc = []
        for i in range(len(self.crc)):
            if i in range(3):
                og_crc += sequence[i]
            elif i == 3:
                og_crc += sn_id
            else:
                og_crc += self.crc[i]
        og_crc = "".join(og_crc)

        if crc == og_crc[3:]:
            crc_check = True
        
        # Return final state
        if id_check and sequence_check and crc_check:
            return True 
        else:
            return False 

    def handle_data(self, msg_pmt):
        with self.lock : 
            try:
                if self.phy_option in [0, 1] :# nb iot phy 
                    self.data = pmt.to_python(pmt.cdr(msg_pmt))
                    l = [chr(c) for c in self.data]
                    l = ''.join(l)
                    l = re.split(r'\t+', l)

                elif self.phy_option == 2: # lora phy
                    self.data = pmt.to_python(msg_pmt)
                    l = self.data 
                    l = re.split(r'\t+', l)

                else :
                    self.log("MSG MUX - Unknown PHY option %s" % (self.phy_option))
                    
                sn_id = l[0]
                sequence = l[1][0:3]
                crc = l[1][3:]

                self.log("Received - SN %s | seq %s | crc %s | raw %s" % (sn_id, sequence, crc, self.data))
            
                if self.intergity_check(sn_id, sequence, crc):
                    sequence = sequence[0]
                    status = "RX"
                else: 
                    sequence = "error"
                    status = "BUSY"
            except:
                if all(isinstance(c, int) for c in self.data):
                    self.log("Received error - data %s" % ([chr(c) for c in self.data]))
                else: 
                    self.log("Received error - data not int : %s" % (self.data))
                    # print(self.data)
                sn_id = "error"
                sequence = "error"
                crc = "error"
                status = "BUSY"


            self.log("BS - Message Mux : SRC - %s | Sequence - %s | Status - %s" % (sn_id, sequence, status))
            # print("BS - Message Mux : SRC - %s | Sequence - %s | Status - %s" % (sn_id, sequence, status))

            # Find a way to return the sequence
                
            l = [int(self.frame_n),self.slot_n] + l
            l = map(str,l)
            l = '\t'.join(l)
            # print "HERE"
            # print l

            self.log("test BS RX : %s\n" % (l))  
            

            if any(self.slot_n) and any(self.data) :
                # res = [self.frame_n,self.slot_n,self.data]
                res = l
                # print "HEEEEEEEEEEEEEE"
                # print res
                res_pdu = pmt.cons(pmt.make_dict(), pmt.init_u8vector(len(res),[ord(c) for c in res]))
                self.received_packet.append([sn_id, self.slot_n, sequence, status, self.frame_n])
                self.message_port_pub(pmt.to_pmt("final_msg"), res_pdu)
                # self.slot_n = self.data = ''
