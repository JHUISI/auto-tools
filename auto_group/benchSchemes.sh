#!/bin/bash

echo "Running BBIBE experiment"
for i in {1..10}
do
    python3 runAutoGroup.py schemes/bbibe04.sdl --config schemes/configBBIBE.py -o TimingBB.txt -b
done

echo "Running GentryIBE experiment"
for i in {1..10}
do
    python3 runAutoGroup.py schemes/gentry06.sdl --config schemes/configGIBE.py -o TimingGentry.txt -b
done

echo "Running GentryIBE experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/bgw05.sdl --config schemes/configBGW.py -o TimingBGW.txt -b
done

echo "Running DFA experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/dfa12.sdl --config schemes/configDFA.py -o TimingDFA.txt -b
done

echo "Running CL experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/cl04.sdl --config schemes/configCL.py -o TimingCL.txt -b
done

echo "Running BBSig experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/bbssig04.sdl --config schemes/configBBSig.py -o TimingBBsig.txt -b
done

echo "Running Waters05 experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/waters05.sdl --config schemes/configWATERS05.py -o TimingWATERS.txt -b
done

echo "Running DSEsig experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/dse09sig.sdl --config schemes/configDSEsig.py -o TimingDSE.txt -b
done

echo "Running ACDK experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/acdk12.sdl --config schemes/configACDK.py -o TimingACDK.txt -b
done
