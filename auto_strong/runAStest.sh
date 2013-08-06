#!/bin/bash

echo "Running CL experiment"
for i in {1..10}
do
    python runAutoStrong.py --sdl schemes/cl04.sdl --config configCL -o TimingCL.txt -b
done

echo "Running BBSig experiment"
for i in {1..10}
do
    python runAutoStrong.py --sdl schemes/bbssig04.sdl --config configBBSig -o TimingBBsig.txt -b
done

echo "Running Waters05 experiment"
for i in {1..10}
do
    python runAutoStrong.py --sdl schemes/waters05.sdl --config configWATERS05 -o TimingWATERS.txt -b
done

echo "Running DSEsig experiment"
for i in {1..10}
do
    python runAutoStrong.py --sdl schemes/dse09sig.sdl --config configDSEsig -o TimingDSE.txt -b
done

echo "Running ACDK experiment"
for i in {1..10}
do
    python runAutoStrong.py --sdl schemes/acdk12.sdl --config configACDK12 -o TimingACDK.txt -b -t
done
