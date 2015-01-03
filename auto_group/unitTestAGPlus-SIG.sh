#!/bin/bash

cleanup() {
    # do some cleaning here
    rm *.txt *.sdl
    exit $1
}

#echo "Running all encryption experiments..."
#echo "Waters09 Dual-System sigs experiment"
#for i in {1..1}
#do
#    echo "***************************Min PK********************************"
#    python3 runAutoGroup.py --sdl schemes/dse09sig.sdl --config schemes/configWATERS09.py --short public-keys -o TimingWaters09.txt -b || cleanup 1
#    echo "***************************Min AS********************************"
#    python3 runAutoGroup.py --sdl schemes/dse09sig.sdl --config schemes/configWATERS09.py --short assumption -o TimingWaters09.txt -b || cleanup 1
#    echo "***************************Min SK********************************"
#    python3 runAutoGroup.py --sdl schemes/dse09.sdl --config schemes/configWATERS09.py --short signature -o TimingWaters09.txt -b || cleanup 1
#    #echo "***************************Min CT********************************"
#    #python3 runAutoGroup.py --sdl schemes/dse09.sdl --config schemes/configWATERS09.py --short combo? -o TimingWaters09.txt -b || cleanup 1
#done

echo "Waters05 sigs experiment"
for i in {1..1}
do
    echo "***************************Min PK********************************"
    python3 runAutoGroup.py --sdl schemes/waters05SIG.sdl --config schemes/configWATERS05SIG.py --short public-keys -o TimingWaters05.txt -b || cleanup 1
    echo "***************************Min AS********************************"
    python3 runAutoGroup.py --sdl schemes/waters05SIG.sdl --config schemes/configWATERS05SIG.py --short assumption -o TimingWaters05.txt -b || cleanup 1
    echo "***************************Min SK********************************"
    python3 runAutoGroup.py --sdl schemes/waters05SIG.sdl --config schemes/configWATERS05SIG.py --short signature -o TimingWaters05.txt -b || cleanup 1
    #echo "***************************Min CT********************************"
    #python3 runAutoGroup.py --sdl schemes/waters05SIG.sdl --config schemes/configWATERS05SIG.py --short combo? -o TimingWaters05.txt -b || cleanup 1
done

# TODO: add more signature schemes: TOS, SPS ...
cleanup 0
