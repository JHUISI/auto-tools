#ifndef CYH_H
#define CYH_H
/* minimize PK */

#include "Charm.h"
#include <iostream>
#include <sstream>
#include <string>
#include <list>
using namespace std;


class Cyh
{
public:
	PairingGroup group;
	Cyh() { group.setCurve(BN256); };
	~Cyh() {};
	
	void setup(G2 & P, G2 & gG2, ZR & alpha);
	void keygen(ZR & alpha, string & ID, G1 & pk, G1 & sk);
	void sign(string & ID, CharmListStr & ID_list, G1 & pk, G1 & sk, string & M, CharmList & sig);
	bool verify(G2 & P, G2 & gG2, string & M, CharmList & sig);
};


#endif
