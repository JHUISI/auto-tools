#include "TestBBky.h"

void Bbibe04::setup(CharmList & msk, CharmList & pk)
{
    G1 gG1;
    G2 gG2;
    ZR u;
    G1 uG1;
    G2 uG2;
    ZR h;
    G1 hG1;
    G2 hG2;
    ZR alpha;
    GT egg = group.init(GT_t);
    G1 galpha;
    gG1 = group.random(G1_t);
    gG2 = group.random(G2_t);
    u = group.random(ZR_t);
    uG1 = group.exp(gG1, u);
    uG2 = group.exp(gG2, u);
    h = group.random(ZR_t);
    hG1 = group.exp(gG1, h);
    hG2 = group.exp(gG2, h);
    alpha = group.random(ZR_t);
    egg = group.exp(group.pair(gG1, gG2), alpha);
    galpha = group.exp(gG1, alpha);
    msk.insert(0, galpha);
    pk.insert(0, gG1);
    pk.insert(1, gG2);
    pk.insert(2, uG1);
    pk.insert(3, uG2);
    pk.insert(4, hG1);
    pk.insert(5, hG2);
    pk.insert(6, egg);
    return;
}

void Bbibe04::keygen(CharmList & pk, CharmList & msk, NO_TYPE & id, CharmList & sk)
{
    G1 gG1;
    G2 gG2;
    G1 uG1;
    G2 uG2;
    G1 hG1;
    G2 hG2;
    GT egg;
    G1 galpha;
    ZR ID;
    ZR r;
    G1 K1;
    G1 K2;
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    uG1 = pk[2].getG1();
    uG2 = pk[3].getG2();
    hG1 = pk[4].getG1();
    hG2 = pk[5].getG2();
    egg = pk[6].getGT();
    
    galpha = msk[0].getG1();
    ID = group.hashListToZR(id);
    r = group.random(ZR_t);
    K1 = group.exp(group.mul(galpha, group.mul(group.exp(uG1, ID), hG1)), r);
    K2 = group.exp(gG1, r);
    sk.insert(0, K1);
    sk.insert(1, K2);
    return;
}

void Bbibe04::encrypt(CharmList & pk, GT & M, NO_TYPE & id, CharmList & ct)
{
    G1 gG1;
    G2 gG2;
    G1 uG1;
    G2 uG2;
    G1 hG1;
    G2 hG2;
    GT egg;
    ZR ID;
    ZR s;
    GT C0 = group.init(GT_t);
    G2 C1;
    G2 C2;
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    uG1 = pk[2].getG1();
    uG2 = pk[3].getG2();
    hG1 = pk[4].getG1();
    hG2 = pk[5].getG2();
    egg = pk[6].getGT();
    ID = group.hashListToZR(id);
    s = group.random(ZR_t);
    C0 = group.mul(M, group.exp(egg, s));
    C1 = group.exp(gG2, s);
    C2 = group.exp(group.mul(group.exp(uG2, ID), hG2), s);
    ct.insert(0, C0);
    ct.insert(1, C1);
    ct.insert(2, C2);
    return;
}

void Bbibe04::decrypt(CharmList & pk, CharmList & sk, CharmList & ct, GT & M)
{
    G1 gG1;
    G2 gG2;
    G1 uG1;
    G2 uG2;
    G1 hG1;
    G2 hG2;
    GT egg;
    GT C0;
    G2 C1;
    G2 C2;
    G1 K1;
    G1 K2;
    GT R0 = group.init(GT_t);
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    uG1 = pk[2].getG1();
    uG2 = pk[3].getG2();
    hG1 = pk[4].getG1();
    hG2 = pk[5].getG2();
    egg = pk[6].getGT();
    
    C0 = ct[0].getGT();
    C1 = ct[1].getG2();
    C2 = ct[2].getG2();
    
    K1 = sk[0].getG1();
    K2 = sk[1].getG1();
    R0 = group.mul(group.pair(K1, C1), group.exp(group.pair(K2, C2), -1));
    M = group.div(C0, R0);
    return;
}

