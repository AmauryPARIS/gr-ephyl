# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: IoT BS Emulator
# Author: Othmane Oubejja
# Generated: Thu Jan 30 10:55:06 2020
##################################################

from gnuradio import blocks
from gnuradio import digital
from gnuradio import fec
from gnuradio import fft
from gnuradio import gr
from gnuradio.fft import window
from gnuradio.filter import firdes
import ephyl
import math, sys, numpy as np, random


class hier_bs(gr.hier_block2):

    def __init__(self, M=64, N=1, T_bch=200, T_g=20, T_p=200, T_s=150, UHD=True, bs_slots=range(10), exit_frame=0, samp_rate=1e6):
        gr.hier_block2.__init__(
            self, "IoT BS Emulator",
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
            gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
        )
        self.message_port_register_hier_out("DL")
        self.message_port_register_hier_out("BCH")

        ##################################################
        # Parameters
        ##################################################
        self.M = M
        self.N = N
        self.T_bch = T_bch
        self.T_g = T_g
        self.T_p = T_p
        self.T_s = T_s
        self.UHD = UHD
        self.bs_slots = bs_slots
        self.exit_frame = exit_frame
        self.samp_rate = samp_rate

        ##################################################
        # Variables
        ##################################################
        self.rate = rate = 2
        self.polys = polys = [79,109]
        self.k = k = 7
        self.MTU = MTU = 1500
        self.puncpat = puncpat = 11
        self.frame_size = frame_size = 12000


        self.dec_cc = dec_cc = fec.cc_decoder.make(MTU*8, k, rate, (polys), 0, -1, fec.CC_STREAMING, False)

        self.cp_ratio = cp_ratio = 0.25

        self.constel = constel = digital.constellation_qpsk().base()


        ##################################################
        # Blocks
        ##################################################
        self.fft_vxx_0 = fft.fft_vcc(M, True, (), True, 1)
        self.fec_extended_tagged_decoder_1 = self.fec_extended_tagged_decoder_1 = fec_extended_tagged_decoder_1 = fec.extended_tagged_decoder(decoder_obj_list=dec_cc, ann=None, puncpat='11', integration_period=10000, lentagname='burst', mtu=MTU)
        self.ephyl_tag_2_msg_char_0_0 = ephyl.tag_2_msg_char('PUSCH')
        self.ephyl_tag_2_msg_char_0 = ephyl.tag_2_msg_char("FRAME")
        self.ephyl_msg_mux_0 = ephyl.msg_mux()
        self.ephyl_bs_scheduler_0 = ephyl.bs_scheduler(len(bs_slots), T_bch, T_g, T_s, T_p, int(samp_rate), UHD, exit_frame)
        self.digital_map_bb_0 = digital.map_bb(([-1, 1]))
        self.digital_diff_decoder_bb_0 = digital.diff_decoder_bb(2)
        self.digital_costas_loop_cc_0 = digital.costas_loop_cc(2*3.14/100, 2, False)
        self.digital_correlate_access_code_xx_ts_1 = digital.correlate_access_code_bb_ts(digital.packet_utils.default_access_code,
          20, 'burst')
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(constel)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, M)
        self.blocks_tagged_stream_to_pdu_0_0 = blocks.tagged_stream_to_pdu(blocks.byte_t, 'burst')
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, M)
        self.blocks_repack_bits_bb_1 = blocks.repack_bits_bb(1, 8, 'burst', True, gr.GR_MSB_FIRST)
        self.blocks_keep_one_in_n_1 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, M*2)
        self.blocks_keep_m_in_n_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, M, int(M*(1+cp_ratio)), int(cp_ratio*M))
        self.blocks_char_to_float_1 = blocks.char_to_float(1, 1)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0_0, 'pdus'), (self.ephyl_msg_mux_0, 'data'))
        self.msg_connect((self.ephyl_bs_scheduler_0, 'bcn'), (self, 'BCH'))
        self.msg_connect((self.ephyl_msg_mux_0, 'final_msg'), (self, 'DL'))
        self.msg_connect((self.ephyl_tag_2_msg_char_0, 'slot_msg'), (self.ephyl_msg_mux_0, 'frame_n'))
        self.msg_connect((self.ephyl_tag_2_msg_char_0_0, 'slot_msg'), (self.ephyl_msg_mux_0, 'slot_n'))
        self.connect((self.blocks_char_to_float_1, 0), (self.fec_extended_tagged_decoder_1, 0))
        self.connect((self.blocks_keep_m_in_n_0, 0), (self.digital_costas_loop_cc_0, 0))
        self.connect((self.blocks_keep_one_in_n_1, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.blocks_keep_one_in_n_1, 0), (self, 0))
        self.connect((self.blocks_repack_bits_bb_1, 0), (self.blocks_tagged_stream_to_pdu_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_keep_one_in_n_1, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.digital_diff_decoder_bb_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.ephyl_tag_2_msg_char_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.ephyl_tag_2_msg_char_0_0, 0))
        self.connect((self.digital_correlate_access_code_xx_ts_1, 0), (self.digital_map_bb_0, 0))
        self.connect((self.digital_costas_loop_cc_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.digital_diff_decoder_bb_0, 0), (self.digital_correlate_access_code_xx_ts_1, 0))
        self.connect((self.digital_map_bb_0, 0), (self.blocks_char_to_float_1, 0))
        self.connect((self.ephyl_bs_scheduler_0, 0), (self.blocks_keep_m_in_n_0, 0))
        self.connect((self.fec_extended_tagged_decoder_1, 0), (self.blocks_repack_bits_bb_1, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self, 0), (self.ephyl_bs_scheduler_0, 0))

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.blocks_keep_one_in_n_1.set_n(self.M*2)
        self.blocks_keep_m_in_n_0.set_offset(int(self.cp_ratio*self.M))
        self.blocks_keep_m_in_n_0.set_m(self.M)
        self.blocks_keep_m_in_n_0.set_n(int(self.M*(1+self.cp_ratio)))

    def get_N(self):
        return self.N

    def set_N(self, N):
        self.N = N

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

    def get_exit_frame(self):
        return self.exit_frame

    def set_exit_frame(self, exit_frame):
        self.exit_frame = exit_frame

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_rate(self):
        return self.rate

    def set_rate(self, rate):
        self.rate = rate

    def get_polys(self):
        return self.polys

    def set_polys(self, polys):
        self.polys = polys

    def get_k(self):
        return self.k

    def set_k(self, k):
        self.k = k

    def get_MTU(self):
        return self.MTU

    def set_MTU(self, MTU):
        self.MTU = MTU

    def get_puncpat(self):
        return self.puncpat

    def set_puncpat(self, puncpat):
        self.puncpat = puncpat

    def get_frame_size(self):
        return self.frame_size

    def set_frame_size(self, frame_size):
        self.frame_size = frame_size

    def get_dec_cc(self):
        return self.dec_cc

    def set_dec_cc(self, dec_cc):
        self.dec_cc = dec_cc

    def get_cp_ratio(self):
        return self.cp_ratio

    def set_cp_ratio(self, cp_ratio):
        self.cp_ratio = cp_ratio
        self.blocks_keep_m_in_n_0.set_offset(int(self.cp_ratio*self.M))
        self.blocks_keep_m_in_n_0.set_n(int(self.M*(1+self.cp_ratio)))

    def get_constel(self):
        return self.constel

    def set_constel(self, constel):
        self.constel = constel
