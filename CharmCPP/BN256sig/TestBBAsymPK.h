#ifndef BBSSIG04_H
#define BBSSIG04_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Bbssig04
{
public:
	PairingGroup group;
	Bbssig04() { group.setCurve(BN256); };
	~Bbssig04() {};
	
	void keygen(CharmList & sk, CharmList & chpk, CharmList & spk, CharmList & vpk);
	void sign(CharmList & chpk, CharmList & spk, CharmList & sk, ZR & m, CharmList & sig);
	bool verify(CharmList & chpk, CharmList & vpk, ZR & m, CharmList & sig);
	ZR chamH(CharmList & chpk, ZR & t0, ZR & t1);
};


#endif
