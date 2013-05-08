#!/bin/bash

set -x
# all the asymmetric tests

python genMakefile.py ./config.mk MakefileCLsu "FOO=1" TestCLsu.cpp benchCLsu.cpp

python genMakefile.py ./config.mk MakefileBBsu "FOO=1" TestBBsu.cpp benchBBsu.cpp

python genMakefile.py ./config.mk MakefileWATsu "FOO=1" TestWaters05su.cpp benchWATsu.cpp

# need to add a few more ... DSS? 

##python genMakefile.py ./config.mk MakefileDSE "FOO=1" TestDSESigorig.cpp benchDSEorig.cpp

##python genMakefile.py ./config.mk MakefileACDK "FOO=1" TestACDKorig.cpp benchACDKorig.cpp


set +x
