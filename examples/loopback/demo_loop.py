#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Demo Loop
# GNU Radio version: 3.7.13.5
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

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import channels
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from hier_bs import hier_bs  # grc-generated hier_block
from hier_sensor import hier_sensor  # grc-generated hier_block
from optparse import OptionParser
import ephyl
import math, sys, numpy as np, random,string
import pmt
import sip
from gnuradio import qtgui


class demo_loop(gr.top_block, Qt.QWidget):

    def __init__(self, M=32, N=1, T_bch=100, T_g=100, T_p=500, T_s=100, bs_slots=range(5), control0='random', control1='1:2', control2='5', control3='7', cp_ratio=0.25, list_sensor=["A","B"], power_tresh_detect=5):
        gr.top_block.__init__(self, "Demo Loop")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Demo Loop")
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

        self.settings = Qt.QSettings("GNU Radio", "demo_loop")
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
        self.control0 = control0
        self.control1 = control1
        self.control2 = control2
        self.control3 = control3
        self.cp_ratio = cp_ratio
        self.list_sensor = list_sensor
        self.power_tresh_detect = power_tresh_detect

        ##################################################
        # Variables
        ##################################################
        self.time_offset = time_offset = 1
        self.samp_rate = samp_rate = 1e6
        self.phase = phase = 0
        self.noise_voltage = noise_voltage = 0.25
        self.freq_offset = freq_offset = 0
        self.freq = freq = 2450e6
        self.frame_len = frame_len = (T_bch+len(bs_slots)*(T_s+T_g)+T_p)/float(1000)
        self.debug_log = debug_log = True
        self.MTU = MTU = 1500

        ##################################################
        # Blocks
        ##################################################
        self._time_offset_range = Range(0.995, 1.005, 0.00001, 1, 200)
        self._time_offset_win = RangeWidget(self._time_offset_range, self.set_time_offset, 'Timing Offset', "counter_slider", float)
        self.top_grid_layout.addWidget(self._time_offset_win)
        self._phase_range = Range(0, 2*3.14, .01, 0, 200)
        self._phase_win = RangeWidget(self._phase_range, self.set_phase, 'taps phase', "counter_slider", float)
        self.top_grid_layout.addWidget(self._phase_win)
        self._noise_voltage_range = Range(0, 10, .01, 0.25, 200)
        self._noise_voltage_win = RangeWidget(self._noise_voltage_range, self.set_noise_voltage, 'Noise Amplitude', "counter_slider", float)
        self.top_grid_layout.addWidget(self._noise_voltage_win)
        self._freq_offset_range = Range(-.1, .1, .00001, 0, 200)
        self._freq_offset_win = RangeWidget(self._freq_offset_range, self.set_freq_offset, 'Frequency Offset (Multiples of Sub-carrier spacing)', "counter_slider", float)
        self.top_grid_layout.addWidget(self._freq_offset_win)
        self.qtgui_time_sink_x_0_0_0_1_0_0 = qtgui.time_sink_f(
        	int(frame_len*samp_rate)/int(2*M*(1+cp_ratio)), #size
        	samp_rate/int(2*M*(1+cp_ratio)), #samp_rate
        	'BS IQ Frame', #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0_0_1_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_0_1_0_0.set_y_axis(-1, 400)

        self.qtgui_time_sink_x_0_0_0_1_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_0_1_0_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0_0_0_1_0_0.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, .9, 0, 0, 'BCH')
        self.qtgui_time_sink_x_0_0_0_1_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_0_1_0_0.enable_grid(True)
        self.qtgui_time_sink_x_0_0_0_1_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_0_1_0_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0_0_1_0_0.enable_stem_plot(False)

        if not True:
          self.qtgui_time_sink_x_0_0_0_1_0_0.disable_legend()

        labels = ['UL BS', 'UL SN', 'BCH BS', '', '',
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
                self.qtgui_time_sink_x_0_0_0_1_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0_0_1_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_0_1_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_0_1_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_0_1_0_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_0_0_1_0_0_win)
        self.hier_sensor_0_2 = hier_sensor(
            M=M,
            N=1,
            T_bch=T_bch,
            T_g=T_g,
            T_p=T_p,
            T_s=T_s,
            bs_slots=bs_slots,
            control=control1,
            debug_log=True,
            id_0="B",
            log=True,
            samp_rate=samp_rate,
        )
        self.hier_sensor_0 = hier_sensor(
            M=M,
            N=1,
            T_bch=T_bch,
            T_g=T_g,
            T_p=T_p,
            T_s=T_s,
            bs_slots=bs_slots,
            control=control0,
            debug_log=True,
            id_0="A",
            log=True,
            samp_rate=samp_rate,
        )
        self.hier_bs_0 = hier_bs(
            M=M,
            N=N,
            T_bch=T_bch,
            T_g=T_g,
            T_p=T_p,
            T_s=T_s,
            UHD=False,
            bs_slots=bs_slots,
            debug_log=True,
            exit_frame=600,
            list_sensor=["A","B"],
            power_tresh_detection=5,
            samp_rate=samp_rate,
        )
        self.ephyl_easy_upper_0_0 = ephyl.easy_upper(True, list_sensor, debug_log, bs_slots)
        self.ephyl_easy_upper_0 = ephyl.easy_upper(False, list_sensor, debug_log, bs_slots)
        self.channels_channel_model_0 = channels.channel_model(
        	noise_voltage=noise_voltage,
        	frequency_offset=freq_offset,
        	epsilon=time_offset,
        	taps=(complex(np.cos(phase),np.sin(phase)), ),
        	noise_seed=0,
        	block_tags=True
        )
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_socket_pdu_0_0 = blocks.socket_pdu("UDP_CLIENT", '127.0.0.1', '52002', MTU, True)
        self.blocks_socket_pdu_0 = blocks.socket_pdu("UDP_SERVER", '', '52002', MTU, True)
        self.blocks_null_sink_1_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_1 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.cons(pmt.make_dict(), pmt.init_u8vector(1,[1])), .01)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.blocks_add_xx_0_0 = blocks.add_vcc(1)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.blocks_socket_pdu_0_0, 'pdus'))
        self.msg_connect((self.blocks_socket_pdu_0_0, 'pdus'), (self.hier_sensor_0, 'DL'))
        self.msg_connect((self.blocks_socket_pdu_0_0, 'pdus'), (self.hier_sensor_0_2, 'DL'))
        self.msg_connect((self.ephyl_easy_upper_0, 'inst'), (self.hier_sensor_0, 'Inst'))
        self.msg_connect((self.ephyl_easy_upper_0, 'inst'), (self.hier_sensor_0_2, 'Inst'))
        self.msg_connect((self.ephyl_easy_upper_0_0, 'inst'), (self.hier_bs_0, 'inst'))
        self.msg_connect((self.hier_bs_0, 'BCH'), (self.blocks_socket_pdu_0, 'pdus'))
        self.msg_connect((self.hier_bs_0, 'DL'), (self.blocks_socket_pdu_0, 'pdus'))
        self.msg_connect((self.hier_bs_0, 'feedback'), (self.ephyl_easy_upper_0_0, 'feedback'))
        self.msg_connect((self.hier_bs_0, 'DLCCH'), (self.hier_sensor_0, 'DLCCH'))
        self.msg_connect((self.hier_bs_0, 'DLCCH'), (self.hier_sensor_0_2, 'DLCCH'))
        self.msg_connect((self.hier_sensor_0, 'feedback'), (self.ephyl_easy_upper_0, 'feedback'))
        self.msg_connect((self.hier_sensor_0, 'ULCCH'), (self.hier_bs_0, 'ULCCH'))
        self.msg_connect((self.hier_sensor_0_2, 'feedback'), (self.ephyl_easy_upper_0, 'feedback'))
        self.msg_connect((self.hier_sensor_0_2, 'ULCCH'), (self.hier_bs_0, 'ULCCH'))
        self.connect((self.blocks_add_xx_0_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.qtgui_time_sink_x_0_0_0_1_0_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.hier_bs_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.hier_bs_0, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.hier_sensor_0, 1), (self.blocks_add_xx_0_0, 0))
        self.connect((self.hier_sensor_0, 0), (self.blocks_null_sink_1, 0))
        self.connect((self.hier_sensor_0_2, 1), (self.blocks_add_xx_0_0, 1))
        self.connect((self.hier_sensor_0_2, 0), (self.blocks_null_sink_1_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "demo_loop")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.qtgui_time_sink_x_0_0_0_1_0_0.set_samp_rate(self.samp_rate/int(2*self.M*(1+self.cp_ratio)))
        self.hier_sensor_0_2.set_M(self.M)
        self.hier_sensor_0.set_M(self.M)
        self.hier_bs_0.set_M(self.M)

    def get_N(self):
        return self.N

    def set_N(self, N):
        self.N = N
        self.hier_bs_0.set_N(self.N)

    def get_T_bch(self):
        return self.T_bch

    def set_T_bch(self, T_bch):
        self.T_bch = T_bch
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))
        self.hier_sensor_0_2.set_T_bch(self.T_bch)
        self.hier_sensor_0.set_T_bch(self.T_bch)
        self.hier_bs_0.set_T_bch(self.T_bch)

    def get_T_g(self):
        return self.T_g

    def set_T_g(self, T_g):
        self.T_g = T_g
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))
        self.hier_sensor_0_2.set_T_g(self.T_g)
        self.hier_sensor_0.set_T_g(self.T_g)
        self.hier_bs_0.set_T_g(self.T_g)

    def get_T_p(self):
        return self.T_p

    def set_T_p(self, T_p):
        self.T_p = T_p
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))
        self.hier_sensor_0_2.set_T_p(self.T_p)
        self.hier_sensor_0.set_T_p(self.T_p)
        self.hier_bs_0.set_T_p(self.T_p)

    def get_T_s(self):
        return self.T_s

    def set_T_s(self, T_s):
        self.T_s = T_s
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))
        self.hier_sensor_0_2.set_T_s(self.T_s)
        self.hier_sensor_0.set_T_s(self.T_s)
        self.hier_bs_0.set_T_s(self.T_s)

    def get_bs_slots(self):
        return self.bs_slots

    def set_bs_slots(self, bs_slots):
        self.bs_slots = bs_slots
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))
        self.hier_sensor_0_2.set_bs_slots(self.bs_slots)
        self.hier_sensor_0.set_bs_slots(self.bs_slots)
        self.hier_bs_0.set_bs_slots(self.bs_slots)

    def get_control0(self):
        return self.control0

    def set_control0(self, control0):
        self.control0 = control0
        self.hier_sensor_0.set_control(self.control0)

    def get_control1(self):
        return self.control1

    def set_control1(self, control1):
        self.control1 = control1
        self.hier_sensor_0_2.set_control(self.control1)

    def get_control2(self):
        return self.control2

    def set_control2(self, control2):
        self.control2 = control2

    def get_control3(self):
        return self.control3

    def set_control3(self, control3):
        self.control3 = control3

    def get_cp_ratio(self):
        return self.cp_ratio

    def set_cp_ratio(self, cp_ratio):
        self.cp_ratio = cp_ratio
        self.qtgui_time_sink_x_0_0_0_1_0_0.set_samp_rate(self.samp_rate/int(2*self.M*(1+self.cp_ratio)))

    def get_list_sensor(self):
        return self.list_sensor

    def set_list_sensor(self, list_sensor):
        self.list_sensor = list_sensor

    def get_power_tresh_detect(self):
        return self.power_tresh_detect

    def set_power_tresh_detect(self, power_tresh_detect):
        self.power_tresh_detect = power_tresh_detect

    def get_time_offset(self):
        return self.time_offset

    def set_time_offset(self, time_offset):
        self.time_offset = time_offset
        self.channels_channel_model_0.set_timing_offset(self.time_offset)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_time_sink_x_0_0_0_1_0_0.set_samp_rate(self.samp_rate/int(2*self.M*(1+self.cp_ratio)))
        self.hier_sensor_0_2.set_samp_rate(self.samp_rate)
        self.hier_sensor_0.set_samp_rate(self.samp_rate)
        self.hier_bs_0.set_samp_rate(self.samp_rate)
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

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.channels_channel_model_0.set_frequency_offset(self.freq_offset)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq

    def get_frame_len(self):
        return self.frame_len

    def set_frame_len(self, frame_len):
        self.frame_len = frame_len

    def get_debug_log(self):
        return self.debug_log

    def set_debug_log(self, debug_log):
        self.debug_log = debug_log

    def get_MTU(self):
        return self.MTU

    def set_MTU(self, MTU):
        self.MTU = MTU


def argument_parser():
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option)
    parser.add_option(
        "", "--T-p", dest="T_p", type="intx", default=500,
        help="Set Proc duration (ms) [default=%default]")
    parser.add_option(
        "", "--control0", dest="control0", type="string", default='random',
        help="Set Control [default=%default]")
    parser.add_option(
        "", "--control1", dest="control1", type="string", default='1:2',
        help="Set Control [default=%default]")
    parser.add_option(
        "", "--control2", dest="control2", type="string", default='5',
        help="Set Control [default=%default]")
    parser.add_option(
        "", "--control3", dest="control3", type="string", default='7',
        help="Set Control [default=%default]")
    return parser


def main(top_block_cls=demo_loop, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(T_p=options.T_p, control0=options.control0, control1=options.control1, control2=options.control2, control3=options.control3)
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
