#!/bin/bash

make -f MakefileCL clean
make -f MakefileBB clean
make -f MakefileWAT clean
make -f MakefileDSE clean
make -f MakefileACDK clean
rm -f Makefile*
