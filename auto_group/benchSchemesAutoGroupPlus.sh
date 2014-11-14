#!/bin/bash

echo "Running Waters09 DSE experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/dse09.sdl --config schemes/configWATERS09.py -o TimingWaters09.txt -b
done

echo "Running Waters05 DSE experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/waters05IBE.sdl --config schemes/configWATERS05IBE.py -o TimingWaters05.txt -b
done

echo "Running GentryIBE experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/gentry06.sdl --config schemes/configGIBE.py -o TimingGentry06.txt -b
done

echo "Running BB04IBE experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/BB04IBE.sdl --config schemes/configBB04IBE.py -o TimingBB04IBE.txt -b
done

echo "Running BGW05 experiment"
for i in {1..10}
do
    python3 runAutoGroup.py --sdl schemes/bgw05.sdl --config schemes/configBGW.py -o TimingBGW05.txt -b
done
