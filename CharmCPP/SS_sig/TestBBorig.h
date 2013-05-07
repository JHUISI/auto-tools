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
	
	void keygen(CharmList & sk, CharmList & pk);
	void sign(CharmList & pk, CharmList & sk, ZR & m, CharmList & sig);
	bool verify(CharmList & pk, ZR & m, CharmList & sig);
};


#endif
