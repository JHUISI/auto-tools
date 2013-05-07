#include "TestDSESigorig.h"

void Waters09sig::keygen(CharmList & pk, CharmList & sk)
{
    G1 g;
    G1 w;
    G1 u;
    G1 h;
    G1 v;
    G1 v1;
    G1 v2;
    ZR a1;
    ZR a2;
    ZR b;
    ZR alpha;
    G1 gb;
    G1 ga1;
    G1 ga2;
    G1 gba1;
    G1 gba2;
    G1 tau1;
    G1 tau2;
    G1 tau1b;
    G1 tau2b;
    GT A = group.init(GT_t);
    G1 galpha;
    G1 galphaa1;
    g = group.random(G1_t);
    w = group.random(G1_t);
    u = group.random(G1_t);
    h = group.random(G1_t);
    v = group.random(G1_t);
    v1 = group.random(G1_t);
    v2 = group.random(G1_t);
    a1 = group.random(ZR_t);
    a2 = group.random(ZR_t);
    b = group.random(ZR_t);
    alpha = group.random(ZR_t);
    gb = group.exp(g, b);
    ga1 = group.exp(g, a1);
    ga2 = group.exp(g, a2);
    gba1 = group.exp(gb, a1);
    gba2 = group.exp(gb, a2);
    tau1 = group.mul(v, group.exp(v1, a1));
    tau2 = group.mul(v, group.exp(v2, a2));
    tau1b = group.exp(tau1, b);
    tau2b = group.exp(tau2, b);
    A = group.exp(group.pair(g, g), group.mul(alpha, group.mul(a1, b)));
    galpha = group.exp(g, alpha);
    galphaa1 = group.exp(galpha, a1);
    pk.insert(0, g);
    pk.insert(1, gb);
    pk.insert(2, ga1);
    pk.insert(3, ga2);
    pk.insert(4, gba1);
    pk.insert(5, gba2);
    pk.insert(6, tau1);
    pk.insert(7, tau2);
    pk.insert(8, tau1b);
    pk.insert(9, tau2b);
    pk.insert(10, w);
    pk.insert(11, u);
    pk.insert(12, h);
    pk.insert(13, A);
    sk.insert(0, galpha);
    sk.insert(1, galphaa1);
    sk.insert(2, v);
    sk.insert(3, v1);
    sk.insert(4, v2);
    sk.insert(5, alpha);
    return;
}

void Waters09sig::sign(CharmList & pk, CharmList & sk, string & m, CharmList & sig)
{
    G1 g;
    G1 gb;
    G1 ga1;
    G1 ga2;
    G1 gba1;
    G1 gba2;
    G1 tau1;
    G1 tau2;
    G1 tau1b;
    G1 tau2b;
    G1 w;
    G1 u;
    G1 h;
    GT A;
    G1 galpha;
    G1 galphaa1;
    G1 v;
    G1 v1;
    G1 v2;
    ZR alpha;
    ZR r1;
    ZR r2;
    ZR z1;
    ZR z2;
    ZR tagk;
    ZR r;
    ZR M;
    G1 S1;
    G1 S2;
    G1 S3;
    G1 S4;
    G1 S5;
    G1 S6;
    G1 S7;
    G1 SK;
    
    g = pk[0].getG1();
    gb = pk[1].getG1();
    ga1 = pk[2].getG1();
    ga2 = pk[3].getG1();
    gba1 = pk[4].getG1();
    gba2 = pk[5].getG1();
    tau1 = pk[6].getG1();
    tau2 = pk[7].getG1();
    tau1b = pk[8].getG1();
    tau2b = pk[9].getG1();
    w = pk[10].getG1();
    u = pk[11].getG1();
    h = pk[12].getG1();
    A = pk[13].getGT();
    
    galpha = sk[0].getG1();
    galphaa1 = sk[1].getG1();
    v = sk[2].getG1();
    v1 = sk[3].getG1();
    v2 = sk[4].getG1();
    alpha = sk[5].getZR();
    r1 = group.random(ZR_t);
    r2 = group.random(ZR_t);
    z1 = group.random(ZR_t);
    z2 = group.random(ZR_t);
    tagk = group.random(ZR_t);
    r = group.add(r1, r2);
    M = group.hashListToZR(m);
    S1 = group.mul(galphaa1, group.exp(v, r));
    S2 = group.mul(group.mul(group.exp(g, group.neg(alpha)), group.exp(v1, r)), group.exp(g, z1));
    S3 = group.exp(gb, group.neg(z1));
    S4 = group.mul(group.exp(v2, r), group.exp(g, z2));
    S5 = group.exp(gb, group.neg(z2));
    S6 = group.exp(gb, r2);
    S7 = group.exp(g, r1);
    SK = group.exp(group.mul(group.mul(group.exp(u, M), group.exp(w, tagk)), h), r1);
    sig.insert(0, S1);
    sig.insert(1, S2);
    sig.insert(2, S3);
    sig.insert(3, S4);
    sig.insert(4, S5);
    sig.insert(5, S6);
    sig.insert(6, S7);
    sig.insert(7, SK);
    sig.insert(8, tagk);
    return;
}

bool Waters09sig::verify(CharmList & pk, string & m, CharmList & sig)
{
    G1 g;
    G1 gb;
    G1 ga1;
    G1 ga2;
    G1 gba1;
    G1 gba2;
    G1 tau1;
    G1 tau2;
    G1 tau1b;
    G1 tau2b;
    G1 w;
    G1 u;
    G1 h;
    GT A;
    G1 S1;
    G1 S2;
    G1 S3;
    G1 S4;
    G1 S5;
    G1 S6;
    G1 S7;
    G1 SK;
    ZR tagk;
    ZR s1;
    ZR s2;
    ZR t;
    ZR tagc;
    ZR s;
    ZR M;
    ZR theta;
    
    g = pk[0].getG1();
    gb = pk[1].getG1();
    ga1 = pk[2].getG1();
    ga2 = pk[3].getG1();
    gba1 = pk[4].getG1();
    gba2 = pk[5].getG1();
    tau1 = pk[6].getG1();
    tau2 = pk[7].getG1();
    tau1b = pk[8].getG1();
    tau2b = pk[9].getG1();
    w = pk[10].getG1();
    u = pk[11].getG1();
    h = pk[12].getG1();
    A = pk[13].getGT();
    
    S1 = sig[0].getG1();
    S2 = sig[1].getG1();
    S3 = sig[2].getG1();
    S4 = sig[3].getG1();
    S5 = sig[4].getG1();
    S6 = sig[5].getG1();
    S7 = sig[6].getG1();
    SK = sig[7].getG1();
    tagk = sig[8].getZR();
    s1 = group.random(ZR_t);
    s2 = group.random(ZR_t);
    t = group.random(ZR_t);
    tagc = group.random(ZR_t);
    s = group.add(s1, s2);
    M = group.hashListToZR(m);
    theta = group.div(1, group.sub(tagc, tagk));
    if ( ( (group.mul(group.pair(group.exp(gb, s), S1), group.mul(group.pair(group.exp(gba1, s1), S2), group.mul(group.pair(group.exp(ga1, s1), S3), group.mul(group.pair(group.exp(gba2, s2), S4), group.pair(group.exp(ga2, s2), S5)))))) == (group.mul(group.pair(S6, group.mul(group.exp(tau1, s1), group.exp(tau2, s2))), group.mul(group.pair(S7, group.mul(group.exp(tau1b, s1), group.mul(group.exp(tau2b, s2), group.exp(w, -t)))), group.mul(group.exp(group.mul(group.pair(S7, group.mul(group.mul(group.exp(u, group.mul(M, t)), group.exp(w, group.mul(tagc, t))), group.exp(h, t))), group.pair(group.exp(g, -t), SK)), theta), group.exp(A, s2))))) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

