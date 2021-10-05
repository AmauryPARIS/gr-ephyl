# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: IoT Sensor emulator
# Author: Othmane Oubejja
# Generated: Thu Feb  6 12:08:20 2020
##################################################

from gnuradio import blocks
from gnuradio import digital
from gnuradio import fec
from gnuradio import fft
from gnuradio import gr
from gnuradio.fft import window
from gnuradio.filter import firdes
import ephyl
import math, sys, numpy as np, random,string


class hier_sensor(gr.hier_block2):

    def __init__(self, M=64, N=1, T_bch=10, T_g=20, T_p=50, T_s=50, activation_rate=1, bs_slots=range(5), control='all', log=True, samp_rate=1e6):
        gr.hier_block2.__init__(
            self, "IoT Sensor emulator",
            gr.io_signature(0, 0, 0),
            gr.io_signaturev(2, 2, [gr.sizeof_float*1, gr.sizeof_gr_complex*1]),
        )
        self.message_port_register_hier_in("DL")

        ##################################################
        # Parameters
        ##################################################
        self.M = M
        self.N = N
        self.T_bch = T_bch
        self.T_g = T_g
        self.T_p = T_p
        self.T_s = T_s
        self.activation_rate = activation_rate
        self.bs_slots = bs_slots
        self.control = control
        self.log = log
        self.samp_rate = samp_rate

        ##################################################
        # Variables
        ##################################################
        self.rate = rate = 2
        self.polys = polys = [79,109]
        self.k = k = 7
        self.MTU = MTU = 1500
        self.puncpat = puncpat = 11
        self.hdr_format = hdr_format = digital.header_format_default(digital.packet_utils.default_access_code, 0)
        self.frame_size = frame_size = 12000


        self.enc_cc = enc_cc = fec.cc_encoder_make(MTU*8, k, rate, (polys), 0, fec.CC_STREAMING, False)

        self.cp_ratio = cp_ratio = 0.25

        self.constel = constel = digital.constellation_qpsk().base()


        ##################################################
        # Blocks
        ##################################################
        self.fft_vxx_0_0_0 = fft.fft_vcc(M, False, (), True, 1)
        self.fec_extended_tagged_encoder_0 = fec.extended_tagged_encoder(encoder_obj_list=enc_cc, puncpat='11', lentagname='packet_len', mtu=MTU)
        self.ephyl_sn_scheduler_0_0 = ephyl.sn_scheduler(0, len(bs_slots), T_bch, T_g, T_s, T_p, 'corr_est',"packet_len2", int(samp_rate))
        self.ephyl_data_and_access_control_0 = ephyl.data_and_access_control(bs_slots,control,activation_rate,log)
        self.digital_protocol_formatter_bb_0 = digital.protocol_formatter_bb(hdr_format, 'packet_len')
        self.digital_ofdm_cyclic_prefixer_0 = digital.ofdm_cyclic_prefixer(M, M+M/4, 0, '')
        self.digital_diff_encoder_bb_0 = digital.diff_encoder_bb(2)
        self.digital_chunks_to_symbols_xx_0 = digital.chunks_to_symbols_bc((constel.points()), 2)
        self.blocks_vector_source_x_0 = blocks.vector_source_c([0]*(M-1), True, 1, [])
        self.blocks_tagged_stream_to_pdu_0_0_0 = blocks.tagged_stream_to_pdu(blocks.complex_t, 'packet_len2')
        self.blocks_tagged_stream_mux_0 = blocks.tagged_stream_mux(gr.sizeof_char*1, 'packet_len', 0)
        self.blocks_tag_gate_0 = blocks.tag_gate(gr.sizeof_float * 1, False)
        self.blocks_sub_xx_0_0 = blocks.sub_ff(1)
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, M)
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, int(M*(1+cp_ratio))*2*8, "packet_len2")
        self.blocks_stream_mux_0 = blocks.stream_mux(gr.sizeof_gr_complex*1, (1, M-1))
        self.blocks_repack_bits_bb_2_2 = blocks.repack_bits_bb(8, 1, "packet_len", False, gr.GR_MSB_FIRST)
        self.blocks_repack_bits_bb_0_0 = blocks.repack_bits_bb(1, 8, 'packet_len', True, gr.GR_MSB_FIRST)
        self.blocks_repack_bits_bb_0 = blocks.repack_bits_bb(8, 1, 'packet_len', False, gr.GR_MSB_FIRST)
        self.blocks_pdu_to_tagged_stream_0_0 = blocks.pdu_to_tagged_stream(blocks.float_t, 'packet_len')
        self.blocks_pdu_to_tagged_stream_0 = blocks.pdu_to_tagged_stream(blocks.byte_t, 'packet_len')
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_float*1, 1)
        self.blocks_complex_to_arg_0 = blocks.complex_to_arg(1)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0_0_0, 'pdus'), (self.ephyl_sn_scheduler_0_0, 'in'))
        self.msg_connect((self.ephyl_data_and_access_control_0, 'Data'), (self.blocks_pdu_to_tagged_stream_0, 'pdus'))
        self.msg_connect((self.ephyl_data_and_access_control_0, 'PER'), (self.blocks_pdu_to_tagged_stream_0_0, 'pdus'))
        self.msg_connect((self.ephyl_data_and_access_control_0, 'Array'), (self.ephyl_sn_scheduler_0_0, 'slot'))
        self.msg_connect((self.ephyl_sn_scheduler_0_0, 'busy'), (self.ephyl_data_and_access_control_0, 'busy'))
        self.msg_connect((self, 'DL'), (self.ephyl_data_and_access_control_0, 'DL'))
        self.msg_connect((self, 'DL'), (self.ephyl_sn_scheduler_0_0, 'trig'))
        self.connect((self.blocks_complex_to_arg_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.blocks_complex_to_arg_0, 0), (self.blocks_tag_gate_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_sub_xx_0_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_stream_mux_0, 0))
        self.connect((self.blocks_pdu_to_tagged_stream_0, 0), (self.blocks_repack_bits_bb_0, 0))
        self.connect((self.blocks_pdu_to_tagged_stream_0_0, 0), (self, 0))
        self.connect((self.blocks_repack_bits_bb_0, 0), (self.fec_extended_tagged_encoder_0, 0))
        self.connect((self.blocks_repack_bits_bb_0_0, 0), (self.blocks_tagged_stream_mux_0, 1))
        self.connect((self.blocks_repack_bits_bb_0_0, 0), (self.digital_protocol_formatter_bb_0, 0))
        self.connect((self.blocks_repack_bits_bb_2_2, 0), (self.digital_diff_encoder_bb_0, 0))
        self.connect((self.blocks_stream_mux_0, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_tagged_stream_to_pdu_0_0_0, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.fft_vxx_0_0_0, 0))
        self.connect((self.blocks_sub_xx_0_0, 0), (self.blocks_float_to_complex_0, 1))
        self.connect((self.blocks_sub_xx_0_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_tag_gate_0, 0), (self.blocks_sub_xx_0_0, 1))
        self.connect((self.blocks_tagged_stream_mux_0, 0), (self.blocks_repack_bits_bb_2_2, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_stream_mux_0, 1))
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self.blocks_complex_to_arg_0, 0))
        self.connect((self.digital_diff_encoder_bb_0, 0), (self.digital_chunks_to_symbols_xx_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.digital_protocol_formatter_bb_0, 0), (self.blocks_tagged_stream_mux_0, 0))
        self.connect((self.ephyl_sn_scheduler_0_0, 0), (self, 1))
        self.connect((self.fec_extended_tagged_encoder_0, 0), (self.blocks_repack_bits_bb_0_0, 0))
        self.connect((self.fft_vxx_0_0_0, 0), (self.digital_ofdm_cyclic_prefixer_0, 0))

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.blocks_vector_source_x_0.set_data([0]*(self.M-1), [])
        self.blocks_stream_to_tagged_stream_0.set_packet_len(int(self.M*(1+self.cp_ratio))*2*8)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(int(self.M*(1+self.cp_ratio))*2*8)

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

    def get_log(self):
        return self.log

    def set_log(self, log):
        self.log = log

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

    def get_hdr_format(self):
        return self.hdr_format

    def set_hdr_format(self, hdr_format):
        self.hdr_format = hdr_format

    def get_frame_size(self):
        return self.frame_size

    def set_frame_size(self, frame_size):
        self.frame_size = frame_size

    def get_enc_cc(self):
        return self.enc_cc

    def set_enc_cc(self, enc_cc):
        self.enc_cc = enc_cc

    def get_cp_ratio(self):
        return self.cp_ratio

    def set_cp_ratio(self, cp_ratio):
        self.cp_ratio = cp_ratio
        self.blocks_stream_to_tagged_stream_0.set_packet_len(int(self.M*(1+self.cp_ratio))*2*8)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(int(self.M*(1+self.cp_ratio))*2*8)

    def get_constel(self):
        return self.constel

    def set_constel(self, constel):
        self.constel = constel
