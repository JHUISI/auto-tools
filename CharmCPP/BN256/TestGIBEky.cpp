#include "TestGIBEky.h"

void Gentry06::setup(CharmList & mk, CharmList & pk)
{
    G1 gG1;
    G2 gG2;
    ZR h;
    G1 hG1;
    G2 hG2;
    ZR alpha;
    G2 g1;
    gG1 = group.random(G1_t);
    gG2 = group.random(G2_t);
    h = group.random(ZR_t);
    hG1 = group.exp(gG1, h);
    hG2 = group.exp(gG2, h);
    alpha = group.random(ZR_t);
    g1 = group.exp(gG2, alpha);
    mk.insert(0, alpha);
    pk.insert(0, gG1);
    pk.insert(1, gG2);
    pk.insert(2, g1);
    pk.insert(3, hG1);
    pk.insert(4, hG2);
    return;
}

void Gentry06::keygen(CharmList & pk, CharmList & mk, string & id, CharmList & sk)
{
    G1 gG1;
    G2 gG2;
    G2 g1;
    G1 hG1;
    G2 hG2;
    ZR alpha;
    ZR ID;
    ZR rID;
    G1 hID;
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    g1 = pk[2].getG2();
    hG1 = pk[3].getG1();
    hG2 = pk[4].getG2();
    
    alpha = mk[0].getZR();
    ID = group.hashListToZR(id);
    rID = group.random(ZR_t);
    if ( ( (rID) != (alpha) ) )
    {
        hID = group.exp(group.mul(hG1, group.exp(gG1, group.neg(rID))), group.div(1, group.sub(alpha, ID)));
    }
    else
    {
        cout << "Error occurred!" << endl;
        return;
    }
    sk.insert(0, rID);
    sk.insert(1, hID);
    return;
}

void Gentry06::encrypt(CharmList & pk, GT & m, string & id, CharmList & ct)
{
    G1 gG1;
    G2 gG2;
    G2 g1;
    G1 hG1;
    G2 hG2;
    ZR ID;
    ZR s;
    G2 U;
    GT V = group.init(GT_t);
    GT W = group.init(GT_t);
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    g1 = pk[2].getG2();
    hG1 = pk[3].getG1();
    hG2 = pk[4].getG2();
    ID = group.hashListToZR(id);
    s = group.random(ZR_t);
    U = group.mul(group.exp(g1, s), group.exp(gG2, group.mul(group.neg(s), ID)));
    V = group.exp(group.pair(gG1, gG2), s);
    W = group.mul(m, group.exp(group.pair(gG1, hG2), group.neg(s)));
    ct.insert(0, U);
    ct.insert(1, V);
    ct.insert(2, W);
    return;
}

void Gentry06::decrypt(CharmList & sk, CharmList & ct, GT & m)
{
    G2 U;
    GT V;
    GT W;
    ZR rID;
    G1 hID;
    
    U = ct[0].getG2();
    V = ct[1].getGT();
    W = ct[2].getGT();
    
    rID = sk[0].getZR();
    hID = sk[1].getG1();
    m = group.mul(group.mul(W, group.pair(hID, U)), group.exp(V, rID));
    return;
}

