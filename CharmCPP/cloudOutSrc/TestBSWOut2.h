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
	Bsw07() { group.setCurve(BN256); };
	~Bsw07() {};
	SecretUtil util;

	void setup(CharmList & mk, CharmList & pk);
	void keygen(CharmList & pk, CharmList & mk, CharmListStr & S, ZR & uf0, ZR & bf0, CharmList & skBlinded);
	void encrypt(CharmList & pk, GT & M, string & policyUSstr, CharmList & ct);
	void transform(CharmList & pk, CharmList & skBlinded, CharmListStr & S, CharmList & ct, CharmList & transformOutputList);
	void decout(CharmList & pk, CharmListStr & S, CharmList & transformOutputList, ZR & bf0, ZR & uf0, GT & M);
};


#endif
