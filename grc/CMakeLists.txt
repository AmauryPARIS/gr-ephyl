# Copyright 2011 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################

install(FILES
    ephyl_turbofsk_tx.xml
    ephyl_turbofsk_tx.xml
    ephyl_turbofsk_rx.xml
    ephyl_data_and_access_control.xml
    ephyl_sn_scheduler.xml
    ephyl_tag_2_msg.xml
    ephyl_bs_scheduler.xml
    ephyl_tag_2_msg_char.xml
    ephyl_msg_mux.xml DESTINATION share/gnuradio/grc/blocks
)
