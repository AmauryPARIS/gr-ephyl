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


#ifndef INCLUDED_EPHYL_GATE_H
#define INCLUDED_EPHYL_GATE_H

#include <ephyl/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace ephyl {

    /*!
     * \brief <+description of block+>
     * \ingroup ephyl
     *
     */
    class EPHYL_API gate : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<gate> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of ephyl::gate.
       *
       * To avoid accidental use of raw pointers, ephyl::gate's
       * constructor is in a private implementation
       * class. ephyl::gate::make is the public interface for
       * creating new instances.
       */
      static sptr make(int power_thresh, int symb_len);
    };

  } // namespace ephyl
} // namespace gr

#endif /* INCLUDED_EPHYL_GATE_H */

