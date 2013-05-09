#!/bin/bash

echo "Running CL experiment"
for i in {1..10}
do
    python runAutoGroup.py schemes/cl04.sdl configCL TimingCL.txt
done

echo "Running BBSig experiment"
for i in {1..10}
do
    python runAutoGroup.py schemes/bbssig04.sdl configBBSig TimingBBsig.txt
done

echo "Running Waters05 experiment"
for i in {1..10}
do
    python runAutoGroup.py schemes/waters05.sdl configWATERS05 TimingWATERS.txt
done

#echo "Running DSEsig experiment"
#for i in {1..10}
#do
#    python runAutoGroup.py schemes/dse09sig.sdl configDSEsig TimingDSE.txt
#done

echo "Running ACDK experiment"
for i in {1..10}
do
    python runAutoGroup.py schemes/acdk12.sdl configACDK TimingACDK.txt
done
