#ifndef WATERS05_H
#define WATERS05_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Waters05
{
public:
	PairingGroup group;
	Waters05() { group.setCurve(BN256); };
	~Waters05() {};
	
	void keygen(CharmList & sk, CharmList & chpk, CharmList & spk, CharmList & vpk);
	void sign(CharmList & chpk, CharmList & spk, CharmList & sk, ZR & M, CharmList & sig);
	bool verify(CharmList & chpk, CharmList & vpk, ZR & M, CharmList & sig);
	ZR chamH(CharmList & chpk, ZR & t0, ZR & t1);
};


#endif
