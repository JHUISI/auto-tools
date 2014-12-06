#!/bin/bash

cleanup() {
    # do some cleaning here
    rm *.txt *.sdl
    exit $1
}

echo "Running all encryption experiments..."
echo "Waters09 DSE experiment"
for i in {1..1}
do
    echo "***************************Min PK********************************"
    python3 runAutoGroup.py --sdl schemes/dse09.sdl --config schemes/configWATERS09.py --short public-keys -o TimingWaters09.txt -b || cleanup 1
    echo "***************************Min AS********************************"
    python3 runAutoGroup.py --sdl schemes/dse09.sdl --config schemes/configWATERS09.py --short assumption -o TimingWaters09.txt -b || cleanup 1
    echo "***************************Min SK********************************"
    python3 runAutoGroup.py --sdl schemes/dse09.sdl --config schemes/configWATERS09.py --short secret-keys -o TimingWaters09.txt -b || cleanup 1
    echo "***************************Min CT********************************"
    python3 runAutoGroup.py --sdl schemes/dse09.sdl --config schemes/configWATERS09.py --short ciphertext -o TimingWaters09.txt -b || cleanup 1
done

echo "Waters05 DSE experiment"
for i in {1..1}
do
    echo "***************************Min PK********************************"
    python3 runAutoGroup.py --sdl schemes/waters05IBE.sdl --config schemes/configWATERS05IBE.py --short public-keys -o TimingWaters05.txt -b || cleanup 1
    echo "***************************Min AS********************************"
    python3 runAutoGroup.py --sdl schemes/waters05IBE.sdl --config schemes/configWATERS05IBE.py --short assumption -o TimingWaters05.txt -b || cleanup 1
    echo "***************************Min SK********************************"
    python3 runAutoGroup.py --sdl schemes/waters05IBE.sdl --config schemes/configWATERS05IBE.py --short secret-keys -o TimingWaters05.txt -b || cleanup 1
    echo "***************************Min CT********************************"
    python3 runAutoGroup.py --sdl schemes/waters05IBE.sdl --config schemes/configWATERS05IBE.py --short ciphertext -o TimingWaters05.txt -b || cleanup 1
done

echo "GentryIBE experiment"
for i in {1..1}
do
    echo "***************************Min PK********************************"
    python3 runAutoGroup.py --sdl schemes/gentry06.sdl --config schemes/configGIBE.py --short public-keys -o TimingGentry06.txt -b || cleanup 1
    echo "***************************Min AS********************************"
    python3 runAutoGroup.py --sdl schemes/gentry06.sdl --config schemes/configGIBE.py --short assumption -o TimingGentry06.txt -b || cleanup 1
    echo "***************************Min SK********************************"
    python3 runAutoGroup.py --sdl schemes/gentry06.sdl --config schemes/configGIBE.py --short secret-keys -o TimingGentry06.txt -b || cleanup 1
    echo "***************************Min CT********************************"
    python3 runAutoGroup.py --sdl schemes/gentry06.sdl --config schemes/configGIBE.py --short ciphertext -o TimingGentry06.txt -b || cleanup 1
done

#echo "Running BB04IBE experiment"
#for i in {1..2}
#do
#    python3 runAutoGroup.py --sdl schemes/BB04IBE.sdl --config schemes/configBB04IBE.py --short public-keys -o TimingBB04IBE.txt -b || cleanup 1
#    python3 runAutoGroup.py --sdl schemes/BB04IBE.sdl --config schemes/configBB04IBE.py --short assumption -o TimingBB04IBE.txt -b || cleanup 1
#    python3 runAutoGroup.py --sdl schemes/BB04IBE.sdl --config schemes/configBB04IBE.py --short secret-keys -o TimingBB04IBE.txt -b || cleanup 1
#    python3 runAutoGroup.py --sdl schemes/BB04IBE.sdl --config schemes/configBB04IBE.py --short ciphertext -o TimingBB04IBE.txt -b || cleanup 1
#done
#
#echo "Running BGW05 experiment"
#for i in {1..2}
#do
#    python3 runAutoGroup.py --sdl schemes/bgw05.sdl --config schemes/configBGW.py --short public-keys -o TimingBGW05.txt -b || cleanup 1
#    python3 runAutoGroup.py --sdl schemes/bgw05.sdl --config schemes/configBGW.py --short assumption -o TimingBGW05.txt -b || cleanup 1
#    python3 runAutoGroup.py --sdl schemes/bgw05.sdl --config schemes/configBGW.py --short secret-keys -o TimingBGW05.txt -b || cleanup 1
#    python3 runAutoGroup.py --sdl schemes/bgw05.sdl --config schemes/configBGW.py --short ciphertext -o TimingBGW05.txt -b || cleanup 1
#done

cleanup 0