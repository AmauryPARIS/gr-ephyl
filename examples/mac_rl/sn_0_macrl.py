#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Sn 0 Macrl
# GNU Radio version: 3.7.14.0
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
import ephyl
import math, sys, numpy as np, random,string
import time


class sn_0_macrl(gr.top_block):

    def __init__(self, M=32, N=1, T_bch=200, T_g=50, T_p=1000, T_s=150, bs_slots=range(10), control='1', cp_ratio=0.25):
        gr.top_block.__init__(self, "Sn 0 Macrl")

        ##################################################
        # Parameters
        ##################################################
        self.M = M
        self.N = N
        self.T_bch = T_bch
        self.T_g = T_g
        self.T_p = T_p
        self.T_s = T_s
        self.bs_slots = bs_slots
        self.control = control
        self.cp_ratio = cp_ratio

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1e6
        self.gain = gain = 25
        self.freq = freq = 2450e6
        self.frame_len = frame_len = (T_bch+len(bs_slots)*(T_s+T_g)+T_p)/float(1000)
        self.MTU = MTU = 10000

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_sub_msg_source_0 = zeromq.sub_msg_source('tcp://mnode18:5556', 100)
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
        self.hier_sensor_0 = hier_sensor(
            M=M,
            N=1,
            T_bch=T_bch,
            T_g=T_g,
            T_p=T_p,
            T_s=T_s,
            bs_slots=bs_slots,
            control=control,
            log=True,
            samp_rate=samp_rate,
        )
        self.ephyl_easy_upper_0 = ephyl.easy_upper()
        self.blocks_null_sink_1 = blocks.null_sink(gr.sizeof_float*1)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.ephyl_easy_upper_0, 'inst'), (self.hier_sensor_0, 'Inst'))
        self.msg_connect((self.hier_sensor_0, 'feedback'), (self.ephyl_easy_upper_0, 'feedback'))
        self.msg_connect((self.zeromq_sub_msg_source_0, 'out'), (self.hier_sensor_0, 'DL'))
        self.connect((self.hier_sensor_0, 0), (self.blocks_null_sink_1, 0))
        self.connect((self.hier_sensor_0, 1), (self.uhd_usrp_sink_0_0, 0))

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.hier_sensor_0.set_M(self.M)

    def get_N(self):
        return self.N

    def set_N(self, N):
        self.N = N

    def get_T_bch(self):
        return self.T_bch

    def set_T_bch(self, T_bch):
        self.T_bch = T_bch
        self.hier_sensor_0.set_T_bch(self.T_bch)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_g(self):
        return self.T_g

    def set_T_g(self, T_g):
        self.T_g = T_g
        self.hier_sensor_0.set_T_g(self.T_g)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_p(self):
        return self.T_p

    def set_T_p(self, T_p):
        self.T_p = T_p
        self.hier_sensor_0.set_T_p(self.T_p)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_s(self):
        return self.T_s

    def set_T_s(self, T_s):
        self.T_s = T_s
        self.hier_sensor_0.set_T_s(self.T_s)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_bs_slots(self):
        return self.bs_slots

    def set_bs_slots(self, bs_slots):
        self.bs_slots = bs_slots
        self.hier_sensor_0.set_bs_slots(self.bs_slots)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_control(self):
        return self.control

    def set_control(self, control):
        self.control = control
        self.hier_sensor_0.set_control(self.control)

    def get_cp_ratio(self):
        return self.cp_ratio

    def set_cp_ratio(self, cp_ratio):
        self.cp_ratio = cp_ratio

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_sink_0_0.set_samp_rate(self.samp_rate)
        self.hier_sensor_0.set_samp_rate(self.samp_rate)

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
        "", "--T-p", dest="T_p", type="intx", default=1000,
        help="Set Proc duration (ms) [default=%default]")
    parser.add_option(
        "", "--control", dest="control", type="string", default='1',
        help="Set Control [default=%default]")
    return parser


def main(top_block_cls=sn_0_macrl, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    tb = top_block_cls(T_p=options.T_p, control=options.control)
    tb.start()
    tb.wait()


if __name__ == '__main__':
    main()
