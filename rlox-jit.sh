#!/bin/sh

if [ ! -x `which rlwrap` ]; then
    echo "Install rlwrap"
    exit 1
fi

if [ ! -f ./rlox-jit ]; then
    make targetlox-jit
fi

rlwrap ./rlox-jit $@
