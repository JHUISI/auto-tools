#!/bin/bash

#echo "Running Waters09 DSE experiment"
#for i in {1..10}
#do
#    python3 runAutoGroup.py --sdl schemes/dse09.sdl --config schemes/configWATERS09.py -o TimingWaters09.txt -b
#done

echo "Running Waters05 SIG experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/waters05SIG.sdl --config schemes/configWATERS05SIG.py --short "public-keys" -o TimingWaters05.txt -b
done

echo "Running BLS experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/BLS.sdl --config schemes/configBLS.py --short "public-keys" -o TimingBLS.txt -b
done

echo "Running BLS experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/acdk12.sdl --config schemes/configACDK.py --short "public-keys" -o TimingACDKNO.txt -b
done



