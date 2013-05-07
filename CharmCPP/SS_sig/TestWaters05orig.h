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
	Waters05() { group.setCurve(SS1536); };
	~Waters05() {};
	
	void keygen(CharmList & pk, G1 & sk);
	void sign(CharmList & pk, G1 & sk, ZR & M, CharmList & sig);
	bool verify(CharmList & pk, ZR & M, CharmList & sig);
};


#endif
