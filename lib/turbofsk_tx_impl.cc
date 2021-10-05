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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "turbofsk_tx_impl.h"
#include <algorithm>
#include <cmath>
#include "init_turbofsk.h"
#include <mutex>

// std::mutex init_mutex_txrx;

namespace gr {
  namespace ephyl {
    
    turbofsk_tx::sptr
    turbofsk_tx::make(float NbBits)
    {
      return gnuradio::get_initial_sptr
        (new turbofsk_tx_impl(NbBits));
    }

    /*
     * The private constructor
     */
    turbofsk_tx_impl::turbofsk_tx_impl(float NbBits)
      : gr::block("TurboFSK TX",
              gr::io_signature::make(1, 1, sizeof(unsigned char)),
              gr::io_signature::make2(2, 2, sizeof(float), sizeof(float))),
      d_NbBits(NbBits)
    {
      get_turbofsk();
      
      // in EPHYL framework, the packet size is:
      // 14 payload chars + tab + slot_n char = 16 chars = 128 bits 
      // NbBits = 128; 
      /*  OUT = (64*32)+(1+(IN+16)/8)*4*137+(1+int((1+(IN+16)/8)*4/5))*137 */
      Signal_len = (64*32)+(1+(d_NbBits+16)/8)*4*137+(1+int((1+(d_NbBits+16)/8)*4/5))*137;

      set_min_output_buffer(0,Signal_len);
      set_min_output_buffer(1,Signal_len);

      /* Create the input data */
      my_in = mxCreateDoubleMatrix(1,d_NbBits,mxREAL);
      b = mxGetPr(my_in);
      b_size = mxGetN(my_in);      
    }

    /*
     * Our virtual destructor.
     */
    turbofsk_tx_impl::~turbofsk_tx_impl()
    {
      mxDestroyArray(my_in);
      mxDestroyArray(outTx_I);
      mxDestroyArray(outTx_Q);
      release_turbofsk();
    }

    void
    turbofsk_tx_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      ninput_items_required[0] = d_NbBits;
    }

    int
    turbofsk_tx_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const unsigned char *in = (const unsigned char *) input_items[0];
      float *out_i = (float *) output_items[0];
      float *out_q = (float *) output_items[1];

      // printf("\nTX Bits:\n");
      for(int k=0;k<b_size;k++){
        b[k] = double(in[k]);
        // printf("%1.0f",b[k]);
      }
      consume_each (d_NbBits);

/************************************************************************/
      mlfMainTx(2, &outTx_I,&outTx_Q, my_in);
/************************************************************************/      

      // mxMakeArrayComplex(outTx);

      a = (float*)mxGetPr(outTx_I);
      a_size = mxGetM(outTx_I);

      c = (float*)mxGetPr(outTx_Q);
      c_size = mxGetM(outTx_Q);

      // printf("\nTAILLE: %d\n",mxGetElementSize(outTx));

      // To assure stable output When Tx and Rx used in the same time:
      for(int i=0;i < a_size; i++) {
        init_mutex_txrx.lock();
        out_q[i] = c[i];
        out_i[i] = a[i];
        init_mutex_txrx.unlock();
      }

      // for(int i=0;i < c_size; i++) {
      //   init_mutex_txrx.lock();
      //   init_mutex_txrx.unlock();
      // }

      // a = (double*) mxRealloc(a, 0);
      // mxSetPr(outTx_I, a);
      // c = (double*) mxRealloc(c, 0);
      // mxSetPr(outTx_Q, c);

      add_item_tag(0, nitems_written(0), pmt::string_to_symbol("packet_len"), pmt::from_long((int)a_size));
      // add_item_tag(1, nitems_written(1), pmt::string_to_symbol("packet_len"), pmt::from_long((int)c_size));
      return a_size;

    }

  } /* namespace ephyl */
} /* namespace gr */

