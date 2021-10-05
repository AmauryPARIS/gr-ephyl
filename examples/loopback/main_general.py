#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Main General
# Generated: Thu Feb  6 13:59:07 2020
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import channels
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import fec
from gnuradio import fft
from gnuradio import gr
from gnuradio import qtgui
from gnuradio import zeromq
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import ephyl
import math, sys, numpy as np, random, string
import sip
import sys
from gnuradio import qtgui


class main_general(gr.top_block, Qt.QWidget):

    def __init__(self, M=32, N=1, T_bch=50, T_g=40, T_p=200, T_s=100, bs_slots=range(6), control='0:2:4', cp_ratio=0.25, frame_size=12000, hdr_format=digital.header_format_default(digital.packet_utils.default_access_code, 0), modulation=4, puncpat='11'):
        gr.top_block.__init__(self, "Main General")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Main General")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "main_general")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

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
        self.frame_size = frame_size
        self.hdr_format = hdr_format
        self.modulation = modulation
        self.puncpat = puncpat

        ##################################################
        # Variables
        ##################################################
        self.rate = rate = 2
        self.polys = polys = [79,109]
        self.k = k = 7
        self.MTU = MTU = 1500
        self.time_offset = time_offset = 1
        self.sps = sps = 2
        self.samp_rate = samp_rate = int(1e6)
        self.phase = phase = 0
        self.noise_voltage = noise_voltage = 0
        self.nfilts = nfilts = 32
        self.freq_offset = freq_offset = 0
        self.frame_len = frame_len = (T_bch+len(bs_slots)*(T_s+T_g)+T_p)/float(1000)


        self.enc_cc = enc_cc = fec.cc_encoder_make(MTU*8, k, rate, (polys), 0, fec.CC_STREAMING, False)

        self.eb = eb = 0.22


        self.dec_cc = dec_cc = fec.cc_decoder.make(MTU*8, k, rate, (polys), 0, -1, fec.CC_STREAMING, False)


        self.constel = constel = digital.constellation_qpsk().base()


        ##################################################
        # Blocks
        ##################################################
        self._time_offset_range = Range(0.995, 1.005, 0.00001, 1, 200)
        self._time_offset_win = RangeWidget(self._time_offset_range, self.set_time_offset, 'Timing Offset', "counter_slider", float)
        self.top_layout.addWidget(self._time_offset_win)
        self._phase_range = Range(0, 2*3.14, .01, 0, 200)
        self._phase_win = RangeWidget(self._phase_range, self.set_phase, 'taps phase', "counter_slider", float)
        self.top_layout.addWidget(self._phase_win)
        self._noise_voltage_range = Range(0, 10, .001, 0, 200)
        self._noise_voltage_win = RangeWidget(self._noise_voltage_range, self.set_noise_voltage, 'Noise Amplitude', "counter_slider", float)
        self.top_layout.addWidget(self._noise_voltage_win)
        self._freq_offset_range = Range(-.1, .1, .00001, 0, 200)
        self._freq_offset_win = RangeWidget(self._freq_offset_range, self.set_freq_offset, 'Frequency Offset (Multiples of Sub-carrier spacing)', "counter_slider", float)
        self.top_layout.addWidget(self._freq_offset_win)
        self.zeromq_push_msg_sink_0 = zeromq.push_msg_sink('tcp://127.0.0.1:5556', 100)
        self.zeromq_pull_msg_source_0 = zeromq.pull_msg_source('tcp://127.0.0.1:5556', 100)
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0 = qtgui.time_sink_c(
        	int(samp_rate*frame_len)/int(2*M*(1+cp_ratio)), #size
        	samp_rate/int(2*M*(1+cp_ratio)), #samp_rate
        	'BS', #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_y_axis(-3, 3)

        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.3, 0, 0, 'BCH')
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.enable_grid(True)
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.enable_control_panel(False)

        if not True:
          self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.disable_legend()

        labels = ['res', 'ref', '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in xrange(2*1):
            if len(labels[i]) == 0:
                if(i % 2 == 0):
                    self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
        	64, #size
        	samp_rate, #samp_rate
        	'Packet Error rate', #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(0, 1)

        self.qtgui_time_sink_x_0.set_y_label('PER', "")

        self.qtgui_time_sink_x_0.enable_tags(-1, False)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)

        if not True:
          self.qtgui_time_sink_x_0.disable_legend()

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in xrange(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.fft_vxx_0_0_0 = fft.fft_vcc(M, False, (), True, 1)
        self.fft_vxx_0 = fft.fft_vcc(M, True, (), True, 1)
        self.fec_extended_tagged_encoder_0 = fec.extended_tagged_encoder(encoder_obj_list=enc_cc, puncpat='11', lentagname='packet_len', mtu=MTU)
        self.fec_extended_tagged_decoder_1 = self.fec_extended_tagged_decoder_1 = fec_extended_tagged_decoder_1 = fec.extended_tagged_decoder(decoder_obj_list=dec_cc, ann=None, puncpat='11', integration_period=10000, lentagname='burst', mtu=MTU)
        self.ephyl_tag_2_msg_char_0_0 = ephyl.tag_2_msg_char('PUSCH')
        self.ephyl_tag_2_msg_char_0 = ephyl.tag_2_msg_char("FRAME")
        self.ephyl_sn_scheduler_0 = ephyl.sn_scheduler(0, len(bs_slots), T_bch, T_g, T_s, T_p, 'corr_est',"packet_len2", samp_rate)
        self.ephyl_msg_mux_0 = ephyl.msg_mux()
        self.ephyl_data_and_access_control_0 = ephyl.data_and_access_control(bs_slots,control,1,False)
        self.ephyl_bs_scheduler_0 = ephyl.bs_scheduler(len(bs_slots), T_bch, T_g, T_s, T_p, samp_rate, False, 0)
        self.digital_protocol_formatter_bb_0 = digital.protocol_formatter_bb(hdr_format, 'packet_len')
        self.digital_ofdm_cyclic_prefixer_0 = digital.ofdm_cyclic_prefixer(M, M+M/4, 0, '')
        self.digital_map_bb_0 = digital.map_bb(([-1, 1]))
        self.digital_diff_encoder_bb_0 = digital.diff_encoder_bb(2)
        self.digital_diff_decoder_bb_0 = digital.diff_decoder_bb(2)
        self.digital_costas_loop_cc_0 = digital.costas_loop_cc(2*3.14/100, 2, False)
        self.digital_correlate_access_code_xx_ts_1 = digital.correlate_access_code_bb_ts(digital.packet_utils.default_access_code,
          20, 'burst')
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(constel)
        self.digital_chunks_to_symbols_xx_0 = digital.chunks_to_symbols_bc((constel.points()), 2)
        self.channels_channel_model_0 = channels.channel_model(
        	noise_voltage=noise_voltage,
        	frequency_offset=freq_offset,
        	epsilon=time_offset,
        	taps=(complex(np.cos(phase),np.sin(phase)), ),
        	noise_seed=0,
        	block_tags=False
        )
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, M)
        self.blocks_vector_source_x_0 = blocks.vector_source_c([0]*(M-1), True, 1, [])
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_tagged_stream_to_pdu_0_0_0 = blocks.tagged_stream_to_pdu(blocks.complex_t, 'packet_len2')
        self.blocks_tagged_stream_to_pdu_0_0 = blocks.tagged_stream_to_pdu(blocks.byte_t, 'burst')
        self.blocks_tagged_stream_mux_0 = blocks.tagged_stream_mux(gr.sizeof_char*1, 'packet_len', 0)
        self.blocks_tag_gate_0_0 = blocks.tag_gate(gr.sizeof_gr_complex * 1, False)
        self.blocks_tag_gate_0 = blocks.tag_gate(gr.sizeof_float * 1, False)
        self.blocks_sub_xx_0_0 = blocks.sub_ff(1)
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, M)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, M)
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, int(M*(1+cp_ratio))*2*8, "packet_len2")
        self.blocks_stream_mux_0 = blocks.stream_mux(gr.sizeof_gr_complex*1, (1, M-1))
        self.blocks_repack_bits_bb_2_2 = blocks.repack_bits_bb(8, 1, "packet_len", False, gr.GR_MSB_FIRST)
        self.blocks_repack_bits_bb_1 = blocks.repack_bits_bb(1, 8, 'burst', True, gr.GR_MSB_FIRST)
        self.blocks_repack_bits_bb_0_0 = blocks.repack_bits_bb(1, 8, 'packet_len', True, gr.GR_MSB_FIRST)
        self.blocks_repack_bits_bb_0 = blocks.repack_bits_bb(8, 1, 'packet_len', False, gr.GR_MSB_FIRST)
        self.blocks_pdu_to_tagged_stream_0_0 = blocks.pdu_to_tagged_stream(blocks.float_t, 'packet_len')
        self.blocks_pdu_to_tagged_stream_0 = blocks.pdu_to_tagged_stream(blocks.byte_t, 'packet_len')
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((1.0/M, ))
        self.blocks_message_debug_2 = blocks.message_debug()
        self.blocks_keep_one_in_n_1 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, M*2)
        self.blocks_keep_m_in_n_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, M, int(M*(1+cp_ratio)), int(cp_ratio*M))
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_float*1, 1)
        self.blocks_complex_to_arg_0 = blocks.complex_to_arg(1)
        self.blocks_char_to_float_1 = blocks.char_to_float(1, 1)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0_0, 'pdus'), (self.ephyl_msg_mux_0, 'data'))
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0_0_0, 'pdus'), (self.ephyl_sn_scheduler_0, 'in'))
        self.msg_connect((self.ephyl_bs_scheduler_0, 'bcn'), (self.zeromq_push_msg_sink_0, 'in'))
        self.msg_connect((self.ephyl_data_and_access_control_0, 'Data'), (self.blocks_pdu_to_tagged_stream_0, 'pdus'))
        self.msg_connect((self.ephyl_data_and_access_control_0, 'PER'), (self.blocks_pdu_to_tagged_stream_0_0, 'pdus'))
        self.msg_connect((self.ephyl_data_and_access_control_0, 'Array'), (self.ephyl_sn_scheduler_0, 'slot'))
        self.msg_connect((self.ephyl_msg_mux_0, 'final_msg'), (self.blocks_message_debug_2, 'print'))
        self.msg_connect((self.ephyl_msg_mux_0, 'final_msg'), (self.zeromq_push_msg_sink_0, 'in'))
        self.msg_connect((self.ephyl_sn_scheduler_0, 'busy'), (self.ephyl_data_and_access_control_0, 'busy'))
        self.msg_connect((self.ephyl_tag_2_msg_char_0, 'slot_msg'), (self.ephyl_msg_mux_0, 'frame_n'))
        self.msg_connect((self.ephyl_tag_2_msg_char_0_0, 'slot_msg'), (self.ephyl_msg_mux_0, 'slot_n'))
        self.msg_connect((self.zeromq_pull_msg_source_0, 'out'), (self.ephyl_data_and_access_control_0, 'DL'))
        self.msg_connect((self.zeromq_pull_msg_source_0, 'out'), (self.ephyl_sn_scheduler_0, 'trig'))
        self.connect((self.blocks_char_to_float_1, 0), (self.fec_extended_tagged_decoder_1, 0))
        self.connect((self.blocks_complex_to_arg_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.blocks_complex_to_arg_0, 0), (self.blocks_tag_gate_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_sub_xx_0_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_stream_mux_0, 0))
        self.connect((self.blocks_keep_m_in_n_0, 0), (self.digital_costas_loop_cc_0, 0))
        self.connect((self.blocks_keep_one_in_n_1, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0, 0))
        self.connect((self.blocks_pdu_to_tagged_stream_0, 0), (self.blocks_repack_bits_bb_0, 0))
        self.connect((self.blocks_pdu_to_tagged_stream_0_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.blocks_pdu_to_tagged_stream_0_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_repack_bits_bb_0, 0), (self.fec_extended_tagged_encoder_0, 0))
        self.connect((self.blocks_repack_bits_bb_0_0, 0), (self.blocks_tagged_stream_mux_0, 1))
        self.connect((self.blocks_repack_bits_bb_0_0, 0), (self.digital_protocol_formatter_bb_0, 0))
        self.connect((self.blocks_repack_bits_bb_1, 0), (self.blocks_tagged_stream_to_pdu_0_0, 0))
        self.connect((self.blocks_repack_bits_bb_2_2, 0), (self.digital_diff_encoder_bb_0, 0))
        self.connect((self.blocks_stream_mux_0, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_tagged_stream_to_pdu_0_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.fft_vxx_0_0_0, 0))
        self.connect((self.blocks_sub_xx_0_0, 0), (self.blocks_float_to_complex_0, 1))
        self.connect((self.blocks_sub_xx_0_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_tag_gate_0, 0), (self.blocks_sub_xx_0_0, 1))
        self.connect((self.blocks_tag_gate_0_0, 0), (self.ephyl_bs_scheduler_0, 0))
        self.connect((self.blocks_tagged_stream_mux_0, 0), (self.blocks_repack_bits_bb_2_2, 0))
        self.connect((self.blocks_throttle_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_stream_mux_0, 1))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_keep_one_in_n_1, 0))
        self.connect((self.channels_channel_model_0, 0), (self.blocks_tag_gate_0_0, 0))
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self.blocks_complex_to_arg_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.digital_diff_decoder_bb_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.ephyl_tag_2_msg_char_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.ephyl_tag_2_msg_char_0_0, 0))
        self.connect((self.digital_correlate_access_code_xx_ts_1, 0), (self.digital_map_bb_0, 0))
        self.connect((self.digital_costas_loop_cc_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.digital_diff_decoder_bb_0, 0), (self.digital_correlate_access_code_xx_ts_1, 0))
        self.connect((self.digital_diff_encoder_bb_0, 0), (self.digital_chunks_to_symbols_xx_0, 0))
        self.connect((self.digital_map_bb_0, 0), (self.blocks_char_to_float_1, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.digital_protocol_formatter_bb_0, 0), (self.blocks_tagged_stream_mux_0, 0))
        self.connect((self.ephyl_bs_scheduler_0, 0), (self.blocks_keep_m_in_n_0, 0))
        self.connect((self.ephyl_sn_scheduler_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.fec_extended_tagged_decoder_1, 0), (self.blocks_repack_bits_bb_1, 0))
        self.connect((self.fec_extended_tagged_encoder_0, 0), (self.blocks_repack_bits_bb_0_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.fft_vxx_0_0_0, 0), (self.digital_ofdm_cyclic_prefixer_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "main_general")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_samp_rate(self.samp_rate/int(2*self.M*(1+self.cp_ratio)))
        self.blocks_vector_source_x_0.set_data([0]*(self.M-1), [])
        self.blocks_stream_to_tagged_stream_0.set_packet_len(int(self.M*(1+self.cp_ratio))*2*8)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(int(self.M*(1+self.cp_ratio))*2*8)
        self.blocks_multiply_const_vxx_0.set_k((1.0/self.M, ))
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
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_g(self):
        return self.T_g

    def set_T_g(self, T_g):
        self.T_g = T_g
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_p(self):
        return self.T_p

    def set_T_p(self, T_p):
        self.T_p = T_p
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_s(self):
        return self.T_s

    def set_T_s(self, T_s):
        self.T_s = T_s
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_bs_slots(self):
        return self.bs_slots

    def set_bs_slots(self, bs_slots):
        self.bs_slots = bs_slots
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_control(self):
        return self.control

    def set_control(self, control):
        self.control = control

    def get_cp_ratio(self):
        return self.cp_ratio

    def set_cp_ratio(self, cp_ratio):
        self.cp_ratio = cp_ratio
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_samp_rate(self.samp_rate/int(2*self.M*(1+self.cp_ratio)))
        self.blocks_stream_to_tagged_stream_0.set_packet_len(int(self.M*(1+self.cp_ratio))*2*8)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(int(self.M*(1+self.cp_ratio))*2*8)
        self.blocks_keep_m_in_n_0.set_offset(int(self.cp_ratio*self.M))
        self.blocks_keep_m_in_n_0.set_n(int(self.M*(1+self.cp_ratio)))

    def get_frame_size(self):
        return self.frame_size

    def set_frame_size(self, frame_size):
        self.frame_size = frame_size

    def get_hdr_format(self):
        return self.hdr_format

    def set_hdr_format(self, hdr_format):
        self.hdr_format = hdr_format

    def get_modulation(self):
        return self.modulation

    def set_modulation(self, modulation):
        self.modulation = modulation

    def get_puncpat(self):
        return self.puncpat

    def set_puncpat(self, puncpat):
        self.puncpat = puncpat

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

    def get_time_offset(self):
        return self.time_offset

    def set_time_offset(self, time_offset):
        self.time_offset = time_offset
        self.channels_channel_model_0.set_timing_offset(self.time_offset)

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0.set_samp_rate(self.samp_rate/int(2*self.M*(1+self.cp_ratio)))
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_phase(self):
        return self.phase

    def set_phase(self, phase):
        self.phase = phase
        self.channels_channel_model_0.set_taps((complex(np.cos(self.phase),np.sin(self.phase)), ))

    def get_noise_voltage(self):
        return self.noise_voltage

    def set_noise_voltage(self, noise_voltage):
        self.noise_voltage = noise_voltage
        self.channels_channel_model_0.set_noise_voltage(self.noise_voltage)

    def get_nfilts(self):
        return self.nfilts

    def set_nfilts(self, nfilts):
        self.nfilts = nfilts

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.channels_channel_model_0.set_frequency_offset(self.freq_offset)

    def get_frame_len(self):
        return self.frame_len

    def set_frame_len(self, frame_len):
        self.frame_len = frame_len

    def get_enc_cc(self):
        return self.enc_cc

    def set_enc_cc(self, enc_cc):
        self.enc_cc = enc_cc

    def get_eb(self):
        return self.eb

    def set_eb(self, eb):
        self.eb = eb

    def get_dec_cc(self):
        return self.dec_cc

    def set_dec_cc(self, dec_cc):
        self.dec_cc = dec_cc

    def get_constel(self):
        return self.constel

    def set_constel(self, constel):
        self.constel = constel


def argument_parser():
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option)
    parser.add_option(
        "", "--control", dest="control", type="string", default='0:2:4',
        help="Set Access control [default=%default]")
    parser.add_option(
        "", "--frame-size", dest="frame_size", type="intx", default=12000,
        help="Set Frame Size [default=%default]")
    parser.add_option(
        "", "--puncpat", dest="puncpat", type="string", default='11',
        help="Set puncpat [default=%default]")
    return parser


def main(top_block_cls=main_general, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(control=options.control, frame_size=options.frame_size, puncpat=options.puncpat)
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
