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
extra_prefix=$1
install_prefix=$location/opm-install-josh
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
for repo in opm-common opm-grid opm-models opm-simulators
do
	# opm-common: 9e3fa794cebb3f0902dfa3400797254ad9ddd5ce
	# opm-grid: 0276599f9eb63de44c3e4f1560f134d8ff77c03d
	# opm-models: 24a8280933230c22b030de0ea73cb0e6109e51f9
	# opm-simulators: 40697789f836da7a5eab4e3f54733e204856cc64  (from github/jcbowden)
    cd $location
    if [[ ! -d $repo ]]; then
		if [[ "$repo" == "opm-simulators" ]]
		then
			git clone https://github.com/jcbowden/${repo} -b damariswriter-for-sim-fields-v5-master

			# TODO: Make a nicer fix for this. This is to make it compile
			# with newer versions of fmtlib
			cp ${SCRIPT_DIR}/ISTLSolverEbos.cpp opm-simulators/opm/simulators/linalg/ISTLSolverEbos.cpp    
		else
			git clone https://github.com/OPM/${repo}
			cd ${repo}
			if [[ "$repo" == "opm-common" ]]
			then
				git checkout 9e3fa794cebb3f0902dfa3400797254ad9ddd5ce
                cp ${SCRIPT_DIR}/Schedule.hpp opm/input/eclipse/Schedule/Schedule.hpp

			elif [[ "$repo" == "opm-grid" ]]
			then
				git checkout 0276599f9eb63de44c3e4f1560f134d8ff77c03d
			elif [[ "$repo" == "opm-models" ]]
			then
				git checkout 24a8280933230c22b030de0ea73cb0e6109e51f9
			else
				git checkout `git rev-list -n 1 --before="2023-09-28 18:37" master`
			fi
			cd ..;
		fi
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
	${USE_DAMARIS} \
	..
    make -j$parallel_build_tasks
    make install
done
cd $location
