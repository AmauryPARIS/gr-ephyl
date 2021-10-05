# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: IoT Sensor emulator (TurboFSK PHY)
# Author: Othmane Oubejja, CEA leti
# Generated: Wed Jan 29 17:14:13 2020
##################################################

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import ephyl
import math, sys, numpy as np, random,string


class hier_sensor_turbofsk(gr.hier_block2):

    def __init__(self, T_bch=10, T_g=20, T_p=50, T_s=50, activation_rate=1, bs_slots=range(5), control='all', samp_rate=1e6):
        gr.hier_block2.__init__(
            self, "IoT Sensor emulator (TurboFSK PHY)",
            gr.io_signature(0, 0, 0),
            gr.io_signaturev(2, 2, [gr.sizeof_float*1, gr.sizeof_gr_complex*1]),
        )
        self.message_port_register_hier_in("DL")
        self.message_port_register_hier_in("BCN")

        ##################################################
        # Parameters
        ##################################################
        self.T_bch = T_bch
        self.T_g = T_g
        self.T_p = T_p
        self.T_s = T_s
        self.activation_rate = activation_rate
        self.bs_slots = bs_slots
        self.control = control
        self.samp_rate = samp_rate

        ##################################################
        # Variables
        ##################################################
        self.nbits = nbits = 16*8
        self.l = l = (64*32)+(1+(nbits+16)/8)*4*137+(1+(1+(nbits+16)/8)*4/5)*137

        ##################################################
        # Blocks
        ##################################################
        self.ephyl_turbofsk_tx_0 = ephyl.turbofsk_tx(nbits)
        self.ephyl_sn_scheduler_0_0 = ephyl.sn_scheduler(1, len(bs_slots), T_bch, T_g, T_s, T_p, 'corr_est',"packet_len2", int(samp_rate))
        self.ephyl_data_and_access_control_0 = ephyl.data_and_access_control(bs_slots,control,activation_rate,False)
        self.blocks_tagged_stream_to_pdu_0_0_0 = blocks.tagged_stream_to_pdu(blocks.complex_t, 'packet_len2')
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, l/4, "packet_len2")
        self.blocks_repack_bits_bb_2_2 = blocks.repack_bits_bb(8, 1, "packet_len", False, gr.GR_MSB_FIRST)
        self.blocks_pdu_to_tagged_stream_0_0 = blocks.pdu_to_tagged_stream(blocks.float_t, 'packet_len')
        self.blocks_pdu_to_tagged_stream_0 = blocks.pdu_to_tagged_stream(blocks.byte_t, 'packet_len')
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_vcc((128, ))
        self.blocks_float_to_complex_1 = blocks.float_to_complex(1)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0_0_0, 'pdus'), (self.ephyl_sn_scheduler_0_0, 'in'))
        self.msg_connect((self.ephyl_data_and_access_control_0, 'Data'), (self.blocks_pdu_to_tagged_stream_0, 'pdus'))
        self.msg_connect((self.ephyl_data_and_access_control_0, 'PER'), (self.blocks_pdu_to_tagged_stream_0_0, 'pdus'))
        self.msg_connect((self.ephyl_data_and_access_control_0, 'Array'), (self.ephyl_sn_scheduler_0_0, 'slot'))
        self.msg_connect((self.ephyl_sn_scheduler_0_0, 'busy'), (self.ephyl_data_and_access_control_0, 'busy'))
        self.msg_connect((self, 'DL'), (self.ephyl_data_and_access_control_0, 'DL'))
        self.msg_connect((self, 'BCN'), (self.ephyl_sn_scheduler_0_0, 'trig'))
        self.connect((self.blocks_float_to_complex_1, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self, 1))
        self.connect((self.blocks_pdu_to_tagged_stream_0, 0), (self.blocks_repack_bits_bb_2_2, 0))
        self.connect((self.blocks_pdu_to_tagged_stream_0_0, 0), (self, 0))
        self.connect((self.blocks_repack_bits_bb_2_2, 0), (self.ephyl_turbofsk_tx_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_tagged_stream_to_pdu_0_0_0, 0))
        self.connect((self.ephyl_sn_scheduler_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.ephyl_turbofsk_tx_0, 0), (self.blocks_float_to_complex_1, 0))
        self.connect((self.ephyl_turbofsk_tx_0, 1), (self.blocks_float_to_complex_1, 1))

    def get_T_bch(self):
        return self.T_bch

    def set_T_bch(self, T_bch):
        self.T_bch = T_bch

    def get_T_g(self):
        return self.T_g

    def set_T_g(self, T_g):
        self.T_g = T_g

    def get_T_p(self):
        return self.T_p

    def set_T_p(self, T_p):
        self.T_p = T_p

    def get_T_s(self):
        return self.T_s

    def set_T_s(self, T_s):
        self.T_s = T_s

    def get_activation_rate(self):
        return self.activation_rate

    def set_activation_rate(self, activation_rate):
        self.activation_rate = activation_rate

    def get_bs_slots(self):
        return self.bs_slots

    def set_bs_slots(self, bs_slots):
        self.bs_slots = bs_slots

    def get_control(self):
        return self.control

    def set_control(self, control):
        self.control = control

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_nbits(self):
        return self.nbits

    def set_nbits(self, nbits):
        self.nbits = nbits
        self.set_l((64*32)+(1+(self.nbits+16)/8)*4*137+(1+(1+(self.nbits+16)/8)*4/5)*137)

    def get_l(self):
        return self.l

    def set_l(self, l):
        self.l = l
        self.blocks_stream_to_tagged_stream_0.set_packet_len(self.l/4)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(self.l/4)
