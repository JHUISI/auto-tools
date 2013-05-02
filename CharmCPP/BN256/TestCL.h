#ifndef CL04_H
#define CL04_H
/* minimize PK */

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
	
	void setup(G1 & gG1);
	void keygen(G1 & gG1, CharmList & sk, CharmList & spk, CharmList & vpk);
	void sign(CharmList & sk, string & M, CharmList & sig);
	bool verify(CharmList & vpk, G1 & gG1, string & M, CharmList & sig);
};


#endif
