#!/bin/bash

trials=$1

echo "Running BBIBE experiment"
for i in {1..trials}
do
    python runAutoGroup.py schemes/bbibe04.sdl configBBIBE TimingBB.txt
done

echo "Running GentryIBE experiment"
for i in {1..trials}
do
    python runAutoGroup.py schemes/gentry06.sdl configGIBE TimingGentry.txt
done

echo "Running GentryIBE experiment"
for i in {1..trials}
do
    python runAutoGroup.py schemes/bgw05.sdl configBGW TimingBGW.txt
done

echo "Running DFA experiment"
for i in {1..trials}
do
    python runAutoGroup.py schemes/dfa12.sdl configDFA TimingDFA.txt
done

echo "Running CL experiment"
for i in {1..trials}
do
    python runAutoGroup.py schemes/cl04.sdl configCL TimingCL.txt
done

echo "Running BBSig experiment"
for i in {1..trials}
do
    python runAutoGroup.py schemes/bbssig04.sdl configBBSig TimingBBsig.txt
done

echo "Running Waters05 experiment"
for i in {1..trials}
do
    python runAutoGroup.py schemes/waters05.sdl configWATERS05 TimingWATERS.txt
done

echo "Running DSE experiment"
for i in {1..trials}
do
    python runAutoGroup.py schemes/dse09sig.sdl configDSESig TimingDSE.txt
done

echo "Running ACDK experiment"
for i in {1..trials}
do
    python runAutoGroup.py schemes/acdk12.sdl configACDK TimingACDK.txt
done
