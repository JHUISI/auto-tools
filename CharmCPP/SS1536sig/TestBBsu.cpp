#include "TestBBsu.h"

void Bbssig04::keygen(CharmList & sk, CharmList & pk, CharmList & chpk)
{
    G1 g;
    ZR x;
    ZR y;
    G1 u;
    G1 v;
    GT z = group.init(GT_t);
    ZR chK;
    ZR cht;
    G1 ch0;
    G1 ch1;
    g = group.random(G1_t);
    x = group.random(ZR_t);
    y = group.random(ZR_t);
    u = group.exp(g, x);
    v = group.exp(g, y);
    z = group.pair(g, g);
    chK = group.random(ZR_t);
    cht = group.random(ZR_t);
    ch0 = group.random(G1_t);
    ch1 = group.exp(ch0, cht);
    chpk.insert(0, ch0);
    chpk.insert(1, ch1);
    sk.insert(0, cht);
    sk.insert(1, chK);
    sk.insert(2, x);
    sk.insert(3, y);
    pk.insert(0, chK);
    pk.insert(1, g);
    pk.insert(2, u);
    pk.insert(3, v);
    pk.insert(4, z);
    return;
}

void Bbssig04::sign(CharmList & chpk, CharmList & pk, CharmList & sk, ZR & m, CharmList & sig)
{
    ZR chK;
    G1 g;
    G1 u;
    G1 v;
    GT z;
    ZR cht;
//    ZR chK;
    ZR x;
    ZR y;
    ZR r;
    ZR s0;
    ZR s1;
    ZR mpr;
    G1 S;
    
    chK = pk[0].getZR();
    g = pk[1].getG1();
    u = pk[2].getG1();
    v = pk[3].getG1();
    z = pk[4].getGT();
    
    cht = sk[0].getZR();
    chK = sk[1].getZR();
    x = sk[2].getZR();
    y = sk[3].getZR();
    r = group.random(ZR_t);
    s0 = group.random(ZR_t);
    s1 = group.hashListToZR((Element(chK) + Element(m) + Element(r)));
    mpr = chamH(chpk, s1, s0);
    if ( ( (group.add(group.add(x, mpr), group.mul(y, r))) != (0) ) )
    {
        S = group.exp(g, group.div(1, group.add(group.add(x, mpr), group.mul(y, r))));
    }
    else
    {
        return; // return false;
    }
    sig.insert(0, S);
    sig.insert(1, r);
    sig.insert(2, s0);
    return;
}

bool Bbssig04::verify(CharmList & chpk, CharmList & pk, ZR & m, CharmList & sig)
{
    ZR chK;
    G1 g;
    G1 u;
    G1 v;
    GT z;
    G1 S;
    ZR r;
    ZR s0;
    ZR s1;
    ZR mpr;
    
    chK = pk[0].getZR();
    g = pk[1].getG1();
    u = pk[2].getG1();
    v = pk[3].getG1();
    z = pk[4].getGT();
    
    S = sig[0].getG1();
    r = sig[1].getZR();
    s0 = sig[2].getZR();
    s1 = group.hashListToZR((Element(chK) + Element(m) + Element(r)));
    mpr = chamH(chpk, s1, s0);
    if ( ( (group.pair(S, group.mul(group.mul(u, group.exp(g, mpr)), group.exp(v, r)))) == (z) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

ZR Bbssig04::chamH(CharmList & chpk, ZR & t0, ZR & t1)
{
    G1 ch0;
    G1 ch1;
    G1 chVal;
    ZR chZr;
    
    ch0 = chpk[0].getG1();
    ch1 = chpk[1].getG1();
    chVal = group.mul(group.exp(ch0, t0), group.exp(ch1, t1));
    chZr = group.hashListToZR((Element(1) + Element(chVal)));
    return chZr;
}

