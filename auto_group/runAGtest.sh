#!/bin/bash

echo "Running BBIBE test"
python3 runAutoGroup.py --sdl schemes/bbibe04.sdl --config schemes/configBBIBE.py -o TimingBB.txt -b

echo "Running GentryIBE test"
python3 runAutoGroup.py --sdl schemes/gentry06.sdl --config schemes/configGIBE.py -o TimingGIBE.txt -b

echo "Running Waters09-enc test"
python3 runAutoGroup.py --sdl schemes/dse09.sdl --config schemes/configDSE.py -o TimingDSE.txt -b

echo "Running BGW test"
python3 runAutoGroup.py --sdl schemes/bgw05.sdl --config schemes/configBGW.py -o TimingBGW.txt -b # -v

echo "Running CL test"
python3 runAutoGroup.py --sdl schemes/cl04.sdl --config schemes/configCL.py -o TimingCL.txt -b

echo "Running BBSig test"
python3 runAutoGroup.py --sdl schemes/bbssig04.sdl --config schemes/configBBSig.py -o TimingBBsig.txt -b

echo "Running Waters05 test"
python3 runAutoGroup.py --sdl schemes/waters05.sdl --config schemes/configWATERS05.py -o TimingWATERS.txt -b

echo "Running DSEsig test"
python3 runAutoGroup.py --sdl schemes/dse09sig.sdl --config schemes/configDSEsig.py -o TimingDSEsig.txt -b

echo "Running ACDK test"
python3 runAutoGroup.py --sdl schemes/acdk12.sdl --config schemes/configACDK.py -o TimingACDK.txt -b

##echo "Running DFA experiment"
##python3 runAutoGroup.py --sdl schemes/dfa12.sdl --config configDFA -o TimingDFA.txt -b
