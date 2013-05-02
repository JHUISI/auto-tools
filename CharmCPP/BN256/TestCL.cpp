#include "TestCL.h"

void Cl04::setup(G1 & gG1)
{
    gG1 = group.random(G1_t);
    return;
}

void Cl04::keygen(G1 & gG1, CharmList & sk, CharmList & spk, CharmList & vpk)
{
    ZR x;
    ZR y;
    G1 X;
    G1 Y;
    x = group.random(ZR_t);
    y = group.random(ZR_t);
    X = group.exp(gG1, x);
    Y = group.exp(gG1, y);
    sk.insert(0, x);
    sk.insert(1, y);
    spk = list;
    vpk.insert(0, X);
    vpk.insert(1, Y);
    return;
}

void Cl04::sign(CharmList & sk, string & M, CharmList & sig)
{
    ZR x;
    ZR y;
    G2 a;
    ZR m;
    G2 b;
    G2 c;
    
    x = sk[0].getZR();
    y = sk[1].getZR();
    a = group.random(G2_t);
    m = group.hashListToZR(M);
    b = group.exp(a, y);
    c = group.exp(a, group.add(x, group.mul(group.mul(m, x), y)));
    sig.insert(0, a);
    sig.insert(1, b);
    sig.insert(2, c);
    return;
}

bool Cl04::verify(CharmList & vpk, G1 & gG1, string & M, CharmList & sig)
{
    G2 a;
    G2 b;
    G2 c;
    G1 X;
    G1 Y;
    ZR m;
    
    a = sig[0].getG2();
    b = sig[1].getG2();
    c = sig[2].getG2();
    
    X = vpk[0].getG1();
    Y = vpk[1].getG1();
    m = group.hashListToZR(M);
    if ( ( (( (group.pair(Y, a)) == (group.pair(gG1, b)) )) && (( (group.pair(X, group.mul(a, group.exp(b, m)))) == (group.pair(gG1, c)) )) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

