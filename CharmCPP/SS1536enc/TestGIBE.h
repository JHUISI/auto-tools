#ifndef GENTRY06_H
#define GENTRY06_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Gentry06
{
public:
	PairingGroup group;
	Gentry06() { group.setCurve(SS1536); };
	~Gentry06() {};
	
	void setup(CharmList & mk, CharmList & pk);
	void keygen(CharmList & pk, CharmList & mk, string & id, CharmList & sk);
	void encrypt(CharmList & pk, GT & m, string & id, CharmList & ct);
	void decrypt(CharmList & sk, CharmList & ct, GT & m);
};


#endif
