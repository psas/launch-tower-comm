#!/bin/sh

export C_INCLUDE_PATH=$HOME/local/include
export LD_LIBRARY_PATH=$HOME/local/lib
export LIBRARY_PATH=$HOME/local/lib
export PATH=$HOME/local/bin:$PATH
export PYTHONPATH=$HOME/local/lib/python2.7/site-packages

cd ~/launch-tower-comm/launch-tower-comm/
exec /usr/bin/env python2.7 ltc.py
