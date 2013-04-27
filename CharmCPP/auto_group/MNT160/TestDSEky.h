#ifndef DSE09_H
#define DSE09_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Dse09
{
public:
	PairingGroup group;
	Dse09() { group.setCurve(AES_SECURITY); };
	~Dse09() {};
	
	void setup(CharmList & mpk, CharmList & msk);
	void keygen(CharmList & mpk, CharmList & msk, string & id, CharmList & sk);
	void encrypt(CharmList & mpk, GT & M, string & id, CharmList & ct);
	void decrypt(CharmList & ct, CharmList & sk, GT & M);
};


#endif