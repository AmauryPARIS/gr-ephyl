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
    def __init__(self, list_sensor = ["a", "b"]):  # only default arguments here
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
        
        self.message_port_register_out(pmt.to_pmt("final_msg"))
        self.message_port_register_out(pmt.to_pmt("feedback"))

        self.lock = threading.Lock()

        self.sensor_count = len(list_sensor)

        self.frame_msg = 0
        self.frame_n = 0
        self.slot_n = ''
        self.data = ''
        self.filename = "BS_mux_"+time.strftime("%d%m%Y-%H%M%S")+".txt"
        self.filename_log = "LOG_BS_mux_"+time.strftime("%d%m%Y-%H%M%S")+".txt"

        self.received_packet = []
        self.received_ulcch = []
        self.crc = "wivuopnwusbywu"


    def log(self, log):
        if True:
            now = datetime.now().time()
            with open(self.filename_log,"a+") as f_log:
                f_log.write("%s-%s-%s-%s\n" % ("BS", self.frame_n, now, log)) 

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
                self.received_ulcch.append([sn_id, ulcch])
                self.log("ULCCH received : %s | %s | %s " % (sn_id, ulcch, frame))
                if len(self.received_ulcch) == self.sensor_count:
                    msg = pmt.make_dict()
                    msg = pmt.dict_add(msg, pmt.to_pmt("FRAME"), pmt.to_pmt(frame))
                    msg = pmt.dict_add(msg, pmt.to_pmt("ULCCH"), pmt.to_pmt(self.received_ulcch))    
                    msg = pmt.dict_add(msg, pmt.to_pmt("RX"), pmt.to_pmt(self.received_packet))

                    self.message_port_pub(pmt.to_pmt("feedback"), msg)
                    self.log("ALL ULCCH received : %s | %s | %s " % (frame, self.received_ulcch, self.received_packet))
                    self.received_packet = []
                    self.received_ulcch = []
                    


    def handle_data(self, msg_pmt):
        with self.lock : 
            self.data = pmt.to_python(pmt.cdr(msg_pmt))
            l = [chr(c) for c in self.data]
            l = ''.join(l)
            l = re.split(r'\t+', l)

            sn_id = l[0]
            sequence = l[1][0:3]
            crc = l[1][3:]
            print("MUX : %s | %s | %s vs %s" % (sn_id, sequence, crc, self.crc))
            if sequence[0] == sequence[1] and sequence[1] == sequence[2] and crc in self.crc:
                sequence = sequence[0]
                status = "RX"
            else: 
                sequence = "error"
                status = "BUSY"

            # Find a way to return the sequence
                
            l = [int(self.frame_n),self.slot_n] + l
            l = map(str,l)
            l = '\t'.join(l)
            # print "HERE"
            # print l

            self.log("BS RX : %s\n" % (l))  
            

            if any(self.slot_n) and any(self.data) :
                # res = [self.frame_n,self.slot_n,self.data]
                res = l
                # print "HEEEEEEEEEEEEEE"
                # print res
                res_pdu = pmt.cons(pmt.make_dict(), pmt.init_u8vector(len(res),[ord(c) for c in res]))
                self.received_packet.append([sn_id, sequence, status, self.frame_n])
                self.message_port_pub(pmt.to_pmt("final_msg"), res_pdu)
                # self.slot_n = self.data = ''
