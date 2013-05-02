#include "TestCYH.h"

void Cyh::setup(G2 & P, G2 & gG2, ZR & alpha)
{
    gG2 = group.random(G2_t);
    alpha = group.random(ZR_t);
    P = group.exp(gG2, alpha);
    return;
}

void Cyh::keygen(ZR & alpha, string & ID, G1 & pk, G1 & sk)
{
    sk = group.exp(group.hashListToG1(ID), alpha);
    pk = group.hashListToG1(ID);
    return;
}

void Cyh::sign(string & ID, CharmListStr & ID_list, G1 & pk, G1 & sk, string & M, CharmList & sig)
{
    string Lt;
    CharmListG1 u;
    CharmListZR h;
    int s = 0;
    ZR r;
    CharmListG1 pklist;
    G1 dotProd = group.init(G1_t, 1);
    G1 S;
    Lt = concat(ID_list);
    for (int i = 0; i < l; i++)
    {
        if ( ( isNotEqual(ID, ID_list[i]) ) )
        {
            u[i] = group.random(G1_t);
            h[i] = group.hashListToZR((Element(M) + Element(Lt) + Element(u[i])));
        }
        else
        {
            s = i;
        }
    }
    r = group.random(ZR_t);
    for (int y = 0; y < l; y++)
    {
        pklist[y] = group.hashListToG1(ID_list[y]);
    }
    group.init(dotProd, 1);
    for (int i = 0; i < l; i++)
    {
        if ( ( isNotEqual(ID, ID_list[i]) ) )
        {
            dotProd = group.mul(dotProd, group.mul(u[i], group.exp(pklist[i], h[i])));
        }
    }
    u.insert(s, group.mul(group.exp(pk, r), group.exp(dotProd, -1)));
    h.insert(s, group.hashListToZR((Element(M) + Element(Lt) + Element(u[s]))));
    S = group.exp(sk, group.add(h[s], r));
    sig.insert(0, Lt);
    sig.insert(1, pklist);
    sig.insert(2, u);
    sig.insert(3, S);
    return;
}

bool Cyh::verify(G2 & P, G2 & gG2, string & M, CharmList & sig)
{
    string Lt;
    CharmListG1 pklist;
    CharmListG1 u;
    G1 S;
    CharmListZR h;
    G1 dotProd = group.init(G1_t, 1);
    
    Lt = sig[0].strPtr;
    pklist = sig[1].getListG1();
    u = sig[2].getListG1();
    S = sig[3].getG1();
    for (int y = 0; y < l; y++)
    {
        h[y] = group.hashListToZR((Element(M) + Element(Lt) + Element(u[y])));
    }
    group.init(dotProd, 1);
    for (int y = 0; y < l; y++)
    {
        dotProd = group.mul(dotProd, group.mul(u[y], group.exp(pklist[y], h[y])));
    }
    if ( ( (group.pair(dotProd, P)) == (group.pair(S, gG2)) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

