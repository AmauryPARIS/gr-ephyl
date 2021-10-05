FROM m1mbert/cxlb-gnuradio-3.7:1.0

RUN ${APT} update && ${APT} dist-upgrade
RUN ${APT} install unzip
RUN ${APT} install wget
RUN ${APT} install libncurses5
RUN ${APT} install libxmu-dev

WORKDIR /root/cxlb_toolchain_build

RUN wget https://fr.mathworks.com/supportfiles/downloads/R2014a/deployment_files/R2014a/installers/glnxa64/MCR_R2014a_glnxa64_installer.zip
RUN unzip MCR_R2014a_glnxa64_installer.zip -d MCR_build
RUN rm MCR_R2014a_glnxa64_installer.zip
WORKDIR MCR_build/
RUN sh install -mode silent -agreeToLicense yes
RUN mv /usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/bin/glnxa64/libcurl.so.4 /usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/bin/glnxa64/libcurl.so.4_mcr
RUN mv /usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/sys/os/glnxa64/libstdc++.so.6 /usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/sys/os/glnxa64/libstdc++.so.6_mcr

ENV LD_LIBRARY_PATH "${LD_LIBRARY_PATH}:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/bin/glnxa64:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/sys/os/glnxa64"
ENV XAPPLRESDIR "${XAPPLRESDIR}:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/X11/app-defaults"
ENV INSTALL_PATH "/cortexlab/toolchains/current"
ENV MCR_PATH "/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/extern/include"
ENV CPATH "$CPATH:${MCR_PATH}"

WORKDIR /root/cxlb_toolchain_build
# The following command guarantees that git cloning is updated for each new commit
ADD https://api.github.com/repos/CorteXlab/gr-ephyl/git/refs/heads/master version.json
RUN git clone git://github.com/CorteXlab/gr-ephyl.git
WORKDIR gr-ephyl

RUN cp include/libTurboFSK_v4.h /usr/include/
RUN cp lib/libTurboFSK_v4.so /usr/lib/
RUN mkdir build
WORKDIR build
RUN cmake -DCMAKE_INSTALL_PREFIX=${INSTALL_PATH} ..
RUN make
RUN make install
RUN cp ../examples/hier_* /root/.grc_gnuradio/
# RUN grcc /root/cxlb_toolchain_build/gr-ephyl/examples/hier_sensor.grc
# RUN grcc /root/cxlb_toolchain_build/gr-ephyl/examples/bs.grc
# RUN grcc /root/cxlb_toolchain_build/gr-ephyl/examples/hier_sensor_turbofsk.grc
# RUN grcc /root/cxlb_toolchain_build/gr-ephyl/examples/hier_bs_turbofsk.grc
WORKDIR /root
RUN /bin/bash -c "source cxlb_toolchain_build/gr-ephyl/ephyl_docker/env_conf "
# CMD [ "source", "cxlb_toolchain_build/gr-ephyl/ephyl_docker/env_conf" ]

## THIS DOESNT WORK (??)
# cp include/libTurboFSK_v4.h /cortexlab/toolchains/current/include/
#cp lib/libTurboFSK_v4.so /cortexlab/toolchains/current/lib/
