#!/bin/bash
make -f MakefileDFAct clean
make -f MakefileDSE clean
make -f MakefileWATERS clean
make -f MakefileBSW clean
make -f MakefileBGW clean
make -f MakefileCKRS clean
make -f MakefileHIBE clean
make -f MakefileLW clean
make -f MakefileSW clean
rm -f Makefile*
