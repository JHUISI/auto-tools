#include "TestBGWky.h"

void Bgw05::setup(int n, CharmList & pk, CharmList & msk)
{
    G1 gG1;
    G2 gG2;
    ZR alpha;
    int index = 0;
    CharmListG1 glG1;
    CharmListG2 glG2;
    ZR gamma;
    G2 v;
    gG1 = group.random(G1_t);
    gG2 = group.random(G2_t);
    alpha = group.random(ZR_t);
    index = group.add((2 * n), 1);
    for (int i = 1; i < index; i++)
    {
        glG1[i] = group.exp(gG1, group.exp(alpha, i));
        glG2[i] = group.exp(gG2, group.exp(alpha, i));
    }
    gamma = group.random(ZR_t);
    v = group.exp(gG2, gamma);
    pk.insert(0, gG1);
    pk.insert(1, gG2);
    pk.insert(2, glG1);
    pk.insert(3, glG2);
    pk.insert(4, v);
    msk.insert(0, gamma);
    return;
}

void Bgw05::keygen(CharmList & pk, CharmList & msk, int n, CharmMetaListG1 & sk)
{
    G1 gG1;
    G2 gG2;
    CharmListG1 glG1;
    CharmListG2 glG2;
    G2 v;
    ZR gamma;
    CharmListG1 s;
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    glG1 = pk[2].getListG1();
    glG2 = pk[3].getListG2();
    v = pk[4].getG2();
    
    gamma = msk[0].getZR();
    for (int i = 1; i < n+1; i++)
    {
        s[i] = group.exp(glG1[i], gamma);
    }
    sk.insert(0, s);
    return;
}

void Bgw05::encrypt(CharmListInt & S, CharmList & pk, int n, CharmList & ct)
{
    G1 gG1;
    G2 gG2;
    CharmListG1 glG1;
    CharmListG2 glG2;
    G2 v;
    ZR t;
    GT K = group.init(GT_t);
    G2 dotProd1 = group.init(G2_t, 1);
    G2 Hdr2;
    G2 Hdr1;
    CharmList Hdr;
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    glG1 = pk[2].getListG1();
    glG2 = pk[3].getListG2();
    v = pk[4].getG2();
    t = group.random(ZR_t);
    K = group.exp(group.pair(glG1[n], glG2[1]), t);
    group.init(dotProd1, 1);
    CharmListInt S_keys = S; // .keys();
    int S_len = S_keys.length();
    for (int j_var = 0; j_var < S_len; j_var++)
    {
        int j = S_keys[j_var];
        dotProd1 = group.mul(dotProd1, glG2[n+1-j]);
    }
    Hdr2 = group.exp(group.mul(v, dotProd1), t);
    Hdr1 = group.exp(gG2, t);
    Hdr.insert(0, Hdr1);
    Hdr.insert(1, Hdr2);
    ct.insert(0, Hdr);
    ct.insert(1, K);
    return;
}

void Bgw05::decrypt(CharmListInt & S, int i, int n, CharmList & Hdr, CharmList & pk, CharmMetaListG1 & sk, GT & K)
{
    G2 Hdr1;
    G2 Hdr2;
    G1 gG1;
    G2 gG2;
    CharmListG1 glG1;
    CharmListG2 glG2;
    G2 v;
    CharmListG1 s;
    GT numerator = group.init(GT_t);
    G1 dotProd2 = group.init(G1_t, 1);
    int lenS = 0;
    int j = 0;
    GT denominator = group.init(GT_t);
    
    Hdr1 = Hdr[0].getG2();
    Hdr2 = Hdr[1].getG2();
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    glG1 = pk[2].getListG1();
    glG2 = pk[3].getListG2();
    v = pk[4].getG2();
    
    s = sk[0];
    numerator = group.pair(glG1[i], Hdr2);
    group.init(dotProd2, 1);
    lenS = S.length();
    for (int k = 0; k < lenS; k++)
    {
        j = S[k];
        if ( ( (j) != (i) ) )
        {
            dotProd2 = group.mul(dotProd2, glG1[n+1-j+i]);
        }
    }
    denominator = group.pair(group.mul(s[i], dotProd2), Hdr1);
    K = group.div(numerator, denominator);
    return;
}

