#!/bin/bash

echo "Running BBIBE test"
python runAutoGroup.py --sdl schemes/bbibe04.sdl --config configBBIBE -o TimingBB.txt -b

echo "Running GentryIBE test"
python runAutoGroup.py --sdl schemes/gentry06.sdl --config configGIBE -o TimingGIBE.txt -b

echo "Running Waters09-enc test"
python runAutoGroup.py --sdl schemes/dse09.sdl --config configDSE -o TimingDSE.txt -b

echo "Running BGW test"
python runAutoGroup.py --sdl schemes/bgw05.sdl --config configBGW -o TimingBGW.txt -b # -v

echo "Running CL test"
python runAutoGroup.py --sdl schemes/cl04.sdl --config configCL -o TimingCL.txt -b

echo "Running BBSig test"
python runAutoGroup.py --sdl schemes/bbssig04.sdl --config configBBSig -o TimingBBsig.txt -b

echo "Running Waters05 test"
python runAutoGroup.py --sdl schemes/waters05.sdl --config configWATERS05 -o TimingWATERS.txt -b

echo "Running DSEsig test"
python runAutoGroup.py --sdl schemes/dse09sig.sdl --config configDSEsig -o TimingDSEsig.txt -b

echo "Running ACDK test"
python runAutoGroup.py --sdl schemes/acdk12.sdl --config configACDK -o TimingACDK.txt -b

##echo "Running DFA experiment"
##python runAutoGroup.py --sdl schemes/dfa12.sdl --config configDFA -o TimingDFA.txt -b
