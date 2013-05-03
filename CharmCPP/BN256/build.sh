#!/bin/bash

python genMakefile.py ./config.mk MakefileBBky TestBBky.cpp benchBBky.cpp

python genMakefile.py ./config.mk MakefileGIBEky TestGIBEky.cpp benchGIBEky.cpp

#python genMakefile.py ./config.mk MakefileDSE TestDSE.cpp benchDSE.cpp

#python genMakefile.py ./config.mk MakefileBGW TestBGW.cpp benchBGW.cpp

#python genMakefile.py ./config.mk MakefileDFA TestDFA.cpp benchDFA.cpp


