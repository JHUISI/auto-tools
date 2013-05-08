#include "TestCLsu.h"

void Cl04::setup(G1 & g)
{
    g = group.random(G1_t);
    return;
}

void Cl04::keygen(G1 & g, CharmList & pk, CharmList & sk, CharmList & chpk)
{
    ZR x;
    ZR y;
    G1 X;
    G1 Y;
    ZR chK;
    ZR cht;
    G1 ch0;
    G1 ch1;
    x = group.random(ZR_t);
    y = group.random(ZR_t);
    X = group.exp(g, x);
    Y = group.exp(g, y);
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
    pk.insert(1, X);
    pk.insert(2, Y);
    return;
}

void Cl04::sign(CharmList & chpk, CharmList & sk, string & M, CharmList & sig)
{
    ZR cht;
    ZR chK;
    ZR x;
    ZR y;
    G1 a;
    ZR m;
    G1 b;
    ZR s0;
    ZR s1;
    ZR mpr;
    G1 c;
    
    cht = sk[0].getZR();
    chK = sk[1].getZR();
    x = sk[2].getZR();
    y = sk[3].getZR();
    a = group.random(G1_t);
    m = group.hashListToZR(M);
    b = group.exp(a, y);
    s0 = group.random(ZR_t);
    s1 = group.hashListToZR((Element(chK) + Element(m) + Element(a) + Element(b)));
    mpr = chamH(chpk, s1, s0);
    c = group.exp(a, group.add(x, group.mul(group.mul(mpr, x), y)));
    sig.insert(0, a);
    sig.insert(1, b);
    sig.insert(2, c);
    sig.insert(3, s0);
    return;
}

bool Cl04::verify(CharmList & chpk, CharmList & pk, G1 & g, string & M, CharmList & sig)
{
    G1 a;
    G1 b;
    G1 c;
    ZR s0;
    ZR chK;
    G1 X;
    G1 Y;
    ZR m;
    ZR s1;
    ZR mpr;
    
    a = sig[0].getG1();
    b = sig[1].getG1();
    c = sig[2].getG1();
    s0 = sig[3].getZR();
    
    chK = pk[0].getZR();
    X = pk[1].getG1();
    Y = pk[2].getG1();
    m = group.hashListToZR(M);
    s1 = group.hashListToZR((Element(chK) + Element(m) + Element(a) + Element(b)));
    mpr = chamH(chpk, s1, s0);
    if ( ( (( (group.pair(a, Y)) == (group.pair(g, b)) )) && (( (group.mul(group.pair(X, a), group.exp(group.pair(X, b), mpr))) == (group.pair(g, c)) )) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

ZR Cl04::chamH(CharmList & chpk, ZR & t0, ZR & t1)
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

