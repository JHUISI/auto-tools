#!/bin/bash

python genMakefile.py ./config.mk MakefileDSE TestDSE.cpp benchDSE.cpp

python genMakefile.py ./config.mk MakefileBGW TestBGW.cpp benchBGW.cpp

python genMakefile.py ./config.mk MakefileBB TestBB.cpp benchBB.cpp
