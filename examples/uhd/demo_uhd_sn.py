#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Demo Uhd Sn
# Generated: Thu Feb  6 12:11:55 2020
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
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import qtgui
from gnuradio import uhd
from gnuradio import zeromq
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.qtgui import Range, RangeWidget
from hier_sensor import hier_sensor  # grc-generated hier_block
from optparse import OptionParser
import math, sys, numpy as np, random,string
import sip
import time
from gnuradio import qtgui


class demo_uhd_sn(gr.top_block, Qt.QWidget):

    def __init__(self, M=32, N=1, T_bch=200, T_g=20, T_p=300, T_s=150, bs_slots=range(10), control0='0:1', control1='8:9', control2='basic', control3='ucb', cp_ratio=0.25):
        gr.top_block.__init__(self, "Demo Uhd Sn")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Demo Uhd Sn")
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

        self.settings = Qt.QSettings("GNU Radio", "demo_uhd_sn")
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

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1000000
        self.gain = gain = 14
        self.freq = freq = 2450e6
        self.frame_len = frame_len = (T_bch+len(bs_slots)*(T_s+T_g)+T_p)/float(1000)
        self.bs_slots_0 = bs_slots_0 = bs_slots[:3]
        self.MTU = MTU = 1500

        ##################################################
        # Blocks
        ##################################################
        self._gain_range = Range(0, 25, 1, 14, 200)
        self._gain_win = RangeWidget(self._gain_range, self.set_gain, 'Absolute Gain', "counter_slider", float)
        self.top_layout.addWidget(self._gain_win)
        self.zeromq_pull_msg_source_0 = zeromq.pull_msg_source('tcp://mnode3:5556', 100)
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
        	",".join(('', "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0.set_center_freq(freq, 0)
        self.uhd_usrp_sink_0.set_gain(gain, 0)
        self.uhd_usrp_sink_0.set_antenna('TX/RX', 0)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
        	64, #size
        	samp_rate, #samp_rate
        	'Packet Error rate', #name
        	4 #number of inputs
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

        labels = [control0, control1, control2, control3, '',
                  '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
                  1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
                  "magenta", "yellow", "dark red", "dark green", "blue"]
        styles = [1, 2, 1, 1, 1,
                  1, 1, 1, 1, 1]
        markers = [0, 8, 3, 2, -1,
                   -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in xrange(4):
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
        self.hier_sensor_0_2 = hier_sensor(
            M=M,
            N=1,
            T_bch=T_bch,
            T_g=T_g,
            T_p=T_p,
            T_s=T_s,
            activation_rate=1,
            bs_slots=bs_slots,
            control=control1,
            log=True,
            samp_rate=samp_rate,
        )
        self.hier_sensor_0_1 = hier_sensor(
            M=M,
            N=1,
            T_bch=T_bch,
            T_g=T_g,
            T_p=T_p,
            T_s=T_s,
            activation_rate=1,
            bs_slots=bs_slots,
            control=control3,
            log=True,
            samp_rate=samp_rate,
        )
        self.hier_sensor_0_0 = hier_sensor(
            M=M,
            N=1,
            T_bch=T_bch,
            T_g=T_g,
            T_p=T_p,
            T_s=T_s,
            activation_rate=1,
            bs_slots=bs_slots,
            control=control2,
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
            activation_rate=1,
            bs_slots=bs_slots,
            control=control0,
            log=True,
            samp_rate=samp_rate,
        )
        self.blocks_null_sink_1 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_message_debug_0 = blocks.message_debug()
        self.blocks_add_xx_0 = blocks.add_vcc(1)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.zeromq_pull_msg_source_0, 'out'), (self.blocks_message_debug_0, 'print'))
        self.msg_connect((self.zeromq_pull_msg_source_0, 'out'), (self.hier_sensor_0, 'DL'))
        self.msg_connect((self.zeromq_pull_msg_source_0, 'out'), (self.hier_sensor_0_0, 'DL'))
        self.msg_connect((self.zeromq_pull_msg_source_0, 'out'), (self.hier_sensor_0_1, 'DL'))
        self.msg_connect((self.zeromq_pull_msg_source_0, 'out'), (self.hier_sensor_0_2, 'DL'))
        self.connect((self.blocks_add_xx_0, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.hier_sensor_0, 1), (self.blocks_add_xx_0, 0))
        self.connect((self.hier_sensor_0, 0), (self.blocks_null_sink_1, 0))
        self.connect((self.hier_sensor_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.hier_sensor_0_0, 1), (self.blocks_add_xx_0, 2))
        self.connect((self.hier_sensor_0_0, 0), (self.qtgui_time_sink_x_0, 2))
        self.connect((self.hier_sensor_0_1, 1), (self.blocks_add_xx_0, 3))
        self.connect((self.hier_sensor_0_1, 0), (self.qtgui_time_sink_x_0, 3))
        self.connect((self.hier_sensor_0_2, 1), (self.blocks_add_xx_0, 1))
        self.connect((self.hier_sensor_0_2, 0), (self.qtgui_time_sink_x_0, 1))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "demo_uhd_sn")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

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

    def get_bs_slots(self):
        return self.bs_slots

    def set_bs_slots(self, bs_slots):
        self.bs_slots = bs_slots
        self.hier_sensor_0_2.set_bs_slots(self.bs_slots)
        self.hier_sensor_0_1.set_bs_slots(self.bs_slots)
        self.hier_sensor_0_0.set_bs_slots(self.bs_slots)
        self.hier_sensor_0.set_bs_slots(self.bs_slots)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))
        self.set_bs_slots_0(self.bs_slots[:3])

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
        self.hier_sensor_0_0.set_control(self.control2)

    def get_control3(self):
        return self.control3

    def set_control3(self, control3):
        self.control3 = control3
        self.hier_sensor_0_1.set_control(self.control3)

    def get_cp_ratio(self):
        return self.cp_ratio

    def set_cp_ratio(self, cp_ratio):
        self.cp_ratio = cp_ratio

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)
        self.hier_sensor_0_2.set_samp_rate(self.samp_rate)
        self.hier_sensor_0_1.set_samp_rate(self.samp_rate)
        self.hier_sensor_0_0.set_samp_rate(self.samp_rate)
        self.hier_sensor_0.set_samp_rate(self.samp_rate)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.uhd_usrp_sink_0.set_gain(self.gain, 0)


    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.uhd_usrp_sink_0.set_center_freq(self.freq, 0)

    def get_frame_len(self):
        return self.frame_len

    def set_frame_len(self, frame_len):
        self.frame_len = frame_len

    def get_bs_slots_0(self):
        return self.bs_slots_0

    def set_bs_slots_0(self, bs_slots_0):
        self.bs_slots_0 = bs_slots_0

    def get_MTU(self):
        return self.MTU

    def set_MTU(self, MTU):
        self.MTU = MTU


def argument_parser():
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option)
    parser.add_option(
        "", "--control0", dest="control0", type="string", default='0:1',
        help="Set Control [default=%default]")
    parser.add_option(
        "", "--control1", dest="control1", type="string", default='8:9',
        help="Set Control [default=%default]")
    parser.add_option(
        "", "--control2", dest="control2", type="string", default='basic',
        help="Set Control [default=%default]")
    parser.add_option(
        "", "--control3", dest="control3", type="string", default='ucb',
        help="Set Control [default=%default]")
    return parser


def main(top_block_cls=demo_uhd_sn, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(control0=options.control0, control1=options.control1, control2=options.control2, control3=options.control3)
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
