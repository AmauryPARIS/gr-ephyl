#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2022 gr-ephyl author.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr, gr_unittest
from gnuradio import blocks
import ephyl_swig as ephyl
import numpy as np

# Method
LOW, HIGH, FIRST, LAST = 0, 1, 2, 3

class qa_select_m_in_n (gr_unittest.TestCase):

    def setUp (self):
        self.tb = gr.top_block ()

    def tearDown (self):
        self.tb = None

    def test_001_first_sample (self):
        M, N = 64, 80
        src_data = np.arange(2*N) + 1j * np.arange(2*N)
        expected_result = np.arange(2*M) + 1j * np.arange(2*M)

        src = blocks.vector_source_c(src_data, False, 1, [])
        # slct = ephyl.select_m_in_n(choice = FIRST, m = M, n = N, offset = 0)
        dst = blocks.vector_sink_c()
        print("#### !!!! ####")
        # self.tb.connect(src, slct)
        self.tb.connect(src, dst)
        self.tb.start()
        self.tb.wait()
        self.tb.stop()
        result_data = dst.data()
        # check data

        self.assertTupleEqual(tuple(result_data), tuple(expected_result))


if __name__ == '__main__':
    gr_unittest.run(qa_select_m_in_n, "qa_select_m_in_n.xml")
