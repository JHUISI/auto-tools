#ifndef DSEWATERS09_H
#define DSEWATERS09_H

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Dsewaters09
{
public:
	PairingGroup group;
	Dsewaters09() { group.setCurve(AES_SECURITY); };
	~Dsewaters09() {};
	
	void setup(CharmList & mpk, CharmList & msk);
	void keygen(CharmList & mpk, CharmList & msk, string & id, ZR & uf0, ZR & bf0, ZR & uf1, CharmList & skBlinded);
	void encrypt(CharmList & mpk, GT & M, string & id, CharmList & ct);
	void transform(CharmList & ct, CharmList & skBlinded, CharmList & transformOutputList);
	void decout(CharmList & transformOutputList, ZR & bf0, ZR & uf0, ZR & uf1, GT & M);
};


#endif