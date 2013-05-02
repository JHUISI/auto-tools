#include "TestBB.h"

void Bbibe04::setup(CharmList & msk, CharmList & pk)
{
    G1 g;
    G1 u;
    G1 h;
    ZR alpha;
    GT egg = group.init(GT_t);
    G1 galpha;
    g = group.random(G1_t);
    u = group.random(G1_t);
    h = group.random(G1_t);
    alpha = group.random(ZR_t);
    egg = group.exp(group.pair(g, g), alpha);
    galpha = group.exp(g, alpha);
    msk.insert(0, galpha);
    pk.insert(0, g);
    pk.insert(1, u);
    pk.insert(2, h);
    pk.insert(3, egg);
    return;
}

void Bbibe04::keygen(CharmList & pk, CharmList & msk, string & id, CharmList & sk)
{
    G1 g;
    G1 u;
    G1 h;
    GT egg;
    G1 galpha;
    ZR ID;
    ZR r;
    G1 K1;
    G1 K2;
    
    g = pk[0].getG1();
    u = pk[1].getG1();
    h = pk[2].getG1();
    egg = pk[3].getGT();
    
    galpha = msk[0].getG1();
    ID = group.hashListToZR(id);
    r = group.random(ZR_t);
    K1 = group.mul(galpha, group.exp(group.mul(group.exp(u, ID), h), r));
    K2 = group.exp(g, r);
    sk.insert(0, K1);
    sk.insert(1, K2);
    return;
}

void Bbibe04::encrypt(CharmList & pk, GT & M, string & id, CharmList & ct)
{
    G1 g;
    G1 u;
    G1 h;
    GT egg;
    ZR ID;
    ZR s;
    GT C0 = group.init(GT_t);
    G1 C1;
    G1 C2;
    
    g = pk[0].getG1();
    u = pk[1].getG1();
    h = pk[2].getG1();
    egg = pk[3].getGT();
    ID = group.hashListToZR(id);
    s = group.random(ZR_t);
    C0 = group.mul(M, group.exp(egg, s));
    C1 = group.exp(g, s);
    C2 = group.exp(group.mul(group.exp(u, ID), h), s);
    ct.insert(0, C0);
    ct.insert(1, C1);
    ct.insert(2, C2);
    return;
}

void Bbibe04::decrypt(CharmList & pk, CharmList & sk, CharmList & ct, GT & M)
{
    G1 g;
    G1 u;
    G1 h;
    GT egg;
    GT C0;
    G1 C1;
    G1 C2;
    G1 K1;
    G1 K2;
    GT R0 = group.init(GT_t);
    
    g = pk[0].getG1();
    u = pk[1].getG1();
    h = pk[2].getG1();
    egg = pk[3].getGT();
    
    C0 = ct[0].getGT();
    C1 = ct[1].getG1();
    C2 = ct[2].getG1();
    
    K1 = sk[0].getG1();
    K2 = sk[1].getG1();
    R0 = group.div(group.pair(K1, C1), group.pair(K2, C2));
    M = group.div(C0, R0);
    return;
}

