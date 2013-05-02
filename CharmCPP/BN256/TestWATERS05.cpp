#include "TestWATERS05.h"

void Waters05::setup(G1 & msk, CharmList & smpk, CharmList & vmpk)
{
    ZR alpha;
    G1 hG1;
    G2 hG2;
    ZR g;
    G1 gG1;
    G2 gG2;
    GT A = group.init(GT_t);
    CharmListZR y0;
    CharmListG1 u;
    CharmListG2 ub;
    ZR y1t;
    ZR y2t;
    G1 u1t;
    G1 u2t;
    G2 u1b;
    G2 u2b;
    alpha = group.random(ZR_t);
    hG1 = group.random(G1_t);
    hG2 = group.random(G2_t);
    g = group.random(ZR_t);
    gG1 = group.exp(hG1, g);
    gG2 = group.exp(hG2, g);
    A = group.exp(group.pair(hG1, gG2), alpha);
    for (int i = 0; i < l; i++)
    {
        y0[i] = group.random(ZR_t);
        u[i] = group.exp(gG1, y0[i]);
        ub[i] = group.exp(gG2, y0[i]);
    }
    y1t = group.random(ZR_t);
    y2t = group.random(ZR_t);
    u1t = group.exp(gG1, y1t);
    u2t = group.exp(gG1, y2t);
    u1b = group.exp(gG2, y1t);
    u2b = group.exp(gG2, y2t);
    msk = group.exp(hG1, alpha);
    smpk.insert(0, gG1);
    smpk.insert(1, u);
    smpk.insert(2, u1t);
    smpk.insert(3, u2t);
    vmpk.insert(0, A);
    vmpk.insert(1, gG2);
    vmpk.insert(2, u1b);
    vmpk.insert(3, u2b);
    vmpk.insert(4, ub);
    return;
}

void Waters05::keygen(CharmList & smpk, G1 & msk, string & ID, CharmList & sk)
{
    G1 gG1;
    CharmListG1 u;
    G1 u1t;
    G1 u2t;
    CharmListZR k;
    G1 dotProd = group.init(G1_t, 1);
    ZR r;
    G1 k1;
    G1 k2;
    
    gG1 = smpk[0].getG1();
    u = smpk[1].getListG1();
    u1t = smpk[2].getG1();
    u2t = smpk[3].getG1();
    k = stringToInt(group, ID, l, zz);
    group.init(dotProd, 1);
    for (int i = 0; i < l; i++)
    {
        dotProd = group.mul(dotProd, group.exp(u[i], k[i]));
    }
    r = group.random(ZR_t);
    k1 = group.mul(msk, group.exp(group.mul(u1t, dotProd), r));
    k2 = group.exp(gG1, group.neg(r));
    sk.insert(0, k1);
    sk.insert(1, k2);
    return;
}

void Waters05::sign(CharmList & smpk, CharmList & sk, string & M, CharmList & sig)
{
    G1 gG1;
    CharmListG1 u;
    G1 u1t;
    G1 u2t;
    CharmListZR m;
    G1 k1;
    G1 k2;
    ZR s;
    G1 dotProd1 = group.init(G1_t, 1);
    G1 S1;
    G1 S2;
    G1 S3;
    
    gG1 = smpk[0].getG1();
    u = smpk[1].getListG1();
    u1t = smpk[2].getG1();
    u2t = smpk[3].getG1();
    m = stringToInt(group, M, l, zz);
    
    k1 = sk[0].getG1();
    k2 = sk[1].getG1();
    s = group.random(ZR_t);
    group.init(dotProd1, 1);
    for (int i = 0; i < l; i++)
    {
        dotProd1 = group.mul(dotProd1, group.exp(u[i], m[i]));
    }
    S1 = group.mul(k1, group.exp(group.mul(u2t, dotProd1), s));
    S2 = k2;
    S3 = group.exp(gG1, group.neg(s));
    sig.insert(0, S1);
    sig.insert(1, S2);
    sig.insert(2, S3);
    return;
}

bool Waters05::verify(CharmList & vmpk, string & ID, string & M, CharmList & sig)
{
    GT A;
    G2 gG2;
    G2 u1b;
    G2 u2b;
    CharmListG2 ub;
    G1 S1;
    G1 S2;
    G1 S3;
    CharmListZR kver;
    CharmListZR mver;
    G2 dotProd2 = group.init(G2_t, 1);
    G2 dotProd3 = group.init(G2_t, 1);
    
    A = vmpk[0].getGT();
    gG2 = vmpk[1].getG2();
    u1b = vmpk[2].getG2();
    u2b = vmpk[3].getG2();
    ub = vmpk[4].getListG2();
    
    S1 = sig[0].getG1();
    S2 = sig[1].getG1();
    S3 = sig[2].getG1();
    kver = stringToInt(group, ID, l, zz);
    mver = stringToInt(group, M, l, zz);
    group.init(dotProd2, 1);
    group.init(dotProd3, 1);
    for (int i = 0; i < l; i++)
    {
        dotProd2 = group.mul(dotProd2, group.exp(ub[i], kver[i]));
        dotProd3 = group.mul(dotProd3, group.exp(ub[i], mver[i]));
    }
    if ( ( (group.mul(group.mul(group.pair(S1, gG2), group.pair(S2, group.mul(u1b, dotProd2))), group.pair(S3, group.mul(u2b, dotProd3)))) == (A) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

