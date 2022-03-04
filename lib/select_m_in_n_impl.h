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

#ifndef INCLUDED_EPHYL_SELECT_M_IN_N_IMPL_H
#define INCLUDED_EPHYL_SELECT_M_IN_N_IMPL_H

#include <ephyl/select_m_in_n.h>

namespace gr {
  namespace ephyl {

    class select_m_in_n_impl : public select_m_in_n
    {
     private:
      int d_m;
      int d_n;
      int d_offset;
      int d_choice;
      int d_itemsize;

     public:
      select_m_in_n_impl(int choice, int m, int n, int offset);
      ~select_m_in_n_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);
      double power (const gr_complex *samples, const int &length);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace ephyl
} // namespace gr

#endif /* INCLUDED_EPHYL_SELECT_M_IN_N_IMPL_H */

