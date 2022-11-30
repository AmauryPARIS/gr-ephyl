FROM m1mbert/cxlb-gnuradio-3.7:1.1


RUN ${APT} update && ${APT} dist-upgrade
# RUN ${APT} install unzip
# RUN ${APT} install wget
# RUN ${APT} install libncurses5
# RUN ${APT} install libxmu-dev

# WORKDIR /root/cxlb_toolchain_build

# RUN wget https://fr.mathworks.com/supportfiles/downloads/R2014a/deployment_files/R2014a/installers/glnxa64/MCR_R2014a_glnxa64_installer.zip
# RUN unzip MCR_R2014a_glnxa64_installer.zip -d MCR_build
# RUN rm MCR_R2014a_glnxa64_installer.zip
# WORKDIR MCR_build/
# RUN sh install -mode silent -agreeToLicense yes
# RUN mv /usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/bin/glnxa64/libcurl.so.4 /usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/bin/glnxa64/libcurl.so.4_mcr
# RUN mv /usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/sys/os/glnxa64/libstdc++.so.6 /usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/sys/os/glnxa64/libstdc++.so.6_mcr

ENV LD_LIBRARY_PATH "${LD_LIBRARY_PATH}:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/bin/glnxa64:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/sys/os/glnxa64"
ENV XAPPLRESDIR "${XAPPLRESDIR}:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/X11/app-defaults"
ENV INSTALL_PATH "/cortexlab/toolchains/current"
ENV MCR_PATH "/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/extern/include"
ENV CPATH "$CPATH:${MCR_PATH}"

RUN mkdir /root/.ssh && chmod 0700 /root/.ssh 
RUN ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

# INSTALL LoRa PHY
WORKDIR /root/cxlb_toolchain_build/
RUN git clone https://github.com/AmauryPARIS/LoRa_PHY_Cxlb.git
RUN sed -i "s+/root/LoRa_PHY_Cxlb.git+/root/cxlb_toolchain_build/LoRa_PHY_Cxlb+" /root/cxlb_toolchain_build/LoRa_PHY_Cxlb/gr-lora_sdr/docker_install/build.sh
RUN chmod +x  /root/cxlb_toolchain_build/LoRa_PHY_Cxlb/gr-lora_sdr/docker_install/build.sh ; /root/cxlb_toolchain_build/LoRa_PHY_Cxlb/gr-lora_sdr/docker_install/build.sh 


# INSTALL S3CAP framework
WORKDIR /root/cxlb_toolchain_build
RUN git clone https://github.com/AmauryPARIS/gr-ephyl.git
WORKDIR /root/cxlb_toolchain_build/gr-ephyl
RUN mkdir build
WORKDIR /root/cxlb_toolchain_build/gr-ephyl/build
RUN cmake -DCMAKE_INSTALL_PREFIX=${INSTALL_PATH} ..
RUN make
RUN make install
WORKDIR /root/cxlb_toolchain_build/gr-ephyl/examples/LoRa
#RUN grcc -d . hier_bs_lora.grc
#RUN grcc -d . hier_sn_lora.grc

# the container's default executable: ssh daemon
CMD [ "/usr/sbin/sshd", "-p", "2222", "-D" ]
