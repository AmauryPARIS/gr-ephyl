/*
 * MATLAB Compiler: 5.1 (R2014a)
 * Date: Thu Oct  3 17:42:58 2019
 * Arguments: "-B" "macro_default" "-W" "lib:libTurboFSK_v3" "-T" "link:lib"
 * "-d" "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/libTurboFSK_v3/for_testing"
 * "-v" "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/Standalone/Turbo_FSK_Rx/mainRx.m
 * " "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/Standalone/TurboFSK_Tx/mainTx.m"
 * "class{Class1:/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/Standalone/Turbo_FSK_Rx/mainRx.m
 * ,/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/Standalone/TurboFSK_Tx/mainTx.m}
 * " "-a" "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/Cmex/AppMLMAP.mexa64" "-a"
 * "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/blocks/bcjrTolm.m" "-a"
 * "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/blocks/ChannelEstimation_v4.m"
 * "-a" "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/blocks/channelMST.m" "-a"
 * "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/Cmex/computeCrc.mexa64" "-a"
 * "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/blocks/equalize_cfo.m" "-a"
 * "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/Cmex/ForwardBackwardTolm.mexa64"
 * "-a" "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/functions/get_UMTS_interleaver.m
 * " "-a" "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/functions/getRSCTrellis.m" "-a"
 * "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/Standalone/TurboFSK_Tx/initConfi
 * gSA.m" "-a" "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/Standalone/TurboFSK_Tx/initModeS
 * A.m" "-a" "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/functions/initModule.m" "-a"
 * "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/functions/MengaliMorelli.m"
 * "-a" "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/functions/mybi2de.m" "-a"
 * "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/functions/myde2bi.m" "-a"
 * "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/blocks/pilotcfo.m" "-a"
 * "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/Standalone/Turbo_FSK_Rx/rx_FDSA.
 * m" "-a" "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/blocks/synchroZF3.m" "-a"
 * "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/Standalone/Turbo_FSK_Rx/tolmDeco
 * derSA.m" "-a" "/home/360.1.296-JOE-LPWA/500
 * Development/SimulationMatlab/matlab_TurboFSK/tests/ZadoffChuSeq.m" 
 */

#ifndef __libTurboFSK_v3_h
#define __libTurboFSK_v3_h 1

#if defined(__cplusplus) && !defined(mclmcrrt_h) && defined(__linux__)
#  pragma implementation "mclmcrrt.h"
#endif
#include "mclmcrrt.h"
#ifdef __cplusplus
extern "C" {
#endif

#if defined(__SUNPRO_CC)
/* Solaris shared libraries use __global, rather than mapfiles
 * to define the API exported from a shared library. __global is
 * only necessary when building the library -- files including
 * this header file to use the library do not need the __global
 * declaration; hence the EXPORTING_<library> logic.
 */

#ifdef EXPORTING_libTurboFSK_v3
#define PUBLIC_libTurboFSK_v3_C_API __global
#else
#define PUBLIC_libTurboFSK_v3_C_API /* No import statement needed. */
#endif

#define LIB_libTurboFSK_v3_C_API PUBLIC_libTurboFSK_v3_C_API

#elif defined(_HPUX_SOURCE)

#ifdef EXPORTING_libTurboFSK_v3
#define PUBLIC_libTurboFSK_v3_C_API __declspec(dllexport)
#else
#define PUBLIC_libTurboFSK_v3_C_API __declspec(dllimport)
#endif

#define LIB_libTurboFSK_v3_C_API PUBLIC_libTurboFSK_v3_C_API


#else

#define LIB_libTurboFSK_v3_C_API

#endif

/* This symbol is defined in shared libraries. Define it here
 * (to nothing) in case this isn't a shared library. 
 */
#ifndef LIB_libTurboFSK_v3_C_API 
#define LIB_libTurboFSK_v3_C_API /* No special import/export declaration */
#endif

extern LIB_libTurboFSK_v3_C_API 
bool MW_CALL_CONV libTurboFSK_v3InitializeWithHandlers(
       mclOutputHandlerFcn error_handler, 
       mclOutputHandlerFcn print_handler);

extern LIB_libTurboFSK_v3_C_API 
bool MW_CALL_CONV libTurboFSK_v3Initialize(void);

extern LIB_libTurboFSK_v3_C_API 
void MW_CALL_CONV libTurboFSK_v3Terminate(void);



extern LIB_libTurboFSK_v3_C_API 
void MW_CALL_CONV libTurboFSK_v3PrintStackTrace(void);

extern LIB_libTurboFSK_v3_C_API 
bool MW_CALL_CONV mlxMainRx(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[]);

extern LIB_libTurboFSK_v3_C_API 
bool MW_CALL_CONV mlxMainTx(int nlhs, mxArray *plhs[], int nrhs, mxArray *prhs[]);


extern LIB_libTurboFSK_v3_C_API bool MW_CALL_CONV mlfMainRx(int nargout, mxArray** RxBits, mxArray** crcCheck, mxArray** indsynchro, mxArray* RxSamples, mxArray* NbBits, mxArray* noiseVar);

extern LIB_libTurboFSK_v3_C_API bool MW_CALL_CONV mlfMainTx(int nargout, mxArray** TxIQ, mxArray* infoBits);

#ifdef __cplusplus
}
#endif
#endif
