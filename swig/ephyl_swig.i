/* -*- c++ -*- */

#define EPHYL_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "ephyl_swig_doc.i"

%{
#include "ephyl/turbofsk_tx.h"
#include "ephyl/turbofsk_rx.h"
#include "ephyl/gate.h"
#include "ephyl/select_m_in_n.h"
%}


%include "ephyl/turbofsk_tx.h"
GR_SWIG_BLOCK_MAGIC2(ephyl, turbofsk_tx);

%include "ephyl/turbofsk_rx.h"
GR_SWIG_BLOCK_MAGIC2(ephyl, turbofsk_rx);
%include "ephyl/gate.h"
GR_SWIG_BLOCK_MAGIC2(ephyl, gate);
%include "ephyl/select_m_in_n.h"
GR_SWIG_BLOCK_MAGIC2(ephyl, select_m_in_n);
