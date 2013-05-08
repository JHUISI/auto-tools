#include "TestWaters05AsymSig.h"

int l = 128;

void Waters05::keygen(CharmList & sk, CharmList & chpk, CharmList & spk, CharmList & vpk)
{
    ZR alpha;
    G1 gG1;
    G2 gG2;
    G1 g1;
    ZR g2;
    G1 g2G1;
    G2 g2G2;
    ZR ut;
    G1 utG1;
    G2 utG2;
    CharmListZR y;
    CharmListG1 uG1;
    CharmListG2 uG2;
    ZR chK;
    ZR cht;
    ZR ch;
    G1 ch0;
    G1 ch1;
    G1 sk0;
    alpha = group.random(ZR_t);
    gG1 = group.random(G1_t);
    gG2 = group.random(G2_t);
    g1 = group.exp(gG1, alpha);
    g2 = group.random(ZR_t);
    g2G1 = group.exp(gG1, g2);
    g2G2 = group.exp(gG2, g2);
    ut = group.random(ZR_t);
    utG1 = group.exp(gG1, ut);
    utG2 = group.exp(gG2, ut);
    for (int i = 0; i < l; i++)
    {
        y[i] = group.random(ZR_t);
        uG1[i] = group.exp(gG1, y[i]);
        uG2[i] = group.exp(gG2, y[i]);
    }
    chK = group.random(ZR_t);
    cht = group.random(ZR_t);
    ch = group.random(ZR_t);
    ch0 = group.exp(gG1, ch);
    ch1 = group.exp(ch0, cht);
    chpk.insert(0, ch0);
    chpk.insert(1, ch1);
    sk0 = group.exp(g2G1, alpha);
    sk.insert(0, sk0);
    sk.insert(1, chK);
    sk.insert(2, cht);
    spk.insert(0, g2G1);
    spk.insert(1, gG1);
    spk.insert(2, gG2);
    spk.insert(3, uG1);
    spk.insert(4, utG1);
    vpk.insert(0, g1);
    vpk.insert(1, g2G2);
    vpk.insert(2, gG2);
    vpk.insert(3, uG2);
    vpk.insert(4, utG2);
    vpk.insert(5, chK);
    return;
}

void Waters05::sign(CharmList & chpk, CharmList & spk, CharmList & sk, ZR & M, CharmList & sig)
{
    G1 sk0;
    ZR chK;
    ZR cht;
    G1 g2G1;
    G1 gG1;
    G2 gG2;
    CharmListG1 uG1;
    G1 utG1;
    ZR r;
    G1 S2;
    ZR s0;
    ZR s1;
    ZR Mpr;
    CharmListZR m;
    G1 dotProd1 = group.init(G1_t, 1);
    G1 S1;
    
    sk0 = sk[0].getG1();
    chK = sk[1].getZR();
    cht = sk[2].getZR();
    
    g2G1 = spk[0].getG1();
    gG1 = spk[1].getG1();
    gG2 = spk[2].getG2();
    uG1 = spk[3].getListG1();
    utG1 = spk[4].getG1();
    r = group.random(ZR_t);
    S2 = group.exp(gG1, r);
    s0 = group.random(ZR_t);
    s1 = group.hashListToZR((Element(chK) + Element(M) + Element(S2)));
    Mpr = chamH(chpk, s1, s0);
    m = intToBits(Mpr, l);
    group.init(dotProd1, 1);
    for (int i = 0; i < l; i++)
    {
        dotProd1 = group.mul(dotProd1, group.exp(uG1[i], m[i]));
    }
    S1 = group.mul(sk0, group.exp(group.mul(utG1, dotProd1), r));
    sig.insert(0, S1);
    sig.insert(1, S2);
    sig.insert(2, s0);
    return;
}

bool Waters05::verify(CharmList & chpk, CharmList & vpk, ZR & M, CharmList & sig)
{
    G1 g1;
    G2 g2G2;
    G2 gG2;
    CharmListG2 uG2;
    G2 utG2;
    G1 S1;
    G1 S2;
    ZR s0;
    ZR s1;
    ZR Mpr;
    CharmListZR m;
    G2 dotProd2 = group.init(G2_t, 1);
    
    g1 = vpk[0].getG1();
    g2G2 = vpk[1].getG2();
    gG2 = vpk[2].getG2();
    uG2 = vpk[3].getListG2();
    utG2 = vpk[4].getG2();
    ZR chK = vpk[5].getZR(); // should be in chpk
    
    S1 = sig[0].getG1();
    S2 = sig[1].getG1();
    s0 = sig[2].getZR();
    s1 = group.hashListToZR((Element(chK) + Element(M) + Element(S2)));
    Mpr = chamH(chpk, s1, s0);
    m = intToBits(Mpr, l);
    group.init(dotProd2, 1);
    for (int i = 0; i < l; i++)
    {
        dotProd2 = group.mul(dotProd2, group.exp(uG2[i], m[i]));
    }
    if ( ( (group.div(group.pair(S1, gG2), group.pair(S2, group.mul(utG2, dotProd2)))) == (group.pair(g1, g2G2)) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

ZR Waters05::chamH(CharmList & chpk, ZR & t0, ZR & t1)
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

