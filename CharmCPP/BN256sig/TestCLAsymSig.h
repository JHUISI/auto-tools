#ifndef CL04_H
#define CL04_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Cl04
{
public:
	PairingGroup group;
	Cl04() { group.setCurve(BN256); };
	~Cl04() {};
	
	void setup(G2 & gG2);
	void keygen(G2 & gG2, CharmList & sk, CharmList & chpk, CharmList & spk, CharmList & vpk);
	void sign(CharmList & chpk, CharmList & sk, string & M, CharmList & sig);
	bool verify(CharmList & chpk, CharmList & vpk, G2 & gG2, string & M, CharmList & sig);
	ZR chamH(CharmList & chpk, ZR & t0, ZR & t1);
};


#endif
