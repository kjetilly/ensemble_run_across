#!/bin/bash


set -e

if [[ $(type -P "gcc-11") ]]
then
    CC=$(which gcc-11)
    CXX=$(which g++-11)
else
    CC=$(which gcc)
    CXX=$(which g++)
fi
location=$(pwd)
parallel_build_tasks=1
repo=$1
extra_prefix=$2
install_prefix=$location/opm-install
cd $location
if [[ ! -d $repo ]]; then
    git clone https://github.com/OPM/${repo}
fi
cd $repo
if [[ ! -d build ]]; then
    mkdir build
fi
cd build
USE_DAMARIS=''
if [[ $repo == 'opm-simulators' ]]; then
    USE_DAMARIS='-DUSE_DAMARIS_LIB=ON'
fi
cmake -DCMAKE_C_COMPILER=$CC \
    -DCMAKE_CXX_COMPILER=$CXX \
    -DUSE_MPI=1  \
    -DCMAKE_PREFIX_PATH="$(realpath $location/../../xsd-install);$(realpath $location/../damaris-install);$location/zoltan/;$location/dune;$location/boost;$location/opm-common;$location/opm-material;$location/opm-grid;$location/opm-models;${extra_prefix}" \
    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE} \
    -DBUILD_EXAMPLES=OFF \
    -DCMAKE_INSTALL_PREFIX=$install_prefix \
    -DBUILD_TESTING=OFF \
    -Wno-dev \
    ..
make -j$parallel_build_tasks
make install

