#!/bin/bash
# Author: Wonder
# Description:
# Usage:

SUDO=`command -v sudo`
LUA_VERSION="5.1"
PREFIX=${PREFIX-"/usr"}
LUAJIT_PREFIX=${PREFIX}
NGINX_PREFIX=${PREFIX}

# Tell nginx's build system where to find luajit
# NOTE: LUAJIT_LIB and LUAJIT_INC is exported to nginx configure script,
# please dont change their names 
# Refer to: https://github.com/openresty/lua-nginx-module#installation
export LUAJIT_LIB=${LUAJIT_PREFIX}/lib
export LUAJIT_INC=${LUAJIT_PREFIX}/include/luajit-2.1

# Set lua lib dir(pure lua lib and C modules)
export LUA_LIB_DIR=${LUAJIT_PREFIX}/lib/lua/${LUA_VERSION}
export LUA_CMODULE_DIR=${LUA_LIB_DIR}

JOBS=`nproc`
MAKE="make -j${JOBS}"
CD() {
    echo "- Getting into $1"
    cd "$@"
}

ROOT_DIR=`pwd`
CONF_DIR="${ROOT_DIR}/conf"
export BUNDLE_DIR="${ROOT_DIR}/bundle"

# build&install LuaJIT:
CD $ROOT_DIR/bundle/luajit2-2.1-20160517/
$MAKE PREFIX=${LUAJIT_PREFIX} || exit 1
$SUDO $MAKE install PREFIX=${LUAJIT_PREFIX}

# add www-data user&group
$SUDO adduser --system --no-create-home --disabled-login --disabled-password --group www-data

$SUDO mkdir -p /var/tmp/nginx/

# build nginx with modules
CD "$($ROOT_DIR/module-manager.py --show-path nginx)"
./configure --prefix=${NGINX_PREFIX} \
    $(cat "${CONF_DIR}/ng-configure-opts.txt" | grep -v '^#') \
    --with-ld-opt="-Wl,-rpath,${LUAJIT_LIB}" \
    $(cat ${ROOT_DIR}/added-modules.txt | awk '{ printf("--add-module=%s/%s ", ENVIRON["BUNDLE_DIR"], $0) }');
$MAKE || exit 1
$SUDO $MAKE install

# install lua libs
CD $($ROOT_DIR/module-manager.py --show-path lua_cjson)
$MAKE PREFIX=${LUAJIT_PREFIX} LUA_INCLUDE_DIR=${LUAJIT_INC} || exit 1
$SUDO $MAKE install PREFIX=${LUAJIT_PREFIX} LUA_INCLUDE_DIR=${LUAJIT_INC} LUA_CMODULE_DIR=${LUA_CMODULE_DIR}


for lua_lib in  lua_resty_string \
                lua_resty_redis \
                lua_resty_lrucache \
                lua_resty_core \
                lua_resty_iputils; do
    CD "$($ROOT_DIR/module-manager.py --show-path $lua_lib)"
    $SUDO $MAKE install LUA_LIB_DIR=${LUA_LIB_DIR} 2>/dev/null ||
    # FIXME: find a more robust method
    $SUDO cp -r lib/* ${LUA_LIB_DIR}
done
