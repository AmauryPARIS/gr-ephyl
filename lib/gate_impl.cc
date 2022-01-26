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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "gate_impl.h"
#include <math.h>

namespace gr {
  namespace ephyl {

    gate::sptr
    gate::make(int power_thresh, int symb_len)
    {
      return gnuradio::get_initial_sptr
        (new gate_impl(power_thresh, symb_len));
    }

    /*
     * The private constructor
     */
    gate_impl::gate_impl(int power_thresh, int symb_len)
      : gr::block("gate",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex)))
    {
      m_power_thresh  =   power_thresh;
      m_symb_len      =   symb_len;
      m_open          =   false;
      m_index_offset  =   0;
    }

    /*
     * Our virtual destructor.
     */
    gate_impl::~gate_impl()
    {
    }

    void
    gate_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    }

    int
    gate_impl::detect_start_sig (const gr_complex &in_samples_dB, int ninput_items)
    {
      for (int i = 0; i < ninput_items; i++){
        if (in_samples_dB[i] > m_power_thresh:
          m_open = true;
          return i;
      }
      return 0;
    }

    int
    gate_impl::detect_stop_sig (const gr_complex &in_samples_dB, int ninput_items)
    {
      for (int i = m_index_offset; i < ninput_items; i++){
        if (in_samples_dB[i] < m_power_thresh:
          m_open = false;
          m_index_offset = 0;
          return i;
      }
      m_index_offset = ninput_items - i;
      return ninput_items;
    }

    dou
    gate_impl::power (const gr_complex &samples, int length)
    {
      double linear_power[length];
      double log_power[length];

      linear_power = pow(pow(samples.real(), 2) + pow(samples.img(), 2),0.5);
      log_power = 10 * log10(linear_power);

      return log_power;
    }

    int
    gate_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const gr_complex *in = (const gr_complex *) input_items[0];
      gr_complex *out = (gr_complex *) output_items[0];

      // Do <+signal processing+>
      // Tell runtime system how many input items we consumed on
      // each input stream.
      consume_each (noutput_items);

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace ephyl */
} /* namespace gr */

