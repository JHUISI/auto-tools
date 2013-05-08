#ifndef ACDK12_H
#define ACDK12_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Acdk12
{
public:
	PairingGroup group;
	Acdk12() { group.setCurve(BN256); };
	~Acdk12() {};
	
	void setup(CharmList & gk);
	void keygen(CharmList & gk, CharmList & sk, CharmList & svk, CharmList & vvk);
	void sign(CharmList & gk, CharmList & svk, CharmList & sk, ZR & m1, ZR & m2, CharmList & M, CharmList & sig);
	bool verify(CharmList & gk, CharmList & vvk, CharmList & M, CharmList & sig);
};


#endif
