/* -*- c++ -*- */
/* 
 * Copyright 2019 <+YOU OR YOUR COMPANY+>.
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

#ifndef INCLUDED_EPHYL_TURBOFSK_RX_IMPL_H
#define INCLUDED_EPHYL_TURBOFSK_RX_IMPL_H

#include <ephyl/turbofsk_rx.h>
#include <libTurboFSK_v4.h>


namespace gr {
  namespace ephyl {

    class turbofsk_rx_impl : public turbofsk_rx
    {
    float d_Noise;
    float d_NbBits;
     private:
      mxArray *rx_in_I;  /* Define input parameters  */
      mxArray *rx_in_Q;  /* Define input parameters  */
      mxArray *mxNbBits;
      mxArray *mxNoiseVar;
      mxArray *outRxBits = NULL;
      mxArray *outcrcCheck = NULL;
      mxArray *indexPayload = NULL;
      int NbErr,Signal_len,cnt;
      int r,s,t,pkt_cnt;
      double *d,*e;
      size_t c_size,d_size;
    
     public:
      turbofsk_rx_impl(float Noise,float NbBits);
      ~turbofsk_rx_impl();

      void setup_rpc();

      float Noise() const { return d_Noise; }
      void set_Noise(float Noise) { d_Noise = Noise; }
      float NbBits() const { return d_NbBits; }
      void set_NbBits(float NbBits) { d_NbBits = NbBits; }

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace ephyl
} // namespace gr

#endif /* INCLUDED_EPHYL_TURBOFSK_RX_IMPL_H */

