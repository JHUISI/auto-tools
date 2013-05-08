#ifndef DSE09SIG_H
#define DSE09SIG_H
// REDO: currently broken
#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Dse09sig
{
public:
	PairingGroup group;
	Dse09sig() { group.setCurve(BN256); };
	~Dse09sig() {};
	
	void keygen(CharmList & sk, CharmList & spk, CharmList & vpk);
	void sign(CharmList & spk, CharmList & sk, string & m, CharmList & sig);
	bool verify(CharmList & vpk, string & m, CharmList & sig);
};


#endif
