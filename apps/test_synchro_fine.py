#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Test de re-synchronisation fine
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

from PyQt4 import Qt
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import fec
from gnuradio import fft
from gnuradio import gr
from gnuradio import qtgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from optparse import OptionParser
import ephyl
import math, sys, numpy as np, random
import pmt
import sip
import sys
from gnuradio import qtgui


class test_synchro_fine(gr.top_block, Qt.QWidget):

    def __init__(self, M=64, N=1, T_bch=200, T_g=20, T_p=200, T_s=150, UHD=True, bs_slots=range(10), cp_ratio=0.25, debug_log=False, exit_frame=1000, list_sensor=["A","B"], power_tresh_detection=5, samp_rate=1e6):
        gr.top_block.__init__(self, "Test de re-synchronisation fine")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Test de re-synchronisation fine")
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

        self.settings = Qt.QSettings("GNU Radio", "test_synchro_fine")
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
        self.UHD = UHD
        self.bs_slots = bs_slots
        self.cp_ratio = cp_ratio
        self.debug_log = debug_log
        self.exit_frame = exit_frame
        self.list_sensor = list_sensor
        self.power_tresh_detection = power_tresh_detection
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


        self.constel = constel = digital.constellation_qpsk().base()


        ##################################################
        # Blocks
        ##################################################
        self.qtgui_time_sink_x_0 = qtgui.time_sink_c(
        	1024, #size
        	samp_rate, #samp_rate
        	"", #name
        	1 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(-1, True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)

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

        for i in xrange(2):
            if len(labels[i]) == 0:
                if(i % 2 == 0):
                    self.qtgui_time_sink_x_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.fft_vxx_0 = fft.fft_vcc(M, True, (), True, 1)
        self.fec_extended_tagged_decoder_1 = self.fec_extended_tagged_decoder_1 = fec_extended_tagged_decoder_1 = fec.extended_tagged_decoder(decoder_obj_list=dec_cc, ann=None, puncpat='11', integration_period=10000, lentagname='burst', mtu=MTU)
        self.ephyl_tag_2_msg_char_0_0 = ephyl.tag_2_msg_char('PUSCH')
        self.ephyl_tag_2_msg_char_0 = ephyl.tag_2_msg_char("FRAME")
        self.digital_map_bb_0 = digital.map_bb(([-1, 1]))
        self.digital_diff_decoder_bb_0 = digital.diff_decoder_bb(2)
        self.digital_costas_loop_cc_0 = digital.costas_loop_cc(2*3.14/100, 2, False)
        self.digital_correlate_access_code_xx_ts_1 = digital.correlate_access_code_bb_ts(digital.packet_utils.default_access_code,
          20, 'burst')
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(constel)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, M)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_tagged_stream_to_pdu_0_0 = blocks.tagged_stream_to_pdu(blocks.byte_t, 'burst')
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, M)
        self.blocks_repack_bits_bb_1 = blocks.repack_bits_bb(1, 8, 'burst', True, gr.GR_MSB_FIRST)
        self.blocks_message_debug_0 = blocks.message_debug()
        self.blocks_keep_one_in_n_1 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, M*2)
        self.blocks_keep_m_in_n_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, M, int(M*(1+cp_ratio)), int(cp_ratio*M))
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, '/root/BS_carrier_complex_2_32b', False)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_char_to_float_1 = blocks.char_to_float(1, 1)



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_tagged_stream_to_pdu_0_0, 'pdus'), (self.blocks_message_debug_0, 'print'))
        self.msg_connect((self.ephyl_tag_2_msg_char_0, 'slot_msg'), (self.blocks_message_debug_0, 'print'))
        self.msg_connect((self.ephyl_tag_2_msg_char_0_0, 'slot_msg'), (self.blocks_message_debug_0, 'print'))
        self.connect((self.blocks_char_to_float_1, 0), (self.fec_extended_tagged_decoder_1, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_keep_m_in_n_0, 0), (self.digital_costas_loop_cc_0, 0))
        self.connect((self.blocks_keep_one_in_n_1, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.blocks_repack_bits_bb_1, 0), (self.blocks_tagged_stream_to_pdu_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.blocks_keep_m_in_n_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_keep_one_in_n_1, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.digital_diff_decoder_bb_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.ephyl_tag_2_msg_char_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.ephyl_tag_2_msg_char_0_0, 0))
        self.connect((self.digital_correlate_access_code_xx_ts_1, 0), (self.digital_map_bb_0, 0))
        self.connect((self.digital_costas_loop_cc_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.digital_diff_decoder_bb_0, 0), (self.digital_correlate_access_code_xx_ts_1, 0))
        self.connect((self.digital_map_bb_0, 0), (self.blocks_char_to_float_1, 0))
        self.connect((self.fec_extended_tagged_decoder_1, 0), (self.blocks_repack_bits_bb_1, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_vector_to_stream_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "test_synchro_fine")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

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

    def get_cp_ratio(self):
        return self.cp_ratio

    def set_cp_ratio(self, cp_ratio):
        self.cp_ratio = cp_ratio
        self.blocks_keep_m_in_n_0.set_offset(int(self.cp_ratio*self.M))
        self.blocks_keep_m_in_n_0.set_n(int(self.M*(1+self.cp_ratio)))

    def get_debug_log(self):
        return self.debug_log

    def set_debug_log(self, debug_log):
        self.debug_log = debug_log

    def get_exit_frame(self):
        return self.exit_frame

    def set_exit_frame(self, exit_frame):
        self.exit_frame = exit_frame

    def get_list_sensor(self):
        return self.list_sensor

    def set_list_sensor(self, list_sensor):
        self.list_sensor = list_sensor

    def get_power_tresh_detection(self):
        return self.power_tresh_detection

    def set_power_tresh_detection(self, power_tresh_detection):
        self.power_tresh_detection = power_tresh_detection

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)

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

    def get_constel(self):
        return self.constel

    def set_constel(self, constel):
        self.constel = constel


def argument_parser():
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option)
    parser.add_option(
        "", "--exit-frame", dest="exit_frame", type="intx", default=1000,
        help="Set Exit Frame [default=%default]")
    parser.add_option(
        "", "--samp-rate", dest="samp_rate", type="eng_float", default=eng_notation.num_to_str(1e6),
        help="Set Sample rate [default=%default]")
    return parser


def main(top_block_cls=test_synchro_fine, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(exit_frame=options.exit_frame, samp_rate=options.samp_rate)
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
