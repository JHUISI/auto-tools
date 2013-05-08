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
	Bbssig04() { group.setCurve(SS1536); };
	~Bbssig04() {};
	
	void keygen(CharmList & sk, CharmList & pk, CharmList & chpk);
	void sign(CharmList & chpk, CharmList & pk, CharmList & sk, ZR & m, CharmList & sig);
	bool verify(CharmList & chpk, CharmList & pk, ZR & m, CharmList & sig);
	ZR chamH(CharmList & chpk, ZR & t0, ZR & t1);
};


#endif
