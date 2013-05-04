#!/bin/bash

python genMakefile.py ./config.mk MakefileBBky "TESTBBKY=1" TestBBky.cpp benchBBbn.cpp
python genMakefile.py ./config.mk MakefileBBct "TESTBBCT=1" TestBBct.cpp benchBBbn.cpp

python genMakefile.py ./config.mk MakefileGky "TESTGIBEKY=1" TestGIBEky.cpp benchGIBEbn.cpp
python genMakefile.py ./config.mk MakefileGct "TESTGIBECT=1" TestGIBEct.cpp benchGIBEbn.cpp

python genMakefile.py ./config.mk MakefileDSEboth   "TESTDSEBOTH=1" TestDSEBoth.cpp benchDSEbn.cpp
python genMakefile.py ./config.mk MakefileDSEbothex "TESTDSEBOTHEX=1" TestDSEBothEx.cpp benchDSEbn.cpp

#python genMakefile.py ./config.mk MakefileBGW TestBGWky.cpp benchBGWky.cpp

#python genMakefile.py ./config.mk MakefileDFAct TestDFAct.cpp benchDFA.cpp


