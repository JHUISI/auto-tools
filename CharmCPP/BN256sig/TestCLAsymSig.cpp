#include "TestCLAsymSig.h"

void Cl04::setup(G2 & gG2)
{
    gG2 = group.random(G2_t);
    return;
}

void Cl04::keygen(G2 & gG2, CharmList & sk, CharmList & chpk, CharmList & spk, CharmList & vpk)
{
    ZR x;
    ZR y;
    G2 X;
    G2 Y;
    ZR chK;
    ZR cht;
    G1 ch0;
    G1 ch1;
    x = group.random(ZR_t);
    y = group.random(ZR_t);
    X = group.exp(gG2, x);
    Y = group.exp(gG2, y);
    chK = group.random(ZR_t);
    cht = group.random(ZR_t);
    ch0 = group.random(G1_t);
    ch1 = group.exp(ch0, cht);
    chpk.insert(0, ch0); // fix in AS
    chpk.insert(1, ch1);
    sk.insert(0, cht);
    sk.insert(1, chK);
    sk.insert(2, x);
    sk.insert(3, y);
    //spk = list; // TODO: remove if spk list is empty
    vpk.insert(0, X);
    vpk.insert(1, Y);
    vpk.insert(2, chK); // fix in AS. Always add this to vpk
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

bool Cl04::verify(CharmList & chpk, CharmList & vpk, G2 & gG2, string & M, CharmList & sig)
{
    G1 a;
    G1 b;
    G1 c;
    ZR s0;
    G2 X;
    G2 Y;
    ZR m;
    ZR s1;
    ZR mpr;
    ZR chK;
    
    a = sig[0].getG1();
    b = sig[1].getG1();
    c = sig[2].getG1();
    s0 = sig[3].getZR();
    
    X = vpk[0].getG2();
    Y = vpk[1].getG2();
    chK = vpk[2].getZR();
    m = group.hashListToZR(M);
    s1 = group.hashListToZR((Element(chK) + Element(m) + Element(a) + Element(b)));
    mpr = chamH(chpk, s1, s0);
    if ( ( (( (group.pair(a, Y)) == (group.pair(b, gG2)) )) && (( (group.pair(group.mul(a, group.exp(b, mpr)), X)) == (group.pair(c, gG2)) )) ) )
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

