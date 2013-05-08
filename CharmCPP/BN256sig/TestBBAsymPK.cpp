#include "TestBBAsymPK.h"

void Bbssig04::keygen(CharmList & sk, CharmList & chpk, CharmList & spk, CharmList & vpk)
{
    G1 gG1;
    G2 gG2;
    ZR x;
    ZR y;
    G1 u;
    G1 v;
    GT z = group.init(GT_t);
    ZR chK;
    ZR cht;
    ZR ch0;
    G2 ch0G2;
    G2 ch1;
    gG1 = group.random(G1_t);
    gG2 = group.random(G2_t);
    x = group.random(ZR_t);
    y = group.random(ZR_t);
    u = group.exp(gG1, x);
    v = group.exp(gG1, y);
    z = group.pair(gG1, gG2);
    chK = group.random(ZR_t);
    cht = group.random(ZR_t);
    ch0 = group.random(ZR_t);
    ch0G2 = group.exp(gG2, ch0);
    ch1 = group.exp(ch0G2, cht);
    chpk.insert(0, ch0G2);
    chpk.insert(1, ch1);
    sk.insert(0, cht);
    sk.insert(1, chK);
    sk.insert(2, x);
    sk.insert(3, y);
    spk.insert(0, gG1);
    spk.insert(1, gG2);
    spk.insert(2, z);
    vpk.insert(0, gG1);
    vpk.insert(1, u);
    vpk.insert(2, v);
    vpk.insert(3, z);
    vpk.insert(4, chK);
    return;
}

void Bbssig04::sign(CharmList & chpk, CharmList & spk, CharmList & sk, ZR & m, CharmList & sig)
{
    G1 gG1;
    G2 gG2;
    GT z;
    ZR cht;
    ZR chK;
    ZR x;
    ZR y;
    ZR r;
    ZR s0;
    ZR s1;
    ZR mpr;
    G2 S;
    
    gG1 = spk[0].getG1();
    gG2 = spk[1].getG2();
    z = spk[2].getGT();
    
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
        S = group.exp(gG2, group.div(1, group.add(group.add(x, mpr), group.mul(y, r))));
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

bool Bbssig04::verify(CharmList & chpk, CharmList & vpk, ZR & m, CharmList & sig)
{
    G1 gG1;
    G1 u;
    G1 v;
    GT z;
    G2 S;
    ZR r;
    ZR s0;
    ZR s1;
    ZR mpr, chK;
    
    gG1 = vpk[0].getG1();
    u = vpk[1].getG1();
    v = vpk[2].getG1();
    z = vpk[3].getGT();
    chK = vpk[4].getZR(); // TODO: tweak this
    S = sig[0].getG2();
    r = sig[1].getZR();
    s0 = sig[2].getZR();
    s1 = group.hashListToZR((Element(chK) + Element(m) + Element(r)));
    mpr = chamH(chpk, s1, s0);
    if ( ( (group.pair(group.mul(u, group.mul(group.exp(gG1, mpr), group.exp(v, r))), S)) == (z) ) )
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
    G2 ch0G2;
    G2 ch1;
    G2 chVal;
    ZR chZr;
    
    ch0G2 = chpk[0].getG2();
    ch1 = chpk[1].getG2();
    chVal = group.mul(group.exp(ch0G2, t0), group.exp(ch1, t1));
    chZr = group.hashListToZR((Element(1) + Element(chVal)));
    return chZr;
}

