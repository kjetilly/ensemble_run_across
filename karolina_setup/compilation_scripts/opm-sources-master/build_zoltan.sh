#!/bin/bash
set -e
location=`pwd`


if [[ $(type -P "gcc-11") ]]
then
    CC=$(which gcc-11)
    CXX=$(which g++-11)
else
    CC=$(which gcc)
    CXX=$(which g++)
fi
extra_prefix=$1

parallel_build_tasks=16

export INSTALL_PREFIX=$location"/boost"

trilinos_version=13-4-1
install_prefix=$location"/zoltan"
if [[ ! -d $install_prefix ]]; then
    mkdir $install_prefix
fi

if [[ ! -d Trilinos ]]; then
    # git clone https://github.com/trilinos/Trilinos.git
    wget https://github.com/trilinos/Trilinos/archive/refs/tags/trilinos-release-${trilinos_version}.zip
    unzip trilinos-release-${trilinos_version}.zip
    mv Trilinos-trilinos-release-${trilinos_version} Trilinos
fi

cd Trilinos
# git checkout trilinos-release-13-0-1

if [[ ! -d build ]]; then
    mkdir build
fi
cd build
cmake \
    -DCMAKE_C_COMPILER=$CC \
    -DCMAKE_CXX_COMPILER=$CXX \
    -DCMAKE_INSTALL_PREFIX=$install_prefix \
    -DCMAKE_PREFIX_PATH=$extra_prefix \
    -D TPL_ENABLE_MPI:BOOL=ON \
    -D Trilinos_ENABLE_ALL_PACKAGES:BOOL=OFF \
    -D Trilinos_ENABLE_Zoltan:BOOL=ON \
    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE} \
    -Wno-dev \
    ../
make -j $parallel_build_tasks
make install
cd $location
rm -rf Trilinos

