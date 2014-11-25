#!/bin/bash

#echo "Running Waters09 DSE experiment"
#for i in {1..10}
#do
#    python3 runAutoGroup.py --sdl schemes/dse09.sdl --config schemes/configWATERS09.py -o TimingWaters09.txt -b
#done

echo "Running Waters05 SIG experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/waters05SIG.sdl --config schemes/configWATERS05SIG.py -o TimingWaters05.txt -b
done

echo "Running BLS experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/BLS.sdl --config schemes/configBLS.py -o TimingBLS.txt -b
done


