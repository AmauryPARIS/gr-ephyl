#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Main Turbo
# Generated: Wed Jan 29 13:44:20 2020
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
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import qtgui
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from optparse import OptionParser
import ephyl
import math, sys, numpy as np, random, string
import pmt
import sip
import sys
import time
from gnuradio import qtgui


class main_turbo(gr.top_block, Qt.QWidget):

    def __init__(self, T_bch=200, T_g=20, T_p=500, T_s=1000, bs_slots=range(1), control='none'):
        gr.top_block.__init__(self, "Main Turbo")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Main Turbo")
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

        self.settings = Qt.QSettings("GNU Radio", "main_turbo")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())

        ##################################################
        # Parameters
        ##################################################
        self.T_bch = T_bch
        self.T_g = T_g
        self.T_p = T_p
        self.T_s = T_s
        self.bs_slots = bs_slots
        self.control = control

        ##################################################
        # Variables
        ##################################################
        self.nbits = nbits = 16*8
        self.time_offset = time_offset = 1
        self.samp_rate = samp_rate = int(1e6)
        self.phase = phase = 0
        self.noise_voltage = noise_voltage = 0
        self.n = n = 35
        self.l = l = (64*32)+(1+(nbits+16)/8)*4*137+(1+(1+(nbits+16)/8)*4/5)*137
        self.gain = gain = 9
        self.freq_offset = freq_offset = 0
        self.freq = freq = 2450e6
        self.frame_len = frame_len = (T_bch+len(bs_slots)*(T_s+T_g)+T_p)/float(1000)

        ##################################################
        # Blocks
        ##################################################
        self._n_range = Range(0, 50, .1, 35, 200)
        self._n_win = RangeWidget(self._n_range, self.set_n, "n", "counter_slider", float)
        self.top_layout.addWidget(self._n_win)
        self._gain_range = Range(0, 16, 1, 9, 200)
        self._gain_win = RangeWidget(self._gain_range, self.set_gain, 'Absolute Gain', "counter_slider", float)
        self.top_layout.addWidget(self._gain_win)
        self.uhd_usrp_source_0 = uhd.usrp_source(
        	",".join(('addr=192.168.10.3', "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_center_freq(freq, 0)
        self.uhd_usrp_source_0.set_gain(gain, 0)
        self.uhd_usrp_source_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_sink_0_1 = uhd.usrp_sink(
        	",".join(('addr=192.168.10.2', "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_sink_0_1.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0_1.set_center_freq(freq, 0)
        self.uhd_usrp_sink_0_1.set_gain(gain, 0)
        self.uhd_usrp_sink_0_1.set_antenna('TX/RX', 0)
        self._time_offset_range = Range(0.995, 1.005, 0.00001, 1, 200)
        self._time_offset_win = RangeWidget(self._time_offset_range, self.set_time_offset, 'Timing Offset', "counter_slider", float)
        self.top_layout.addWidget(self._time_offset_win)
        self.qtgui_time_sink_x_1_0 = qtgui.time_sink_f(
        	16*8, #size
        	samp_rate, #samp_rate
        	"", #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_1_0.set_update_time(0.10)
        self.qtgui_time_sink_x_1_0.set_y_axis(0, 140)

        self.qtgui_time_sink_x_1_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_1_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_1_0.set_trigger_mode(qtgui.TRIG_MODE_AUTO, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, 'packet_len')
        self.qtgui_time_sink_x_1_0.enable_autoscale(True)
        self.qtgui_time_sink_x_1_0.enable_grid(True)
        self.qtgui_time_sink_x_1_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_1_0.enable_control_panel(False)

        if not True:
          self.qtgui_time_sink_x_1_0.disable_legend()

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
                self.qtgui_time_sink_x_1_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_1_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_1_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_1_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_1_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_1_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_1_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_1_0_win = sip.wrapinstance(self.qtgui_time_sink_x_1_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_1_0_win)
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0 = qtgui.time_sink_c(
        	int(samp_rate*frame_len), #size
        	samp_rate, #samp_rate
        	'BS', #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.set_y_axis(-40, 40)

        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.1, 0, 0, 'BCH')
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.enable_grid(True)
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.enable_control_panel(False)

        if not True:
          self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.disable_legend()

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
                    self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0_win)
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
        self._phase_range = Range(0, 2*3.14, .01, 0, 200)
        self._phase_win = RangeWidget(self._phase_range, self.set_phase, 'taps phase', "counter_slider", float)
        self.top_layout.addWidget(self._phase_win)
        self._noise_voltage_range = Range(0, 5, .01, 0, 200)
        self._noise_voltage_win = RangeWidget(self._noise_voltage_range, self.set_noise_voltage, 'Noise Amplitude', "counter_slider", float)
        self.top_layout.addWidget(self._noise_voltage_win)
        self._freq_offset_range = Range(-.1, .1, .00001, 0, 200)
        self._freq_offset_win = RangeWidget(self._freq_offset_range, self.set_freq_offset, 'Frequency Offset (Multiples of Sub-carrier spacing)', "counter_slider", float)
        self.top_layout.addWidget(self._freq_offset_win)
        self.ephyl_turbofsk_tx_0 = ephyl.turbofsk_tx(nbits)
        self.ephyl_turbofsk_rx_0 = ephyl.turbofsk_rx(n,nbits)
        self.ephyl_tag_2_msg_char_0_0 = ephyl.tag_2_msg_char('PUSCH')
        self.ephyl_tag_2_msg_char_0 = ephyl.tag_2_msg_char("FRAME")
        self.ephyl_sn_scheduler_0 = ephyl.sn_scheduler(1, len(bs_slots), T_bch, T_g, T_s, T_p, 'corr_est',"packet_len2", samp_rate)
        self.ephyl_msg_mux_0 = ephyl.msg_mux()
        self.ephyl_data_and_access_control_0 = ephyl.data_and_access_control(bs_slots,control,1,False)
        self.ephyl_bs_scheduler_0 = ephyl.bs_scheduler(len(bs_slots), T_bch, T_g, T_s, T_p, samp_rate, True, 0)
        self.blocks_tagged_stream_to_pdu_0_0_0 = blocks.tagged_stream_to_pdu(blocks.complex_t, 'packet_len2')
        self.blocks_tagged_stream_to_pdu_0_0 = blocks.tagged_stream_to_pdu(blocks.byte_t, 'packet_len')
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, l/4, "packet_len2")
        self.blocks_socket_pdu_0_0_0 = blocks.socket_pdu("UDP_CLIENT", '127.0.0.1', '52002', 10000, True)
        self.blocks_socket_pdu_0_0 = blocks.socket_pdu("UDP_SERVER", '', '52002', 10000, True)
        self.blocks_repack_bits_bb_2_2 = blocks.repack_bits_bb(8, 1, "packet_len", False, gr.GR_MSB_FIRST)
        self.blocks_repack_bits_bb_1 = blocks.repack_bits_bb(1, 8, 'packet_len', True, gr.GR_MSB_FIRST)
        self.blocks_pdu_to_tagged_stream_0_0 = blocks.pdu_to_tagged_stream(blocks.float_t, 'packet_len')
        self.blocks_pdu_to_tagged_stream_0 = blocks.pdu_to_tagged_stream(blocks.byte_t, 'packet_len')
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_vcc((128, ))
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.cons(pmt.make_dict(), pmt.init_u8vector(1,[1])), .01)
        self.blocks_message_debug_2 = blocks.message_debug()
        self.blocks_float_to_complex_1 = blocks.float_to_complex(1)
        self.blocks_float_to_char_0 = blocks.float_to_char(1, 1)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.blocks_char_to_float_0_0 = blocks.char_to_float(1, 1)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.blocks_socket_pdu_0_0_0, 'pdus'))
        self.msg_connect((self.blocks_socket_pdu_0_0_0, 'pdus'), (self.ephyl_data_and_access_control_0, 'DL'))
        self.msg_connect((self.blocks_socket_pdu_0_0_0, 'pdus'), (self.ephyl_sn_scheduler_0, 'trig'))
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0_0, 'pdus'), (self.ephyl_msg_mux_0, 'data'))
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0_0_0, 'pdus'), (self.ephyl_sn_scheduler_0, 'in'))
        self.msg_connect((self.ephyl_bs_scheduler_0, 'bcn'), (self.blocks_socket_pdu_0_0, 'pdus'))
        self.msg_connect((self.ephyl_data_and_access_control_0, 'Data'), (self.blocks_pdu_to_tagged_stream_0, 'pdus'))
        self.msg_connect((self.ephyl_data_and_access_control_0, 'PER'), (self.blocks_pdu_to_tagged_stream_0_0, 'pdus'))
        self.msg_connect((self.ephyl_data_and_access_control_0, 'Array'), (self.ephyl_sn_scheduler_0, 'slot'))
        self.msg_connect((self.ephyl_msg_mux_0, 'final_msg'), (self.blocks_message_debug_2, 'print'))
        self.msg_connect((self.ephyl_msg_mux_0, 'final_msg'), (self.blocks_socket_pdu_0_0, 'pdus'))
        self.msg_connect((self.ephyl_sn_scheduler_0, 'busy'), (self.ephyl_data_and_access_control_0, 'busy'))
        self.msg_connect((self.ephyl_tag_2_msg_char_0, 'slot_msg'), (self.ephyl_msg_mux_0, 'frame_n'))
        self.msg_connect((self.ephyl_tag_2_msg_char_0_0, 'slot_msg'), (self.ephyl_msg_mux_0, 'slot_n'))
        self.connect((self.blocks_char_to_float_0_0, 0), (self.qtgui_time_sink_x_1_0, 0))
        self.connect((self.blocks_complex_to_float_0, 0), (self.blocks_float_to_char_0, 0))
        self.connect((self.blocks_complex_to_float_0, 1), (self.ephyl_turbofsk_rx_0, 1))
        self.connect((self.blocks_complex_to_float_0, 0), (self.ephyl_turbofsk_rx_0, 0))
        self.connect((self.blocks_float_to_char_0, 0), (self.ephyl_tag_2_msg_char_0, 0))
        self.connect((self.blocks_float_to_char_0, 0), (self.ephyl_tag_2_msg_char_0_0, 0))
        self.connect((self.blocks_float_to_complex_1, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.uhd_usrp_sink_0_1, 0))
        self.connect((self.blocks_pdu_to_tagged_stream_0, 0), (self.blocks_repack_bits_bb_2_2, 0))
        self.connect((self.blocks_pdu_to_tagged_stream_0_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.blocks_pdu_to_tagged_stream_0_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_repack_bits_bb_1, 0), (self.blocks_tagged_stream_to_pdu_0_0, 0))
        self.connect((self.blocks_repack_bits_bb_2_2, 0), (self.ephyl_turbofsk_tx_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_tagged_stream_to_pdu_0_0_0, 0))
        self.connect((self.ephyl_bs_scheduler_0, 0), (self.blocks_complex_to_float_0, 0))
        self.connect((self.ephyl_bs_scheduler_0, 0), (self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0, 0))
        self.connect((self.ephyl_sn_scheduler_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.ephyl_turbofsk_rx_0, 0), (self.blocks_char_to_float_0_0, 0))
        self.connect((self.ephyl_turbofsk_rx_0, 0), (self.blocks_repack_bits_bb_1, 0))
        self.connect((self.ephyl_turbofsk_tx_0, 0), (self.blocks_float_to_complex_1, 0))
        self.connect((self.ephyl_turbofsk_tx_0, 1), (self.blocks_float_to_complex_1, 1))
        self.connect((self.uhd_usrp_source_0, 0), (self.ephyl_bs_scheduler_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "main_turbo")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

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

    def get_nbits(self):
        return self.nbits

    def set_nbits(self, nbits):
        self.nbits = nbits
        self.set_l((64*32)+(1+(self.nbits+16)/8)*4*137+(1+(1+(self.nbits+16)/8)*4/5)*137)

    def get_time_offset(self):
        return self.time_offset

    def set_time_offset(self, time_offset):
        self.time_offset = time_offset

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_sink_0_1.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_1_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_0_0_1_0_0_0_0_0_0_0_0_0_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)

    def get_phase(self):
        return self.phase

    def set_phase(self, phase):
        self.phase = phase

    def get_noise_voltage(self):
        return self.noise_voltage

    def set_noise_voltage(self, noise_voltage):
        self.noise_voltage = noise_voltage

    def get_n(self):
        return self.n

    def set_n(self, n):
        self.n = n
        self.ephyl_turbofsk_rx_0.set_Noise(self.n)

    def get_l(self):
        return self.l

    def set_l(self, l):
        self.l = l
        self.blocks_stream_to_tagged_stream_0.set_packet_len(self.l/4)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(self.l/4)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.uhd_usrp_source_0.set_gain(self.gain, 0)

        self.uhd_usrp_sink_0_1.set_gain(self.gain, 0)


    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_source_0.set_center_freq(self.freq, 0)
        self.uhd_usrp_sink_0_1.set_center_freq(self.freq, 0)

    def get_frame_len(self):
        return self.frame_len

    def set_frame_len(self, frame_len):
        self.frame_len = frame_len


def argument_parser():
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option)
    parser.add_option(
        "", "--control", dest="control", type="string", default='none',
        help="Set Access control [default=%default]")
    return parser


def main(top_block_cls=main_turbo, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(control=options.control)
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
