#!/bin/bash

set -x
# all the asymmetric tests

#python genMakefile.py ./config.mk MakefileCL "FOO=1" TestCLAsymSig.cpp benchCLAsym.cpp

#python genMakefile.py ./config.mk MakefileBB "FOO=1" TestBBAsymPK.cpp benchBBAsym.cpp

#python genMakefile.py ./config.mk MakefileWAT "FOO=1" TestWaters05AsymSig.cpp benchWATAsym.cpp

#python genMakefile.py ./config.mk MakefileDSE "FOO=1" TestDSEAsymSig.cpp benchDSEAsym.cpp

python genMakefile.py ./config.mk MakefileACDK "FOO=1" TestACDKBothEx.cpp benchACDK.cpp


set +x
