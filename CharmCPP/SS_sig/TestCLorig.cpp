#include "TestCLorig.h"

void Cl04::setup(G1 & g)
{
    g = group.random(G1_t);
    return;
}

void Cl04::keygen(G1 & g, CharmList & pk, CharmList & sk)
{
    ZR x;
    ZR y;
    G1 X;
    G1 Y;
    x = group.random(ZR_t);
    y = group.random(ZR_t);
    X = group.exp(g, x);
    Y = group.exp(g, y);
    sk.insert(0, x);
    sk.insert(1, y);
    pk.insert(0, X);
    pk.insert(1, Y);
    return;
}

void Cl04::sign(CharmList & sk, string & M, CharmList & sig)
{
    ZR x;
    ZR y;
    G1 a;
    ZR m;
    G1 b;
    G1 c;
    
    x = sk[0].getZR();
    y = sk[1].getZR();
    a = group.random(G1_t);
    m = group.hashListToZR(M);
    b = group.exp(a, y);
    c = group.exp(a, group.add(x, group.mul(group.mul(m, x), y)));
    sig.insert(0, a);
    sig.insert(1, b);
    sig.insert(2, c);
    return;
}

bool Cl04::verify(CharmList & pk, G1 & g, string & M, CharmList & sig)
{
    G1 a;
    G1 b;
    G1 c;
    G1 X;
    G1 Y;
    ZR m;
    
    a = sig[0].getG1();
    b = sig[1].getG1();
    c = sig[2].getG1();
    
    X = pk[0].getG1();
    Y = pk[1].getG1();
    m = group.hashListToZR(M);
    if ( ( (( (group.pair(a, Y)) == (group.pair(g, b)) )) && (( (group.mul(group.pair(X, a), group.exp(group.pair(X, b), m))) == (group.pair(g, c)) )) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

