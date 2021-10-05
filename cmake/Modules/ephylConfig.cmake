INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_EPHYL ephyl)

FIND_PATH(
    EPHYL_INCLUDE_DIRS
    NAMES ephyl/api.h
    HINTS $ENV{EPHYL_DIR}/include
        ${PC_EPHYL_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    EPHYL_LIBRARIES
    NAMES gnuradio-ephyl
    HINTS $ENV{EPHYL_DIR}/lib
        ${PC_EPHYL_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(EPHYL DEFAULT_MSG EPHYL_LIBRARIES EPHYL_INCLUDE_DIRS)
MARK_AS_ADVANCED(EPHYL_LIBRARIES EPHYL_INCLUDE_DIRS)

