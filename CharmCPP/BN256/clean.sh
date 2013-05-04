#!/bin/bash

make -f MakefileBBky  clean
make -f MakefileBBct  clean

make -f MakefileGky  clean
make -f MakefileGct clean

make -f MakefileDSEboth clean
make -f MakefileDSEbothex clean

#make -f MakefileBGW clean
#make -f MakefileDFA clean
