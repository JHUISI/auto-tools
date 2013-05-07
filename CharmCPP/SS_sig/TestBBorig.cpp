#include "TestBBorig.h"

void Bbssig04::keygen(CharmList & sk, CharmList & pk)
{
    G1 g;
    ZR x;
    ZR y;
    G1 u;
    G1 v;
    GT z = group.init(GT_t);
    g = group.random(G1_t);
    x = group.random(ZR_t);
    y = group.random(ZR_t);
    u = group.exp(g, x);
    v = group.exp(g, y);
    z = group.pair(g, g);
    sk.insert(0, x);
    sk.insert(1, y);
    pk.insert(0, g);
    pk.insert(1, u);
    pk.insert(2, v);
    pk.insert(3, z);
    return;
}

void Bbssig04::sign(CharmList & pk, CharmList & sk, ZR & m, CharmList & sig)
{
    G1 g;
    G1 u;
    G1 v;
    GT z;
    ZR x;
    ZR y;
    ZR r;
    G1 S;
    
    g = pk[0].getG1();
    u = pk[1].getG1();
    v = pk[2].getG1();
    z = pk[3].getGT();
    
    x = sk[0].getZR();
    y = sk[1].getZR();
    r = group.random(ZR_t);
    if ( ( (group.add(group.add(x, m), group.mul(y, r))) != (0) ) )
    {
        S = group.exp(g, group.div(1, group.add(group.add(x, m), group.mul(y, r))));
    }
    else
    {
        return; // return false; ==> fix type
    }
    sig.insert(0, S);
    sig.insert(1, r);
    return;
}

bool Bbssig04::verify(CharmList & pk, ZR & m, CharmList & sig)
{
    G1 g;
    G1 u;
    G1 v;
    GT z;
    G1 S;
    ZR r;
    
    g = pk[0].getG1();
    u = pk[1].getG1();
    v = pk[2].getG1();
    z = pk[3].getGT();
    
    S = sig[0].getG1();
    r = sig[1].getZR();
    if ( ( (group.pair(S, group.mul(group.mul(u, group.exp(g, m)), group.exp(v, r)))) == (z) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

