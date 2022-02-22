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
#include <cmath>
#include <iostream>
#include <fstream>

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
      m_power_thresh  =   (double) power_thresh;
      m_symb_len      =   symb_len;
      m_open          =   false;
      m_index_offset  =   0;
      myfile.open ("example.txt");
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
      ninput_items_required[0] = noutput_items;
    }

    int
    gate_impl::detect_start_sig (const double *in_samples_dB, const int &ninput_items)
    {
      for (int i = 0; i < ninput_items; i++){
        if (in_samples_dB[i] > m_power_thresh){
          m_open = true;
          return i;
        }
      }
      return 0;
    }

    int
    gate_impl::detect_stop_sig (const double *in_samples_dB, int ninput_items)
    {
      int i = 0;
      std::cout << "GATE - search stop index offset : " << m_index_offset << "\n";
      for (i = m_symb_len - m_index_offset; i < ninput_items; i = i + m_symb_len){
        if (in_samples_dB[i] < m_power_thresh) {
          m_open = false;
          m_index_offset = 0;
          return i;
        }
      }
      m_index_offset = ninput_items - (i - m_symb_len);
      std::cout << "GATE - Stop not found - n input items : " << ninput_items << " - index offset : " << m_index_offset << " - i : " << i << "\n";
      return ninput_items;
    }

    double *
    gate_impl::power (const gr_complex *samples, double *log_power, const int &length)
    {
      double linear_power;

      for (int i = 0; i < length; i++){
        linear_power = pow(pow(samples[i].real(), 2) + pow(samples[i].imag(), 2),0.5);
        log_power[i] = 10 * log10(linear_power);
        if (linear_power != 0 ) {
          myfile << nitems_read(0) << "," << samples[i].real() << "," << samples[i].real() << "," << samples[i].imag() << "," << linear_power << "," << log_power[i] << "\n";
        }
        // std::cout << "power," << samples[i].real() << "," << samples[i].imag() << "," << linear_power << "," << log_power[i] << "\n";
      }
      
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
      const int &ninputitems = (int &) ninput_items[0];

      double empty_log_power[ninputitems];
      int start_sig = 0;
      int stop_sig = 0;

      double *log_power = power(in, empty_log_power, ninputitems);

      double sum;
      double average;
      double min = 1000;
      double max = -1000;
      for(int i = 0; i < ninputitems; ++i)
      {
          if (log_power[i] > max) {
            max = log_power[i];
          }
          if (log_power[i] < min) {
            min = log_power[i];
          }
      }

      // std::cout << "GATE - power value - min : " << min << " - max : " << max << "\n";

      if (m_open == false) {
        start_sig = std::max(0, detect_start_sig(log_power, ninputitems)-10);
        if (start_sig != 0) {
          std::cout << "GATE - Start found : " << start_sig << " - ninputitems " << ninputitems << "\n";
        }
        
      }
      
      if (m_open == true) {
        stop_sig = detect_stop_sig(log_power + start_sig, ninputitems - start_sig) + start_sig;
        std::cout << "GATE - nimput items : " << ninputitems << " - start : " << start_sig << " - stop : " << stop_sig << "\n";
        int signal_sample_length = stop_sig - start_sig;
        for (int i = start_sig; i < stop_sig; i++) {
          out[i - start_sig] = in[i];
        }
        produce(0, signal_sample_length);
        std::cout << "GATE - produce " << signal_sample_length << " samples - total : " << nitems_written(0) << " ################  \n";
      }

      consume_each (ninputitems);
      return WORK_CALLED_PRODUCE;
    }

  } /* namespace ephyl */
} /* namespace gr */

