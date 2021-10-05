#include "turbofsk_rx_impl.h"
#include <mutex>

int lib_turbofsk_init = 0;
std::mutex init_mutex;
std::mutex init_mutex_txrx;
// extern std::mutex init_mutex_txrx;

const char *opts[]={"-singleCompThread"}; 

void get_turbofsk() {

  init_mutex.lock();
  if (lib_turbofsk_init == 0) {
    if( !mclInitializeApplication(opts,0) )
    {
      fprintf(stderr, "Could not initialize the application.\n");
      init_mutex.unlock();
      throw new std::exception();
    }

    if (!libTurboFSK_v4Initialize()){
      fprintf(stderr,"Could not initialize the library.\n");
      init_mutex.unlock();
      throw new std::exception();
    } 
  }
  lib_turbofsk_init++;
  init_mutex.unlock();
}

void release_turbofsk() {
  init_mutex.lock();
  lib_turbofsk_init--;
  if (lib_turbofsk_init == 0) {
    //  Call the library termination routine 
    libTurboFSK_v4Terminate();     

    /* Note that you should call mclTerminate application at the end of your application */
    mclTerminateApplication();
  }
  init_mutex.unlock();
}
