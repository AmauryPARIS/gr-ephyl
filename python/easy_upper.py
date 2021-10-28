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

import time
import numpy, pmt
from gnuradio import gr
from datetime import datetime

class easy_upper(gr.sync_block):
    """
    docstring for block easy_upper
    """
    def __init__(self, BS = True, list_sensor = ["a", "b"]):
        gr.sync_block.__init__(self,
            name="easy_upper",
            in_sig=[],
            out_sig=[])

        self.BS = BS
        self.list_sensor = list_sensor
        self.count = 0

        self.message_port_register_out(pmt.to_pmt("inst"))

        self.message_port_register_in(pmt.intern("feedback"))
        self.set_msg_handler(pmt.intern("feedback"), self.handle_feedback)
        self.sensors_instruction = {}
        if BS:
            self.filename_log = "LOG_BS_easy_upper_"+time.strftime("%d%m%Y-%H%M%S")+".txt"
        else:
            self.filename_log = "LOG_SN_easy_upper_"+time.strftime("%d%m%Y-%H%M%S")+".txt"

    def log(self, frame, log):
        if True:
            now = datetime.now().time()
            with open(self.filename_log,"a+") as f_log:
                f_log.write("%s-%s-%s-%s\n" % ("UPPER", frame, now, log)) 

    def handle_feedback(self, msg_pmt):
        feedback = pmt.to_python(msg_pmt)
        msg = pmt.make_dict()

        ########## Base Station ##########
        if self.BS:

            # Extract feedback information
            frame_nbr = int(pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("FRAME"), pmt.PMT_NIL))) # Current frame number
            ulcch = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("ULCCH"), pmt.PMT_NIL)) # List of [sensor ID, ULCCH message]
            rx = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("RX"), pmt.PMT_NIL)) # List of [Frame number , Slot Number, sensor ID, Message content] - separated by \t
            print("BS Easy upper : %s | %s | %s" % (frame_nbr, ulcch, rx))
            
            # Build response for each sensor
            list_dlcch = []
            for sensor in self.list_sensor:
                sn_id = sensor
                dlcch = str("dlcch_" + str(frame_nbr +1) + "_" + str(sn_id))
                list_dlcch.append([sn_id, dlcch])
            
            msg = pmt.dict_add(msg, pmt.to_pmt("DLCCH"), pmt.to_pmt(list_dlcch))
            msg = pmt.dict_add(msg, pmt.to_pmt("FRAME"), pmt.to_pmt(frame_nbr +1 ))
            self.log(frame_nbr, "Feedback : Frame %s | ULCCH %s | RX %s - Return : DLCCH %s | Frame %s" % (frame_nbr, ulcch, rx, list_dlcch, frame_nbr +1) )
            
        ########## Sensor / Agent ##########
        else:
            
            # Extract feedback information
            sensor_id = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("NODE"), pmt.PMT_NIL)) 
            frame = int(pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("FRAME"), pmt.PMT_NIL)))
            dlcch = pmt.to_python(pmt.dict_ref(msg_pmt, pmt.to_pmt("DLCCH"), pmt.PMT_NIL))
            print("SN Easy upper : %s | %s | %s" % (frame, sensor_id, dlcch))

            # Build response for this sensor
            action = "True"
            if numpy.random.uniform() < 0.3:
                action = "True" 

            sequence = "1"
            if numpy.random.uniform() < 0.5:
                sequence = "2" 

            msg = pmt.dict_add(msg, pmt.to_pmt("ID"), pmt.to_pmt(sensor_id))
            msg = pmt.dict_add(msg, pmt.to_pmt("FRAME"), pmt.to_pmt(frame +1))
            msg = pmt.dict_add(msg, pmt.to_pmt("SEND"), pmt.to_pmt(action))
            msg = pmt.dict_add(msg, pmt.to_pmt("SEQUENCE"), pmt.to_pmt(sequence)) # Not yet working
            #if sensor_id is not None: # not clean - solve frame 0
            msg = pmt.dict_add(msg, pmt.to_pmt("ULCCH"), pmt.to_pmt(str("ulcch_" + str(frame +1) + "_" + str(sensor_id))))

            self.log(frame, "Feedback : Node %s | Frame %s | DLCCH %s - Return : Node %s | Frame %s | Send %s | Seq %s" % (sensor_id, frame, dlcch, sensor_id, frame +1, action, sequence) )
                
        # Send back instruction  
        self.message_port_pub(pmt.to_pmt("inst"), msg)
