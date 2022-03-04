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
#include "select_m_in_n_impl.h"

namespace gr {
  namespace ephyl {

    select_m_in_n::sptr
    select_m_in_n::make(int choice, int m, int n, int offset)
    {
      return gnuradio::get_initial_sptr
        (new select_m_in_n_impl(choice, m, n, offset));
    }

    /*
     * The private constructor
     */
    select_m_in_n_impl::select_m_in_n_impl(int choice, int m, int n, int offset)
      : gr::block("select_m_in_n",
              gr::io_signature::make(1, 1, sizeof(gr_complex)),
              gr::io_signature::make(1, 1, sizeof(gr_complex)))
    {
      d_m = m;
      d_n = n;
      d_offset = offset;
      d_choice = choice;
      d_itemsize = sizeof(gr_complex);
      std::cout << "Select m in n - INIT - m : " << d_m << " - n : " << d_n << " - choice : " << d_choice << "\n";
    }

    /*
     * Our virtual destructor.
     */
    select_m_in_n_impl::~select_m_in_n_impl()
    {
    }

    void
    select_m_in_n_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = d_n*(noutput_items/d_m);
    }

    double 
    select_m_in_n_impl::power (const gr_complex *samples, const int &length)
    {
      double linear_power = 0;
      double log_power;

      for (int i = 0; i < length; i++){
        linear_power += pow(pow(samples[i].real(), 2) + pow(samples[i].imag(), 2),0.5);
      }
      linear_power = linear_power / length;
      log_power = 10 * log10(linear_power);
      
      return log_power;
    }

    int
    select_m_in_n_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const gr_complex *in = (const gr_complex *) input_items[0];
      gr_complex *out = (gr_complex *) output_items[0];

      // iterate over data blocks of size {n, input : m, output}
      int blks = std::min(noutput_items/d_m, ninput_items[0]/d_n);

      // std::cout << "Select m in n - counter - consume : " << nitems_written(0) << " - produce : " << nitems_read(0) << "\n";

      for(int i=0; i<blks; i++) {
        
        // LOW POWER
        if (d_choice == 0) {
          // std::cout << "Select m in n - low power - input : " << ninput_items[0] << "\n";
          int ref_index = false;
          double pwr;
          double ref_pwr;

          // Compute and find lower power window
          for (int i_sb=0; i_sb < (d_n - d_m); i_sb++){
            pwr = power(&in[i + i_sb], d_m);
            if (i_sb == 0) {ref_pwr = pwr;}
            if (pwr < ref_pwr){
              ref_pwr = pwr;
              ref_index = i_sb;
            }
          }
          // std::cout << "Select m in n - low power - i : " << i << " - samples index : " << ref_index << " - ref power : " << ref_pwr << "\n";

          // Default value
          if (ref_index != false) {
            ref_index = 0;
          }

          // set up copy pointers
          const gr_complex* iptr = &in[(i*d_n + ref_index)];
          gr_complex* optr = &out[i*d_m];
          // perform copy
          memcpy( optr, iptr, d_m*d_itemsize );

        }

        // HIGH POWER
        else if (d_choice == 1) {
          // std::cout << "Select m in n - high power - input : " << ninput_items[0] << "\n";
          int ref_index = false;
          double pwr;
          double ref_pwr;

          // Compute and find lower power window
          for (int i_sb=0; i_sb < (d_n - d_m); i_sb++){
            pwr = power(&in[i + i_sb], d_m);
            if (i_sb == 0) {ref_pwr = pwr;}
            if (pwr > ref_pwr){
              ref_pwr = pwr;
              ref_index = i_sb;
            }
          }

          // Default value
          if (ref_index != false) {
            ref_index = 0;
          }

          // set up copy pointers
          const gr_complex* iptr = &in[(i*d_n + ref_index)];
          gr_complex* optr = &out[i*d_m];
          // perform copy
          memcpy( optr, iptr, d_m*d_itemsize );
        }

        // FIRST SAMPLES
        else if (d_choice == 2) {
          // std::cout << "Select m in n - FIRST SAMPLES - input : " << ninput_items[0] << "\n";
          // set up copy pointers
          const gr_complex* iptr = &in[(i*d_n + d_offset)];
          gr_complex* optr = &out[i*d_m];
          // perform copy
          memcpy( optr, iptr, d_m*d_itemsize );
        }
        // LAST SAMPLES
        else if (d_choice == 3) {
          // set up copy pointers
          const gr_complex* iptr = &in[(i*d_n + (d_n - d_m) - d_offset)];
          gr_complex* optr = &out[i*d_m];
          // perform copy
          memcpy( optr, iptr, d_m*d_itemsize );
          
        }
        else {
          std::cout << "Select m in n - ERROR - NO MODE SELECTED - input : " << ninput_items[0] << "\n";   
        }
      }
      consume_each (d_n* blks);

      // Tell runtime system how many output items we produced.
      return d_m * blks;
    }

  } /* namespace ephyl */
} /* namespace gr */

