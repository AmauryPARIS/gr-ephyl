#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# GNU Radio version: 3.7.14.0
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
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from hier_bs import hier_bs  # grc-generated hier_block
from hier_sensor import hier_sensor  # grc-generated hier_block
from optparse import OptionParser
import ephyl
import math, sys, numpy as np, random,string
import pmt
from gnuradio import qtgui


class top_block(gr.top_block, Qt.QWidget):

    def __init__(self, M=32, N=1, bs_slots=range(3), cp_ratio=0.25, T_g=100, T_bch=100, T_s=100, T_p=250):
        gr.top_block.__init__(self, "Top Block")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Top Block")
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

        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Parameters
        ##################################################
        self.M = M
        self.N = N
        self.bs_slots = bs_slots
        self.cp_ratio = cp_ratio
        self.T_g = T_g
        self.T_bch = T_bch
        self.T_s = T_s
        self.T_p = T_p

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1000000
        self.log = log = True
        self.gain = gain = 25
        self.freq = freq = 2450e6
        self.frame_len = frame_len = (T_bch+len(bs_slots)*(T_s+T_g)+T_p)/float(1000)
        self.MTU = MTU = 10000

        ##################################################
        # Blocks
        ##################################################
        self.hier_sensor_0_0 = hier_sensor(
            M=M,
            N=1,
            T_bch=T_bch,
            T_g=T_g,
            T_p=T_p,
            T_s=T_s,
            bs_slots=bs_slots,
            control="2",
            log=log,
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
            control="0",
            log=log,
            samp_rate=samp_rate,
        )
        self.hier_bs_0 = hier_bs(
            M=M,
            N=N,
            T_bch=T_bch,
            T_g=T_g,
            T_p=T_p,
            T_s=T_s,
            UHD=True,
            bs_slots=bs_slots,
            exit_frame=1000,
            samp_rate=samp_rate,
        )
        self.ephyl_easy_upper_0 = ephyl.easy_upper()
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_socket_pdu_0_0 = blocks.socket_pdu("UDP_CLIENT", '127.0.0.1', '52002', MTU, True)
        self.blocks_socket_pdu_0 = blocks.socket_pdu("UDP_SERVER", '', '52002', MTU, True)
        self.blocks_null_sink_1_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_1 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.cons(pmt.make_dict(), pmt.init_u8vector(1,[1])), .01)
        self.blocks_add_xx_0 = blocks.add_vcc(1)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.blocks_socket_pdu_0_0, 'pdus'))
        self.msg_connect((self.blocks_socket_pdu_0_0, 'pdus'), (self.hier_sensor_0, 'DL'))
        self.msg_connect((self.blocks_socket_pdu_0_0, 'pdus'), (self.hier_sensor_0_0, 'DL'))
        self.msg_connect((self.ephyl_easy_upper_0, 'inst'), (self.hier_sensor_0, 'Inst'))
        self.msg_connect((self.ephyl_easy_upper_0, 'inst'), (self.hier_sensor_0_0, 'Inst'))
        self.msg_connect((self.hier_bs_0, 'DL'), (self.blocks_socket_pdu_0, 'pdus'))
        self.msg_connect((self.hier_bs_0, 'BCH'), (self.blocks_socket_pdu_0, 'pdus'))
        self.msg_connect((self.hier_sensor_0, 'feedback'), (self.ephyl_easy_upper_0, 'feedback'))
        self.msg_connect((self.hier_sensor_0_0, 'feedback'), (self.ephyl_easy_upper_0, 'feedback'))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.hier_bs_0, 0))
        self.connect((self.hier_bs_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.hier_sensor_0, 1), (self.blocks_add_xx_0, 0))
        self.connect((self.hier_sensor_0, 0), (self.blocks_null_sink_1, 0))
        self.connect((self.hier_sensor_0_0, 1), (self.blocks_add_xx_0, 1))
        self.connect((self.hier_sensor_0_0, 0), (self.blocks_null_sink_1_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_M(self):
        return self.M

    def set_M(self, M):
        self.M = M
        self.hier_sensor_0_0.set_M(self.M)
        self.hier_sensor_0.set_M(self.M)
        self.hier_bs_0.set_M(self.M)

    def get_N(self):
        return self.N

    def set_N(self, N):
        self.N = N
        self.hier_bs_0.set_N(self.N)

    def get_bs_slots(self):
        return self.bs_slots

    def set_bs_slots(self, bs_slots):
        self.bs_slots = bs_slots
        self.hier_sensor_0_0.set_bs_slots(self.bs_slots)
        self.hier_sensor_0.set_bs_slots(self.bs_slots)
        self.hier_bs_0.set_bs_slots(self.bs_slots)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_cp_ratio(self):
        return self.cp_ratio

    def set_cp_ratio(self, cp_ratio):
        self.cp_ratio = cp_ratio

    def get_T_g(self):
        return self.T_g

    def set_T_g(self, T_g):
        self.T_g = T_g
        self.hier_sensor_0_0.set_T_g(self.T_g)
        self.hier_sensor_0.set_T_g(self.T_g)
        self.hier_bs_0.set_T_g(self.T_g)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_bch(self):
        return self.T_bch

    def set_T_bch(self, T_bch):
        self.T_bch = T_bch
        self.hier_sensor_0_0.set_T_bch(self.T_bch)
        self.hier_sensor_0.set_T_bch(self.T_bch)
        self.hier_bs_0.set_T_bch(self.T_bch)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_s(self):
        return self.T_s

    def set_T_s(self, T_s):
        self.T_s = T_s
        self.hier_sensor_0_0.set_T_s(self.T_s)
        self.hier_sensor_0.set_T_s(self.T_s)
        self.hier_bs_0.set_T_s(self.T_s)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_T_p(self):
        return self.T_p

    def set_T_p(self, T_p):
        self.T_p = T_p
        self.hier_sensor_0_0.set_T_p(self.T_p)
        self.hier_sensor_0.set_T_p(self.T_p)
        self.hier_bs_0.set_T_p(self.T_p)
        self.set_frame_len((self.T_bch+len(self.bs_slots)*(self.T_s+self.T_g)+self.T_p)/float(1000))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.hier_sensor_0_0.set_samp_rate(self.samp_rate)
        self.hier_sensor_0.set_samp_rate(self.samp_rate)
        self.hier_bs_0.set_samp_rate(self.samp_rate)
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

    def get_log(self):
        return self.log

    def set_log(self, log):
        self.log = log
        self.hier_sensor_0_0.set_log(self.log)
        self.hier_sensor_0.set_log(self.log)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq

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
        "", "--T-p", dest="T_p", type="intx", default=250,
        help="Set Proc duration (ms) [default=%default]")
    return parser


def main(top_block_cls=top_block, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(T_p=options.T_p)
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
