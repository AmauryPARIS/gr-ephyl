#ifndef INCLUDED_EPHYL_INIT_TURBOFSK_H
#define INCLUDED_EPHYL_INIT_TURBOFSK_H
#include <mutex>

extern std::mutex init_mutex_txrx;

void get_turbofsk();
void release_turbofsk();

#endif // INCLUDED_EPHYL_INIT_TURBOFSK_H