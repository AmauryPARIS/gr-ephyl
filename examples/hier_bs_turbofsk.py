# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: IoT BS Emulator (TurboFSK PHY)
# Author: Othmane Oubejja, CEA leti
# Generated: Wed Jan 29 17:14:16 2020
##################################################

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import ephyl
import math, sys, numpy as np, random


class hier_bs_turbofsk(gr.hier_block2):

    def __init__(self, T_bch=10, T_g=20, T_p=50, T_s=50, UHD=False, bs_slots=range(5), n=35, samp_rate=1e6):
        gr.hier_block2.__init__(
            self, "IoT BS Emulator (TurboFSK PHY)",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )
        self.message_port_register_hier_out("DL")
        self.message_port_register_hier_out("BCH")

        ##################################################
        # Parameters
        ##################################################
        self.T_bch = T_bch
        self.T_g = T_g
        self.T_p = T_p
        self.T_s = T_s
        self.UHD = UHD
        self.bs_slots = bs_slots
        self.n = n
        self.samp_rate = samp_rate

        ##################################################
        # Variables
        ##################################################
        self.nbits = nbits = 16*8

        ##################################################
        # Blocks
        ##################################################
        self.ephyl_turbofsk_rx_0 = ephyl.turbofsk_rx(n,nbits)
        self.ephyl_tag_2_msg_char_0_0 = ephyl.tag_2_msg_char('PUSCH')
        self.ephyl_tag_2_msg_char_0 = ephyl.tag_2_msg_char("FRAME")
        self.ephyl_msg_mux_0 = ephyl.msg_mux()
        self.ephyl_bs_scheduler_0 = ephyl.bs_scheduler(len(bs_slots), T_bch, T_g, T_s, T_p, int(samp_rate), UHD, 0)
        self.blocks_tagged_stream_to_pdu_0_0 = blocks.tagged_stream_to_pdu(blocks.byte_t, 'packet_len')
        self.blocks_repack_bits_bb_1 = blocks.repack_bits_bb(1, 8, 'packet_len', True, gr.GR_MSB_FIRST)
        self.blocks_float_to_char_0 = blocks.float_to_char(1, 1)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0_0, 'pdus'), (self.ephyl_msg_mux_0, 'data'))
        self.msg_connect((self.ephyl_bs_scheduler_0, 'bcn'), (self, 'BCH'))
        self.msg_connect((self.ephyl_msg_mux_0, 'final_msg'), (self, 'DL'))
        self.msg_connect((self.ephyl_tag_2_msg_char_0, 'slot_msg'), (self.ephyl_msg_mux_0, 'frame_n'))
        self.msg_connect((self.ephyl_tag_2_msg_char_0_0, 'slot_msg'), (self.ephyl_msg_mux_0, 'slot_n'))
        self.connect((self.blocks_complex_to_float_0, 1), (self.blocks_float_to_char_0, 0))
        self.connect((self.blocks_complex_to_float_0, 1), (self.ephyl_turbofsk_rx_0, 1))
        self.connect((self.blocks_complex_to_float_0, 0), (self.ephyl_turbofsk_rx_0, 0))
        self.connect((self.blocks_float_to_char_0, 0), (self.ephyl_tag_2_msg_char_0, 0))
        self.connect((self.blocks_float_to_char_0, 0), (self.ephyl_tag_2_msg_char_0_0, 0))
        self.connect((self.blocks_repack_bits_bb_1, 0), (self.blocks_tagged_stream_to_pdu_0_0, 0))
        self.connect((self.ephyl_bs_scheduler_0, 0), (self.blocks_complex_to_float_0, 0))
        self.connect((self.ephyl_bs_scheduler_0, 0), (self, 0))
        self.connect((self.ephyl_turbofsk_rx_0, 0), (self.blocks_repack_bits_bb_1, 0))
        self.connect((self, 0), (self.ephyl_bs_scheduler_0, 0))

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

    def get_UHD(self):
        return self.UHD

    def set_UHD(self, UHD):
        self.UHD = UHD

    def get_bs_slots(self):
        return self.bs_slots

    def set_bs_slots(self, bs_slots):
        self.bs_slots = bs_slots

    def get_n(self):
        return self.n

    def set_n(self, n):
        self.n = n
        self.ephyl_turbofsk_rx_0.set_Noise(self.n)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_nbits(self):
        return self.nbits

    def set_nbits(self, nbits):
        self.nbits = nbits
