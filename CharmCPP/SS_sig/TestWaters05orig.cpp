#include "TestWaters05orig.h"

// int l = 32;
int l = 4;

void Waters05::keygen(CharmList & pk, G1 & sk)
{
    ZR alpha;
    G1 g;
    G1 g1;
    G1 g2;
    G1 ut;
    CharmListZR y;
    CharmListG1 u;
    alpha = group.random(ZR_t);
    g = group.random(G1_t);
    g1 = group.exp(g, alpha);
    g2 = group.random(G1_t);
    ut = group.random(G1_t);
    for (int i = 0; i < l; i++)
    {
        y[i] = group.random(ZR_t);
        u[i] = group.exp(g, y[i]);
    }
    sk = group.exp(g2, alpha);
    pk.insert(0, g);
    pk.insert(1, g1);
    pk.insert(2, g2);
    pk.insert(3, u);
    pk.insert(4, ut);
    return;
}

void Waters05::sign(CharmList & pk, G1 & sk, ZR & M, CharmList & sig)
{
    G1 g;
    G1 g1;
    G1 g2;
    CharmListG1 u;
    G1 ut;
    CharmListZR m;
    ZR r;
    G1 S2;
    G1 dotProd1 = group.init(G1_t, 1);
    G1 S1;
    
    g = pk[0].getG1();
    g1 = pk[1].getG1();
    g2 = pk[2].getG1();
    u = pk[3].getListG1();
    ut = pk[4].getG1();
    cout << "M : " << M << endl;
    m = intToBits(M, l);
    cout << "m1 : \n" << m << endl;

    r = group.random(ZR_t);
    S2 = group.exp(g, r);
    group.init(dotProd1, 1);
    for (int i = 0; i < l; i++)
    {
        dotProd1 = group.mul(dotProd1, group.exp(u[i], m[i]));
    }
    S1 = group.mul(sk, group.exp(group.mul(ut, dotProd1), r));
    sig.insert(0, S1);
    sig.insert(1, S2);
    return;
}

bool Waters05::verify(CharmList & pk, ZR & M, CharmList & sig)
{
    G1 g;
    G1 g1;
    G1 g2;
    CharmListG1 u;
    G1 ut;
    G1 S1;
    G1 S2;
    CharmListZR m;
    G1 dotProd2 = group.init(G1_t, 1);
    
    g = pk[0].getG1();
    g1 = pk[1].getG1();
    g2 = pk[2].getG1();
    u = pk[3].getListG1();
    ut = pk[4].getG1();
    
    S1 = sig[0].getG1();
    S2 = sig[1].getG1();
    m = intToBits(M, l); // make sure this func works
    group.init(dotProd2, 1);
    for (int i = 0; i < l; i++)
    {
        dotProd2 = group.mul(dotProd2, group.exp(u[i], m[i]));
    }
    if ( ( (group.div(group.pair(S1, g), group.pair(S2, group.mul(ut, dotProd2)))) == (group.pair(g1, g2)) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

