#!/bin/bash

set -x
# all the asymmetric tests

python genMakefile.py ./config.mk MakefileWATERS TestWATERS.cpp benchWATERS.cpp

python genMakefile.py ./config.mk MakefileBSW TestBSW.cpp benchBSW.cpp

python genMakefile.py ./config.mk MakefileDSE TestDSEct.cpp benchDSE.cpp

python genMakefile.py ./config.mk MakefileLW TestLW.cpp benchLW.cpp

python genMakefile.py ./config.mk MakefileBGW TestBGWct.cpp benchBGW.cpp

python genMakefile.py ./config.mk MakefileCKRS TestCKRS.cpp benchCKRS.cpp

python genMakefile.py ./config.mk MakefileHIBE TestHIBE.cpp benchHIBE.cpp

python genMakefile.py ./config.mk MakefileSW TestSW.cpp benchSW.cpp

# dfa test 
python genMakefile.py ../config.mk MakefileDFAct TestDFAct.cpp benchDFA.cpp


./TestWATERS 100 100 fixed

./TestBSW 100 100 fixed

#./TestDSE 100 100 fixed

./TestLW 100 100 fixed

./TestCKRS 100 100 fixed

./TestHIBE 100 100 fixed

./TestBGWct 100 100 fixed

./TestSW 100 100 fixed

#./TestDFAct 100 100 25 fixed

set +x
