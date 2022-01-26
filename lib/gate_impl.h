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

namespace gr {
  namespace ephyl {

    class gate_impl : public gate
    {
     private:
      int32_t m_power_thresh;            /// Threshold value in dB to set the start and end of the signal 
      int32_t m_symb_len;            /// Sample length of one symbol with the cyclic prefix

     public:
      gate_impl(int power_thresh, int symb_len);
      ~gate_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);
      int detect_start_sig (const gr_complex &in_samples_dB, int ninput_items);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace ephyl
} // namespace gr

#endif /* INCLUDED_EPHYL_GATE_IMPL_H */

