#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Sensor flowgraph
# Description: Sensor flowgraph for the multislot dynamic version of the gr ephyl project
# GNU Radio version: 3.7.13.5
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
from hier_sensor_nbiot import hier_sensor_nbiot  # grc-generated hier_block
from optparse import OptionParser
import time


class sn_multislot_dyn_ephyl_nbiot(gr.top_block):

    def __init__(self, M=32, N=1, T_bch=200, T_g=50, T_p=1000, T_s=150, bs_slots=range(1), cp_ratio=0.25, debug_log=False, ip_bs_addr='mnode3', ip_decision_layer_addr='localhost', lora_bw=250e3, lora_cr=4, lora_crc=True, lora_sf=7, port_sn_feedback=5560, port_sn_inst=5559, sample_rate=1e6, sn_id='A'):
        gr.top_block.__init__(self, "Sensor flowgraph")

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
        self.cp_ratio = cp_ratio
        self.debug_log = debug_log
        self.ip_bs_addr = ip_bs_addr
        self.ip_decision_layer_addr = ip_decision_layer_addr
        self.lora_bw = lora_bw
        self.lora_cr = lora_cr
        self.lora_crc = lora_crc
        self.lora_sf = lora_sf
        self.port_sn_feedback = port_sn_feedback
        self.port_sn_inst = port_sn_inst
        self.sample_rate = sample_rate
        self.sn_id = sn_id

        ##################################################
        # Variables
        ##################################################
        self.incr_port_sensor_ulcch = incr_port_sensor_ulcch = 0 if sn_id == "A" else 1
        self.port_ulcch = port_ulcch = 5601 + incr_port_sensor_ulcch
        self.port_sync = port_sync = 5556
        self.port_dlcch = port_dlcch = 5600
        self.samp_rate = samp_rate = int(sample_rate)
        self.gain = gain = 25
        self.freq = freq = 2450e6
        self.frame_len = frame_len = (T_bch+len(bs_slots)*(T_s+T_g)+T_p)/float(1000)
        self.addr_ulcch = addr_ulcch = str("tcp://*:" + str(port_ulcch))
        self.addr_sync = addr_sync = str("tcp://" + str(ip_bs_addr) + ":" + str(port_sync))
        self.addr_sn_inst = addr_sn_inst = str("tcp://" + str(ip_decision_layer_addr) + ":" + str(port_sn_inst))
        self.addr_sn_feedback = addr_sn_feedback = str("tcp://*:" + str(port_sn_feedback))
        self.addr_dlcch = addr_dlcch = str("tcp://" + str(ip_bs_addr) + ":" + str(port_dlcch))
        self.MTU = MTU = 10000

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_sub_msg_source_0_1 = zeromq.sub_msg_source(addr_dlcch, 100)
        self.zeromq_sub_msg_source_0_0 = zeromq.sub_msg_source(addr_sync, 100)
        self.zeromq_sub_msg_source_0 = zeromq.sub_msg_source(addr_sn_inst, 100)
        self.zeromq_pub_msg_sink_0_0 = zeromq.pub_msg_sink(addr_ulcch, 100)
        self.zeromq_pub_msg_sink_0 = zeromq.pub_msg_sink(addr_sn_feedback, 100)
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
        self.uhd_usrp_sink_0_0.set_bandwidth(250e3, 0)
        self.hier_sensor_nbiot_0 = hier_sensor_nbiot(
            M=M,
            N=N,
            T_bch=T_bch,
            T_g=T_g,
            T_p=T_p,
            T_s=T_s,
            bs_slots=bs_slots,
            debug_log=debug_log,
            id_0=sn_id,
            log=debug_log,
            samp_rate=samp_rate,
        )
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.hier_sensor_nbiot_0, 'feedback'), (self.zeromq_pub_msg_sink_0, 'in'))
        self.msg_connect((self.hier_sensor_nbiot_0, 'ULCCH'), (self.zeromq_pub_msg_sink_0_0, 'in'))
        self.msg_connect((self.zeromq_sub_msg_source_0, 'out'), (self.hier_sensor_nbiot_0, 'Inst'))
        self.msg_connect((self.zeromq_sub_msg_source_0_0, 'out'), (self.hier_sensor_nbiot_0, 'DL'))
        self.msg_connect((self.zeromq_sub_msg_source_0_1, 'out'), (self.hier_sensor_nbiot_0, 'DLCCH'))
        self.connect((self.hier_sensor_nbiot_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.hier_sensor_nbiot_0, 1), (self.uhd_usrp_sink_0_0, 0))

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.hier_sensor_nbiot_0.set_M(self.M)

    def get_N(self):
        return self.N

    def set_N(self, N):
        self.N = N
        self.hier_sensor_nbiot_0.set_N(self.N)

    def get_T_bch(self):
        return self.T_bch

    def set_T_bch(self, T_bch):
        self.T_bch = T_bch
        self.hier_sensor_nbiot_0.set_T_bch(self.T_bch)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_g(self):
        return self.T_g

    def set_T_g(self, T_g):
        self.T_g = T_g
        self.hier_sensor_nbiot_0.set_T_g(self.T_g)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_p(self):
        return self.T_p

    def set_T_p(self, T_p):
        self.T_p = T_p
        self.hier_sensor_nbiot_0.set_T_p(self.T_p)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_s(self):
        return self.T_s

    def set_T_s(self, T_s):
        self.T_s = T_s
        self.hier_sensor_nbiot_0.set_T_s(self.T_s)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_bs_slots(self):
        return self.bs_slots

    def set_bs_slots(self, bs_slots):
        self.bs_slots = bs_slots
        self.hier_sensor_nbiot_0.set_bs_slots(self.bs_slots)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_cp_ratio(self):
        return self.cp_ratio

    def set_cp_ratio(self, cp_ratio):
        self.cp_ratio = cp_ratio

    def get_debug_log(self):
        return self.debug_log

    def set_debug_log(self, debug_log):
        self.debug_log = debug_log
        self.hier_sensor_nbiot_0.set_debug_log(self.debug_log)
        self.hier_sensor_nbiot_0.set_log(self.debug_log)

    def get_ip_bs_addr(self):
        return self.ip_bs_addr

    def set_ip_bs_addr(self, ip_bs_addr):
        self.ip_bs_addr = ip_bs_addr
        self.set_addr_sync(str("tcp://" + str(self.ip_bs_addr) + ":" + str(self.port_sync)))
        self.set_addr_dlcch(str("tcp://" + str(self.ip_bs_addr) + ":" + str(self.port_dlcch)))

    def get_ip_decision_layer_addr(self):
        return self.ip_decision_layer_addr

    def set_ip_decision_layer_addr(self, ip_decision_layer_addr):
        self.ip_decision_layer_addr = ip_decision_layer_addr
        self.set_addr_sn_inst(str("tcp://" + str(self.ip_decision_layer_addr) + ":" + str(self.port_sn_inst)))

    def get_lora_bw(self):
        return self.lora_bw

    def set_lora_bw(self, lora_bw):
        self.lora_bw = lora_bw

    def get_lora_cr(self):
        return self.lora_cr

    def set_lora_cr(self, lora_cr):
        self.lora_cr = lora_cr

    def get_lora_crc(self):
        return self.lora_crc

    def set_lora_crc(self, lora_crc):
        self.lora_crc = lora_crc

    def get_lora_sf(self):
        return self.lora_sf

    def set_lora_sf(self, lora_sf):
        self.lora_sf = lora_sf

    def get_port_sn_feedback(self):
        return self.port_sn_feedback

    def set_port_sn_feedback(self, port_sn_feedback):
        self.port_sn_feedback = port_sn_feedback
        self.set_addr_sn_feedback(str("tcp://*:" + str(self.port_sn_feedback)))

    def get_port_sn_inst(self):
        return self.port_sn_inst

    def set_port_sn_inst(self, port_sn_inst):
        self.port_sn_inst = port_sn_inst
        self.set_addr_sn_inst(str("tcp://" + str(self.ip_decision_layer_addr) + ":" + str(self.port_sn_inst)))

    def get_sample_rate(self):
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.set_samp_rate(int(self.sample_rate))

    def get_sn_id(self):
        return self.sn_id

    def set_sn_id(self, sn_id):
        self.sn_id = sn_id
        self.set_incr_port_sensor_ulcch(0 if self.sn_id == "A" else 1)
        self.hier_sensor_nbiot_0.set_id_0(self.sn_id)

    def get_incr_port_sensor_ulcch(self):
        return self.incr_port_sensor_ulcch

    def set_incr_port_sensor_ulcch(self, incr_port_sensor_ulcch):
        self.incr_port_sensor_ulcch = incr_port_sensor_ulcch
        self.set_port_ulcch(5601 + self.incr_port_sensor_ulcch)

    def get_port_ulcch(self):
        return self.port_ulcch

    def set_port_ulcch(self, port_ulcch):
        self.port_ulcch = port_ulcch
        self.set_addr_ulcch(str("tcp://*:" + str(self.port_ulcch)))

    def get_port_sync(self):
        return self.port_sync

    def set_port_sync(self, port_sync):
        self.port_sync = port_sync
        self.set_addr_sync(str("tcp://" + str(self.ip_bs_addr) + ":" + str(self.port_sync)))

    def get_port_dlcch(self):
        return self.port_dlcch

    def set_port_dlcch(self, port_dlcch):
        self.port_dlcch = port_dlcch
        self.set_addr_dlcch(str("tcp://" + str(self.ip_bs_addr) + ":" + str(self.port_dlcch)))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_sink_0_0.set_samp_rate(self.samp_rate)
        self.hier_sensor_nbiot_0.set_samp_rate(self.samp_rate)

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

    def get_addr_ulcch(self):
        return self.addr_ulcch

    def set_addr_ulcch(self, addr_ulcch):
        self.addr_ulcch = addr_ulcch

    def get_addr_sync(self):
        return self.addr_sync

    def set_addr_sync(self, addr_sync):
        self.addr_sync = addr_sync

    def get_addr_sn_inst(self):
        return self.addr_sn_inst

    def set_addr_sn_inst(self, addr_sn_inst):
        self.addr_sn_inst = addr_sn_inst

    def get_addr_sn_feedback(self):
        return self.addr_sn_feedback

    def set_addr_sn_feedback(self, addr_sn_feedback):
        self.addr_sn_feedback = addr_sn_feedback

    def get_addr_dlcch(self):
        return self.addr_dlcch

    def set_addr_dlcch(self, addr_dlcch):
        self.addr_dlcch = addr_dlcch

    def get_MTU(self):
        return self.MTU

    def set_MTU(self, MTU):
        self.MTU = MTU


def argument_parser():
    description = 'Sensor flowgraph for the multislot dynamic version of the gr ephyl project'
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option, description=description)
    parser.add_option(
        "", "--T-p", dest="T_p", type="intx", default=1000,
        help="Set Proc duration (ms) [default=%default]")
    parser.add_option(
        "", "--debug-log", dest="debug_log", type="intx", default=False,
        help="Set log [default=%default]")
    parser.add_option(
        "", "--ip-bs-addr", dest="ip_bs_addr", type="string", default='mnode3',
        help="Set IP/name of BS [default=%default]")
    parser.add_option(
        "", "--ip-decision-layer-addr", dest="ip_decision_layer_addr", type="string", default='localhost',
        help="Set IP/name of decision layer [default=%default]")
    parser.add_option(
        "", "--lora-bw", dest="lora_bw", type="eng_float", default=eng_notation.num_to_str(250e3),
        help="Set Bandwidth - LoRa [default=%default]")
    parser.add_option(
        "", "--lora-cr", dest="lora_cr", type="intx", default=4,
        help="Set Coding rate - LoRa [0-4] [default=%default]")
    parser.add_option(
        "", "--lora-crc", dest="lora_crc", type="intx", default=True,
        help="Set CRC [default=%default]")
    parser.add_option(
        "", "--lora-sf", dest="lora_sf", type="intx", default=7,
        help="Set Spreading factor - LoRa [default=%default]")
    parser.add_option(
        "", "--sample-rate", dest="sample_rate", type="eng_float", default=eng_notation.num_to_str(1e6),
        help="Set Sample Rate [default=%default]")
    parser.add_option(
        "", "--sn-id", dest="sn_id", type="string", default='A',
        help="Set Sensor ID - A or B [default=%default]")
    return parser


def main(top_block_cls=sn_multislot_dyn_ephyl_nbiot, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    tb = top_block_cls(T_p=options.T_p, debug_log=options.debug_log, ip_bs_addr=options.ip_bs_addr, ip_decision_layer_addr=options.ip_decision_layer_addr, lora_bw=options.lora_bw, lora_cr=options.lora_cr, lora_crc=options.lora_crc, lora_sf=options.lora_sf, sample_rate=options.sample_rate, sn_id=options.sn_id)
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
