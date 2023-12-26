#!/bin/bash

PYPY=`which pypy`

if [ ! -x `which rlwrap` ]; then
    echo "Install rlwrap"
    exit 1
fi

rlwrap ${PYPY} targetlox.py $@
