#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Ms Fixed Odd
# Generated: Fri Feb  7 14:24:36 2020
##################################################

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio import zeromq
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from hier_sensor import hier_sensor  # grc-generated hier_block
from optparse import OptionParser
import math, sys, numpy as np, random,string
import time


class ms_fixed_odd(gr.top_block):

    def __init__(self, M=32, N=1, T_bch=200, T_g=50, T_p=1000, T_s=150, ar1=1, ar3=1, ar5=1, ar7=1, bs_slots=range(10), control1='1', control3='3', control5='5', control7='7', cp_ratio=0.25):
        gr.top_block.__init__(self, "Ms Fixed Odd")

        ##################################################
        # Parameters
        ##################################################
        self.M = M
        self.N = N
        self.T_bch = T_bch
        self.T_g = T_g
        self.T_p = T_p
        self.T_s = T_s
        self.ar1 = ar1
        self.ar3 = ar3
        self.ar5 = ar5
        self.ar7 = ar7
        self.bs_slots = bs_slots
        self.control1 = control1
        self.control3 = control3
        self.control5 = control5
        self.control7 = control7
        self.cp_ratio = cp_ratio

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1000000
        self.log = log = True
        self.gain = gain = 25
        self.freq = freq = 2450e6
        self.frame_len = frame_len = (T_bch+len(bs_slots)*(T_s+T_g)+T_p)/float(1000)
        self.MTU = MTU = 10000

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_sub_msg_source_0 = zeromq.sub_msg_source('tcp://mnode3:5556', 100)
        self.uhd_usrp_sink_0_0 = uhd.usrp_sink(
        	",".join(('', "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_sink_0_0.set_clock_source('external', 0)
        self.uhd_usrp_sink_0_0.set_time_source('external', 0)
        self.uhd_usrp_sink_0_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0_0.set_time_unknown_pps(uhd.time_spec())
        self.uhd_usrp_sink_0_0.set_center_freq(freq, 0)
        self.uhd_usrp_sink_0_0.set_gain(gain, 0)
        self.uhd_usrp_sink_0_0.set_antenna('TX/RX', 0)
        self.hier_sensor_0_2 = hier_sensor(
            M=M,
            N=1,
            T_bch=T_bch,
            T_g=T_g,
            T_p=T_p,
            T_s=T_s,
            activation_rate=ar3,
            bs_slots=bs_slots,
            control=control3,
            log=log,
            samp_rate=samp_rate,
        )
        self.hier_sensor_0_1 = hier_sensor(
            M=M,
            N=1,
            T_bch=T_bch,
            T_g=T_g,
            T_p=T_p,
            T_s=T_s,
            activation_rate=ar7,
            bs_slots=bs_slots,
            control=control7,
            log=log,
            samp_rate=samp_rate,
        )
        self.hier_sensor_0_0 = hier_sensor(
            M=M,
            N=1,
            T_bch=T_bch,
            T_g=T_g,
            T_p=T_p,
            T_s=T_s,
            activation_rate=ar5,
            bs_slots=bs_slots,
            control=control5,
            log=log,
            samp_rate=samp_rate,
        )
        self.hier_sensor_0 = hier_sensor(
            M=M,
            N=1,
            T_bch=T_bch,
            T_g=T_g,
            T_p=T_p,
            T_s=T_s,
            activation_rate=ar1,
            bs_slots=bs_slots,
            control=control1,
            log=log,
            samp_rate=samp_rate,
        )
        self.blocks_null_sink_0_2 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_1 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.zeromq_sub_msg_source_0, 'out'), (self.hier_sensor_0, 'DL'))
        self.msg_connect((self.zeromq_sub_msg_source_0, 'out'), (self.hier_sensor_0_0, 'DL'))
        self.msg_connect((self.zeromq_sub_msg_source_0, 'out'), (self.hier_sensor_0_1, 'DL'))
        self.msg_connect((self.zeromq_sub_msg_source_0, 'out'), (self.hier_sensor_0_2, 'DL'))
        self.connect((self.blocks_add_xx_0, 0), (self.uhd_usrp_sink_0_0, 0))
        self.connect((self.hier_sensor_0, 1), (self.blocks_add_xx_0, 0))
        self.connect((self.hier_sensor_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.hier_sensor_0_0, 1), (self.blocks_add_xx_0, 2))
        self.connect((self.hier_sensor_0_0, 0), (self.blocks_null_sink_0_1, 0))
        self.connect((self.hier_sensor_0_1, 1), (self.blocks_add_xx_0, 3))
        self.connect((self.hier_sensor_0_1, 0), (self.blocks_null_sink_0_0, 0))
        self.connect((self.hier_sensor_0_2, 1), (self.blocks_add_xx_0, 1))
        self.connect((self.hier_sensor_0_2, 0), (self.blocks_null_sink_0_2, 0))

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.hier_sensor_0_2.set_M(self.M)
        self.hier_sensor_0_1.set_M(self.M)
        self.hier_sensor_0_0.set_M(self.M)
        self.hier_sensor_0.set_M(self.M)

    def get_N(self):
        return self.N

    def set_N(self, N):
        self.N = N

    def get_T_bch(self):
        return self.T_bch

    def set_T_bch(self, T_bch):
        self.T_bch = T_bch
        self.hier_sensor_0_2.set_T_bch(self.T_bch)
        self.hier_sensor_0_1.set_T_bch(self.T_bch)
        self.hier_sensor_0_0.set_T_bch(self.T_bch)
        self.hier_sensor_0.set_T_bch(self.T_bch)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_g(self):
        return self.T_g

    def set_T_g(self, T_g):
        self.T_g = T_g
        self.hier_sensor_0_2.set_T_g(self.T_g)
        self.hier_sensor_0_1.set_T_g(self.T_g)
        self.hier_sensor_0_0.set_T_g(self.T_g)
        self.hier_sensor_0.set_T_g(self.T_g)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_p(self):
        return self.T_p

    def set_T_p(self, T_p):
        self.T_p = T_p
        self.hier_sensor_0_2.set_T_p(self.T_p)
        self.hier_sensor_0_1.set_T_p(self.T_p)
        self.hier_sensor_0_0.set_T_p(self.T_p)
        self.hier_sensor_0.set_T_p(self.T_p)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_s(self):
        return self.T_s

    def set_T_s(self, T_s):
        self.T_s = T_s
        self.hier_sensor_0_2.set_T_s(self.T_s)
        self.hier_sensor_0_1.set_T_s(self.T_s)
        self.hier_sensor_0_0.set_T_s(self.T_s)
        self.hier_sensor_0.set_T_s(self.T_s)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_ar1(self):
        return self.ar1

    def set_ar1(self, ar1):
        self.ar1 = ar1
        self.hier_sensor_0.set_activation_rate(self.ar1)

    def get_ar3(self):
        return self.ar3

    def set_ar3(self, ar3):
        self.ar3 = ar3
        self.hier_sensor_0_2.set_activation_rate(self.ar3)

    def get_ar5(self):
        return self.ar5

    def set_ar5(self, ar5):
        self.ar5 = ar5
        self.hier_sensor_0_0.set_activation_rate(self.ar5)

    def get_ar7(self):
        return self.ar7

    def set_ar7(self, ar7):
        self.ar7 = ar7
        self.hier_sensor_0_1.set_activation_rate(self.ar7)

    def get_bs_slots(self):
        return self.bs_slots

    def set_bs_slots(self, bs_slots):
        self.bs_slots = bs_slots
        self.hier_sensor_0_2.set_bs_slots(self.bs_slots)
        self.hier_sensor_0_1.set_bs_slots(self.bs_slots)
        self.hier_sensor_0_0.set_bs_slots(self.bs_slots)
        self.hier_sensor_0.set_bs_slots(self.bs_slots)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_control1(self):
        return self.control1

    def set_control1(self, control1):
        self.control1 = control1
        self.hier_sensor_0.set_control(self.control1)

    def get_control3(self):
        return self.control3

    def set_control3(self, control3):
        self.control3 = control3
        self.hier_sensor_0_2.set_control(self.control3)

    def get_control5(self):
        return self.control5

    def set_control5(self, control5):
        self.control5 = control5
        self.hier_sensor_0_0.set_control(self.control5)

    def get_control7(self):
        return self.control7

    def set_control7(self, control7):
        self.control7 = control7
        self.hier_sensor_0_1.set_control(self.control7)

    def get_cp_ratio(self):
        return self.cp_ratio

    def set_cp_ratio(self, cp_ratio):
        self.cp_ratio = cp_ratio

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_sink_0_0.set_samp_rate(self.samp_rate)
        self.hier_sensor_0_2.set_samp_rate(self.samp_rate)
        self.hier_sensor_0_1.set_samp_rate(self.samp_rate)
        self.hier_sensor_0_0.set_samp_rate(self.samp_rate)
        self.hier_sensor_0.set_samp_rate(self.samp_rate)

    def get_log(self):
        return self.log

    def set_log(self, log):
        self.log = log
        self.hier_sensor_0_2.set_log(self.log)
        self.hier_sensor_0_1.set_log(self.log)
        self.hier_sensor_0_0.set_log(self.log)
        self.hier_sensor_0.set_log(self.log)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.uhd_usrp_sink_0_0.set_gain(self.gain, 0)


    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_sink_0_0.set_center_freq(self.freq, 0)

    def get_frame_len(self):
        return self.frame_len

    def set_frame_len(self, frame_len):
        self.frame_len = frame_len

    def get_MTU(self):
        return self.MTU

    def set_MTU(self, MTU):
        self.MTU = MTU


def argument_parser():
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option)
    parser.add_option(
        "", "--ar1", dest="ar1", type="eng_float", default=eng_notation.num_to_str(1),
        help="Set Activation rate [default=%default]")
    parser.add_option(
        "", "--ar3", dest="ar3", type="eng_float", default=eng_notation.num_to_str(1),
        help="Set Activation rate [default=%default]")
    parser.add_option(
        "", "--ar5", dest="ar5", type="eng_float", default=eng_notation.num_to_str(1),
        help="Set Activation rate [default=%default]")
    parser.add_option(
        "", "--ar7", dest="ar7", type="eng_float", default=eng_notation.num_to_str(1),
        help="Set Activation rate [default=%default]")
    parser.add_option(
        "", "--control1", dest="control1", type="string", default='1',
        help="Set Control [default=%default]")
    parser.add_option(
        "", "--control3", dest="control3", type="string", default='3',
        help="Set Control [default=%default]")
    parser.add_option(
        "", "--control5", dest="control5", type="string", default='5',
        help="Set Control [default=%default]")
    parser.add_option(
        "", "--control7", dest="control7", type="string", default='7',
        help="Set Control [default=%default]")
    return parser


def main(top_block_cls=ms_fixed_odd, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    tb = top_block_cls(ar1=options.ar1, ar3=options.ar3, ar5=options.ar5, ar7=options.ar7, control1=options.control1, control3=options.control3, control5=options.control5, control7=options.control7)
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
