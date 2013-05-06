#!/bin/bash

set -x
# all the asymmetric tests

python genMakefile.py ../config.mk MakefileWATERS TestWATERS.cpp benchWATERS.cpp

python genMakefile.py ../config.mk MakefileBSW TestBSWOut2.cpp benchBSWOut.cpp

python genMakefile.py ../config.mk MakefileLW TestLWOut2.cpp benchLWOut.cpp

python genMakefile.py ../config.mk MakefileDSE TestDSEOut2.cpp benchDSEOut.cpp

python genMakefile.py ../config.mk MakefileCKRS TestCKRSOut2.cpp benchCKRSOut.cpp

python genMakefile.py ../config.mk MakefileHIBE TestHIBEOut2.cpp benchHIBEOut.cpp

python genMakefile.py ../config.mk MakefileSW TestSWOut2.cpp benchSWOut.cpp

python genMakefile.py ../config.mk MakefileBGW TestBGWOut2.cpp benchBGWOut.cpp

python genMakefile.py ../config.mk MakefileDFA TestDFAOut2.cpp benchDFAOut.cpp


#./TestWATERS 100 100 fixed

#./TestBSWOut2 100 100 fixed

#./TestLWOut2 100 100 fixed

#./TestDSEOut2 100 100 fixed

#./TestCKRSOut2 100 100 fixed

#./TestHIBEOut2 100 100 fixed

#./TestSWOut2 100 100 fixed

#./TestBGWOut2 100 100 fixed

#./TestDFAOut2 100 500 1 fixed

set +x
