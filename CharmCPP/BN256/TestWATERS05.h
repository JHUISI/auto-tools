#ifndef WATERS05_H
#define WATERS05_H
/* minimize SIG */

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
	
	void setup(G1 & msk, CharmList & smpk, CharmList & vmpk);
	void keygen(CharmList & smpk, G1 & msk, string & ID, CharmList & sk);
	void sign(CharmList & smpk, CharmList & sk, string & M, CharmList & sig);
	bool verify(CharmList & vmpk, string & ID, string & M, CharmList & sig);
};


#endif
