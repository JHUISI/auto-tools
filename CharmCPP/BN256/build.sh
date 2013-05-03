#!/bin/bash

python genMakefile.py ./config.mk MakefileBBky TestBBky.cpp benchBBky.cpp
python genMakefile.py ./config.mk MakefileBBct TestBBct.cpp benchBBct.cpp

python genMakefile.py ./config.mk MakefileGIBEct TestGIBEct.cpp benchGIBEct.cpp
python genMakefile.py ./config.mk MakefileGIBEexp TestGIBEexp.cpp benchGIBEexp.cpp

#python genMakefile.py ./config.mk MakefileDSE TestDSEBothExp.cpp benchDSE.cpp

#python genMakefile.py ./config.mk MakefileBGW TestBGWky.cpp benchBGWky.cpp

#python genMakefile.py ./config.mk MakefileDFA TestDFA.cpp benchDFA.cpp


