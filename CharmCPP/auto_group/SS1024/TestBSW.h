#ifndef BSW07_H
#define BSW07_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Bsw07
{
public:
	PairingGroup group;
	Bsw07() { group.setCurve(SS1024); };
	~Bsw07() {};
	SecretUtil util;

	void setup(CharmList & mk, CharmList & pk);
	void keygen(CharmList & pk, CharmList & mk, CharmListStr & S, CharmList & sk);
	void encrypt(CharmList & pk, GT & M, NO_TYPE & policyUSstr, CharmList & ct);
	void decrypt(CharmList & pk, CharmList & sk, CharmListStr & S, CharmList & ct, GT & M);
};


#endif
