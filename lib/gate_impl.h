/* -*- c++ -*- */
/* 
 * Copyright 2022 gr-ephyl author.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_EPHYL_GATE_IMPL_H
#define INCLUDED_EPHYL_GATE_IMPL_H

#include <ephyl/gate.h>
#include <iostream>
#include <fstream>
using namespace std;

namespace gr {
  namespace ephyl {

    class gate_impl : public gate
    {
     private:
      double m_power_thresh;             /// Threshold value in dB to set the start and end of the signal 
      int32_t m_symb_len;                 /// Sample length of one symbol with the cyclic prefix
      int32_t m_open;                     /// Bool to declare if the signal is transmitted (true) or not (false)
      uint32_t m_index_offset;            /// Index the number of sample transmitted for the incomplete and last symbol of the latest work call  
      ofstream myfile;

     public:
      gate_impl(int power_thresh, int symb_len);
      ~gate_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);
      int detect_start_sig (const double *in_samples_dB, const int &ninput_items);
      int detect_stop_sig (const double *in_samples_dB, int ninput_items);
      double * power (const gr_complex *samples, double *log_power, const int &length);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace ephyl
} // namespace gr

#endif /* INCLUDED_EPHYL_GATE_IMPL_H */

