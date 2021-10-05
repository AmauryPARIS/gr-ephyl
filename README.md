# GR-EPHYL: GRC resources used in the EPHYL project

## What is it ?

- Here you can find all GNU Radio blocks and designs used in [EPHYL project](https://project.inria.fr/ephyl/) _(Enhanced Physical Layer for Cellular IoT)_.
- The blocks are developed in Python _(gr_modtool)_.
- After properly installing the module, have a look at the examples/ directory


## Requirements

- Ubuntu 16, Debian 8.10 or higher
- [CorteXlab Toolchain 3.7](https://github.com/CorteXlab/cxlb-build-toolchain) already installed with at least these packages:
 - UHD
 - UHD Firmware
 - GNU Radio v3.7
- Matlab Runtime 2014a (Default installation, no custom directories). Unless you do not need TurboFSK blocks, in this case have a look at the branch "no_turbofsk"
- Some basic knowledge of GNU Radio


## Installation

### Docker Image

Have a look at the [DockerHub repository](https://hub.docker.com/r/timina/cxlb-ephyl " DockerHub repo"). Or simply run the following:
```
docker pull timina/cxlb-ephyl:latest
docker run -dti --net=host timina/cxlb-ephyl
```
Then connect to the container via ssh:
```
ssh -Xp 2222 root@localhost
```
The main advantage of using our docker image is avoiding all installing/upgrading/downgrading steps in order to use the module. Furthermore, the docker image provides a full compatibility with the [CorteXlab](http://www.cortexlab.fr/ "CorteXlab") testbed. 

### Local machine installation

- Be sure to install resources via the [Toolchain](https://github.com/CorteXlab/cxlb-build-toolchain).
- Be sure to know your install directory used in the toolchain, and put it in an environment variable, in order to use later:
  - For example if you installed the toolchain using this command:
```
./cxlb-build-toolchain /A/B/compiled_stuff  /D/installed_stuff
```
 - You should run this:
```
echo 'export INSTALL_PATH=/D/installed_stuff' >> ~/.bashrc
```
- If you haven't done it yet, set some environment variables to configure MCR. These are MCR install directories when it is installed by default. If you happen to have a custom MCR installation, make sure you are putting the correct paths:

```
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/bin/glnxa64:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/sys/os/glnxa64' >> ~/.bashrc 

echo 'export XAPPLRESDIR=$XAPPLRESDIR:/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/X11/app-defaults' >> ~/.bashrc 

echo 'export MCR_PATH=/usr/local/MATLAB/MATLAB_Compiler_Runtime/v83/extern/include' >> ~/.bashrc

echo 'export CPATH=$CPATH:$MCR_PATH' >> ~/.bashrc

```
- Source your .bashrc or close and reopen your current shell to confirm changes.
- Run the following to clone this repository:

```
git clone git://github.com/CorteXlab/gr-ephyl.git
cd gr-ephyl
```
- Now we have to make some modifications to `CMakeLists.txt` in order to include MCR and TurboFSK libraries when compiling:
 - Open `CMakeLists.txt` and look for the 3 lines containing `/home/othmane/` *(They should be in lines 171, 172 and 179)*:
```
/home/othmane/opt/cx/opt/MATLAB_Compiler_Runtime/v83/extern/include
/home/othmane/opt/cx/include
...
/home/othmane/opt/cx/lib
```
 - Replace these lines with the following:
```
${MCR_PATH}
${INSTALL_PATH}/include
...
${INSTALL_PATH}/lib
```

- Everything is set for our GNU Radio module to be compiled properly. Run the follwoing:
```
cp include/libTurboFSK_v4.h ${INSTALL_PATH}/include/
cp lib/libTurboFSK_v4.so ${INSTALL_PATH}/lib/
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX=${INSTALL_PATH} ..
make
make install
```

- Now generate the hierarchical blocks corresponding to the classes of nodes of the design:
  - Go to `examples/`, open all flowgraphs startins with `hier_*.grc` and generate their respective python files. Or copy-paste them from `apps/` to `$HOME/.grc_gnuradio`.
  - Reload blocks


## How to use

Have a look at `examples/`, there are flowgraphs of loopbacks, disassembled hierarchical blocks and UHD compatible examples.

# Design

As mentioned before, there is two main classes/types of nodes:
- Base Station (BS) emulator _(hier_bs.grc)_
- IoT Sensor emulator, which is a network user in fact _(hier_sensor*.grc)_


# Documentation

- In progress


# gr_ephyl_mac_RL
