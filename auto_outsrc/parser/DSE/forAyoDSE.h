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
	void keygen(CharmList & mpk, CharmList & msk, string & id, ZR & bf0, ZR & uf1, ZR & uf0, CharmList & skBlinded);
	void encrypt(CharmList & mpk, GT & M, string & id, CharmList & ct);
	void transform(CharmList & ct, CharmList & skBlinded, CharmList & transformOutputList);
	void decout(CharmList & transformOutputList, ZR & bf0, ZR & uf0, ZR & uf1, GT & M);
};


#endif