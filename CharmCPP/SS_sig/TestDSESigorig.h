#ifndef WATERS09SIG_H
#define WATERS09SIG_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Waters09sig
{
public:
	PairingGroup group;
	Waters09sig() { group.setCurve(SS1536); };
	~Waters09sig() {};
	
	void keygen(CharmList & pk, CharmList & sk);
	void sign(CharmList & pk, CharmList & sk, string & m, CharmList & sig);
	bool verify(CharmList & pk, string & m, CharmList & sig);
};


#endif
