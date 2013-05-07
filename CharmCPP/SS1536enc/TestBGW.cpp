#include "TestBGW.h"

void Bgw05::setup(int n, CharmList & pk, CharmList & msk)
{
    G1 g;
    ZR alpha;
    int index = 0;
    CharmListG1 gl;
    ZR gamma;
    G1 v;
    g = group.random(G1_t);
    alpha = group.random(ZR_t);
    index = group.add((2 * n), 1);
    for (int i = 1; i < index; i++)
    {
        gl[i] = group.exp(g, group.exp(alpha, i));
    }
    gamma = group.random(ZR_t);
    v = group.exp(g, gamma);
    pk.insert(0, g);
    pk.insert(1, gl);
    pk.insert(2, v);
    msk.insert(0, gamma);
    return;
}

void Bgw05::keygen(CharmList & pk, CharmList & msk, int n, CharmMetaListG1 & sk)
{
    G1 g;
    CharmListG1 gl;
    G1 v;
    ZR gamma;
    CharmListG1 s;
    
    g = pk[0].getG1();
    gl = pk[1].getListG1();
    v = pk[2].getG1();
    
    gamma = msk[0].getZR();
    for (int i = 1; i < n+1; i++)
    {
        s[i] = group.exp(gl[i], gamma);
    }
    sk.insert(0, s);
    return;
}

void Bgw05::encrypt(CharmListInt & S, CharmList & pk, int n, CharmList & ct)
{
    G1 g;
    CharmListG1 gl;
    G1 v;
    ZR t;
    GT K = group.init(GT_t);
    G1 dotProd1 = group.init(G1_t, 1);
    G1 Hdr2;
    G1 Hdr1;
    CharmList Hdr;
    
    g = pk[0].getG1();
    gl = pk[1].getListG1();
    v = pk[2].getG1();
    t = group.random(ZR_t);
    K = group.exp(group.pair(gl[n], gl[1]), t);
    group.init(dotProd1, 1);
    CharmListInt S_keys = S; // .keys();
    int S_len = S_keys.length();
    for (int j_var = 0; j_var < S_len; j_var++)
    {
        int j = S_keys[j_var];
        dotProd1 = group.mul(dotProd1, gl[n+1-j]);
    }
    Hdr2 = group.exp(group.mul(v, dotProd1), t);
    Hdr1 = group.exp(g, t);
    Hdr.insert(0, Hdr1);
    Hdr.insert(1, Hdr2);
    ct.insert(0, Hdr);
    ct.insert(1, K);
    return;
}

void Bgw05::decrypt(CharmListInt & S, int i, int n, CharmList & Hdr, CharmList & pk, CharmMetaListG1 & sk, GT & K)
{
    G1 Hdr1;
    G1 Hdr2;
    G1 g;
    CharmListG1 gl;
    G1 v;
    CharmListG1 s;
    GT numerator = group.init(GT_t);
    G1 dotProd2 = group.init(G1_t, 1);
    int lenS = 0;
    int j = 0;
    GT denominator = group.init(GT_t);
    
    Hdr1 = Hdr[0].getG1();
    Hdr2 = Hdr[1].getG1();
    
    g = pk[0].getG1();
    gl = pk[1].getListG1();
    v = pk[2].getG1();
    
    s = sk[0];
    numerator = group.pair(gl[i], Hdr2);
    group.init(dotProd2, 1);
    lenS = S.length();
    for (int k = 0; k < lenS; k++)
    {
        j = S[k];
        if ( ( (j) != (i) ) )
        {
            dotProd2 = group.mul(dotProd2, gl[n+1-j+i]);
        }
    }
    denominator = group.pair(group.mul(s[i], dotProd2), Hdr1);
    K = group.div(numerator, denominator);
    return;
}

