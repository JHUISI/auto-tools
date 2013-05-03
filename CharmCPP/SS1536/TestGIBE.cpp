#include "TestGIBE.h"

void Gentry06::setup(CharmList & mk, CharmList & pk)
{
    G1 g;
    G1 h;
    ZR alpha;
    G1 g1;
    g = group.random(G1_t);
    h = group.random(G1_t);
    alpha = group.random(ZR_t);
    g1 = group.exp(g, alpha);
    mk.insert(0, alpha);
    pk.insert(0, g);
    pk.insert(1, g1);
    pk.insert(2, h);
    return;
}

void Gentry06::keygen(CharmList & pk, CharmList & mk, string & id, CharmList & sk)
{
    G1 g;
    G1 g1;
    G1 h;
    ZR alpha;
    ZR ID;
    ZR rID;
    G1 hID;
    
    g = pk[0].getG1();
    g1 = pk[1].getG1();
    h = pk[2].getG1();
    
    alpha = mk[0].getZR();
    ID = group.hashListToZR(id);
    rID = group.random(ZR_t);
    if ( ( (rID) != (alpha) ) )
    {
        hID = group.exp(group.mul(h, group.exp(g, group.neg(rID))), group.div(1, group.sub(alpha, ID)));
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
    G1 g;
    G1 g1;
    G1 h;
    ZR ID;
    ZR s;
    G1 U;
    GT V = group.init(GT_t);
    GT W = group.init(GT_t);
    
    g = pk[0].getG1();
    g1 = pk[1].getG1();
    h = pk[2].getG1();
    ID = group.hashListToZR(id);
    s = group.random(ZR_t);
    U = group.mul(group.exp(g1, s), group.exp(g, group.mul(group.neg(s), ID)));
    V = group.exp(group.pair(g, g), s);
    W = group.mul(m, group.exp(group.pair(g, h), group.neg(s)));
    ct.insert(0, U);
    ct.insert(1, V);
    ct.insert(2, W);
    return;
}

void Gentry06::decrypt(CharmList & sk, CharmList & ct, GT & m)
{
    G1 U;
    GT V;
    GT W;
    ZR rID;
    G1 hID;
    
    U = ct[0].getG1();
    V = ct[1].getGT();
    W = ct[2].getGT();
    
    rID = sk[0].getZR();
    hID = sk[1].getG1();
    m = group.mul(group.mul(W, group.pair(U, hID)), group.exp(V, rID));
    return;
}

