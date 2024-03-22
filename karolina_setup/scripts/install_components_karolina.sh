#!/bin/bash
set -e
if [ $# -eq 0 ]
then
    echo "No arguments supplied"
    echo "Usage:"
    echo "    bash $0 <path to install directory>"
    exit 1
fi

export CC=$(which gcc)
export CXX=$(which g++)

target_dir=$(realpath $1)
mkdir -p $target_dir
# see https://stackoverflow.com/a/246128
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
compilation_scripts_dir=$(dirname $SCRIPT_DIR)/compilation_scripts
ERT_VENV=${target_dir}/ert_venv
FLOW_VENV=${target_dir}/flow_venv
BUILD_FOLDER=${target_dir}/src

mkdir -p ${BUILD_FOLDER}
BUILD_TYPE=Release

python -m venv $ERT_VENV
python -m venv  --system-site-packages $FLOW_VENV


. $FLOW_VENV/bin/activate
pip install --upgrade pip
pip3 install -r ${compilation_scripts_dir}/damaris-scripts/requirements.txt
pip3 install cmake

cd ${BUILD_FOLDER}
git clone https://github.com/OPM/pyopmspe11.git
cd pyopmspe11
pip install -e .
# we need build2 for xsd which we in turn need for damaris
cd $BUILD_FOLDER/
mkdir build2
cd build2
curl -sSfO https://download.build2.org/0.16.0/build2-install-0.16.0.sh
sh build2-install-0.16.0.sh --trust 70:64:FE:E4:E0:F3:60:F1:B4:51:E1:FA:12:5C:E0:B3:DB:DF:96:33:39:B9:2E:E5:C2:68:63:4C:A6:47:39:43 --yes ${target_dir}/build2

# We need XSD for damaris
cd ${BUILD_FOLDER}
mkdir xsd
cd xsd

${target_dir}/build2/bin/bpkg create -d xsd-gcc-10 cc     \
  config.cxx=g++                  \
  config.cc.coptions=-O3          \
  config.bin.rpath=${target_dir}/xsd-install \
  config.install.root=${target_dir}/xsd-install 

cd xsd-gcc-10
${target_dir}/build2/bin/bpkg build --trust 70:64:FE:E4:E0:F3:60:F1:B4:51:E1:FA:12:5C:E0:B3:DB:DF:96:33:39:B9:2E:E5:C2:68:63:4C:A6:47:39:43 --yes --sys-yes xsd@https://pkg.cppget.org/1/beta

${target_dir}/build2/bin/bpkg install xsd


export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${target_dir}/xsd-install/lib:${target_dir}/boost-install

cd ${BUILD_FOLDER}/xsd

${target_dir}/build2/bin/bpkg create -d libxsd-gcc-10 cc  \
  config.cxx=g++                  \
  config.cc.coptions=-O3          \
  config.install.root=${target_dir}/xsd-install \

cd libxsd-gcc-10
${target_dir}/build2/bin/bpkg add https://pkg.cppget.org/1/beta
${target_dir}/build2/bin/bpkg fetch --trust 70:64:FE:E4:E0:F3:60:F1:B4:51:E1:FA:12:5C:E0:B3:DB:DF:96:33:39:B9:2E:E5:C2:68:63:4C:A6:47:39:43
${target_dir}/build2/bin/bpkg build --yes libxerces-c
${target_dir}/build2/bin/bpkg build --yes libexpat
${target_dir}/build2/bin/bpkg build --yes libxsd
${target_dir}/build2/bin/bpkg install --all --recursive

deactivate
cd ${BUILD_FOLDER}
bash ${SCRIPT_DIR}/install_boost.sh ${target_dir}/boost-install
cd ${BUILD_FOLDER}
. $FLOW_VENV/bin/activate
mkdir -p ${target_dir}/damaris-extra

git clone https://gitlab.inria.fr/Damaris/damaris.git
cd damaris
mkdir -p build
cd build
cmake .. \
    -DENABLE_HDF5=ON \
    -DENABLE_PYTHON=ON \
    -DENABLE_PYTHONMOD=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_PREFIX_PATH="${target_dir}/xsd-install;${target_dir}/boost-install" \
    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE} \
    -DGENERATE_MODEL=ON \
    -DPython_FIND_VIRTUALENV=ONLY \
    -DCMAKE_INSTALL_PREFIX=${BUILD_FOLDER}/damaris-install \
    -DPYTHON_MODULE_INSTALL_PATH=${BUILD_FOLDER}/damaris_python && \
make install

# Get fake_ert
cd ${BUILD_FOLDER}
git clone https://github.com/kjetilly/opm-runner.git

cp -r ${compilation_scripts_dir}/opm-sources-master ${BUILD_FOLDER}/opm-sources
cd ${BUILD_FOLDER}
cd opm-sources
bash build_zoltan.sh ${target_dir}/boost-install
bash build_dune.sh ${target_dir}/boost-install
bash build_opm_component.sh opm-common ${target_dir}/boost-install
bash build_opm_component.sh opm-grid ${target_dir}/boost-install
bash build_opm_component.sh opm-models ${target_dir}/boost-install
bash build_opm_component.sh opm-simulators ${target_dir}/boost-install
deactivate


cd ${BUILD_FOLDER}
wget https://github.com/It4innovations/hyperqueue/releases/download/v0.16.0/hq-v0.16.0-linux-x64.tar.gz
mkdir -p ${target_dir}/bin
cd ${target_dir}/bin
tar xvf ${BUILD_FOLDER}/hq-v0.16.0-linux-x64.tar.gz && \
rm -rf ${BUILD_FOLDER}/hq-v0.16.0-linux-x64.tar.gz && \
chmod a+rwx hq

cp ${compilation_scripts_dir}/run-scripts/* ${target_dir}/bin/
mv ${target_dir}/bin/flow_venv_native.sh ${target_dir}/bin/flow_venv.sh
chmod a+x ${target_dir}/bin/*.sh
chmod a+x ${target_dir}/bin/fix_xml.py
chmod a+x ${target_dir}/bin/get_ensemble_number.py



cp -r ${compilation_scripts_dir}/damaris-scripts ${target_dir}/damaris-scripts
mv ${target_dir}/damaris-scripts/damaris_native.xml ${target_dir}/damaris-scripts/damaris.xml
chmod -R a+rX ${target_dir}/damaris-scripts


echo "export DASK_FILE=${target_dir}/dask.json" > ${target_dir}/environments.sh
echo "export FLOW_VENV=$FLOW_VENV" >> ${target_dir}/environments.sh
echo "export ERT_VENV=$ERT_VENV" >> ${target_dir}/environments.sh
