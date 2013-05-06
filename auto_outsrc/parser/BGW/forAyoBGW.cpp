#include "BGW/forAyoBGW.h"

void Bgw05::setup(int n, CharmList & pk, CharmList & msk)
{
    G1 gG1;
    G2 gG2;
    ZR alpha;
    int index = 0;
    CharmListG1 glG1;
    CharmListG2 glG2;
    ZR gamma;
    G1 v;
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
    v = group.exp(gG1, gamma);
    pk.insert(0, gG1);
    pk.insert(1, gG2);
    pk.insert(2, glG1);
    pk.insert(3, glG2);
    pk.insert(4, v);
    msk.insert(0, gamma);
    return;
}

void Bgw05::keygen(CharmList & pk, CharmList & msk, int n, ZR & bf0, CharmList & skBlinded)
{
    G1 gG1;
    G2 gG2;
    CharmListG1 glG1;
    CharmListG2 glG2;
    G1 v;
    ZR gamma;
    CharmListG2 s;
    CharmListG2 sBlinded;
    bf0 = group.random(ZR_t);
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    glG1 = pk[2].getListG1();
    glG2 = pk[3].getListG2();
    v = pk[4].getG1();
    
    gamma = msk[0].getZR();
    for (int i = 1; i < n+1; i++)
    {
        s[i] = group.exp(glG2[i], gamma);
    }
    CharmListInt s_keys = s.keys();
    int s_len = s_keys.length();
    for (int y_var = 0; y_var < s_len; y_var++)
    {
        int y = s_keys[y_var];
        sBlinded[y] = group.exp(s[y], group.div(1, bf0));
    }
    skBlinded.insert(0, sBlinded);
    return;
}

void Bgw05::encrypt(CharmListInt & S, CharmList & pk, int n, CharmList & ct)
{
    G1 gG1;
    G2 gG2;
    CharmListG1 glG1;
    CharmListG2 glG2;
    G1 v;
    ZR t;
    GT K = group.init(GT_t);
    G1 dotProd1 = group.init(G1_t, 1);
    G1 Hdr2;
    G1 Hdr1;
    CharmList Hdr;
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    glG1 = pk[2].getListG1();
    glG2 = pk[3].getListG2();
    v = pk[4].getG1();
    t = group.random(ZR_t);
    K = group.exp(group.pair(glG1[n], glG2[1]), t);
    group.init(dotProd1, 1);
    CharmListInt S_keys = S.keys();
    int S_len = S_keys.length();
    for (int j_var = 0; j_var < S_len; j_var++)
    {
        int j = S_keys[j_var];
        dotProd1 = group.mul(dotProd1, glG1[n+1-j]);
    }
    Hdr2 = group.exp(group.mul(v, dotProd1), t);
    Hdr1 = group.exp(gG1, t);
    Hdr.insert(0, Hdr1);
    Hdr.insert(1, Hdr2);
    ct.insert(0, Hdr);
    ct.insert(1, K);
    return;
}

void Bgw05::transform(CharmListInt & S, int i, int n, CharmList & Hdr, CharmList & pk, CharmList & skBlinded, CharmList & transformOutputList)
{
    G1 Hdr1;
    G1 Hdr2;
    G1 gG1;
    G2 gG2;
    CharmListG1 glG1;
    CharmListG2 glG2;
    G1 v;
    CharmListG2 sBlinded;
    GT numerator = group.init(GT_t);
    G2 dotProd2 = group.init(G2_t, 1);
    int lenS = 0;
    int j = 0;
    int FLrepVar2 = 0;
    CharmList transformOutputListForLoop;
    
    Hdr1 = Hdr[0].getG1();
    Hdr2 = Hdr[1].getG1();
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    glG1 = pk[2].getListG1();
    glG2 = pk[3].getListG2();
    v = pk[4].getG1();
    
    sBlinded = skBlinded[0].getListG2();
    transformOutputList.insert(0, group.pair(glG2[i], Hdr2));
    numerator = transformOutputList[0].getGT();
    transformOutputList.insert(1, group.init(G2_t));
    dotProd2 = transformOutputList[1].getG2();
    lenS = S.length();
    for (int k = 0; k < lenS; k++)
    {

        j = S[k];
        if ( ( (j) != (i) ) )
        {

            FLrepVar2 = group.add(10, (5 * k));
            transformOutputListForLoop.insert(FLrepVar2, group.mul(dotProd2, glG2[n+1-j+i]));
            dotProd2 = transformOutputListForLoop[FLrepVar2].getG2().getG2();
        }
    }
    transformOutputList.insert(2, group.pair(Hdr1, sBlinded[i]));
    transformOutputList.insert(3, group.pair(Hdr1, dotProd2));
    return;
}

void Bgw05::decout(CharmListInt & S, int i, int n, CharmList & Hdr, CharmList & pk, CharmList & transformOutputList, ZR & bf0, GT & K)
{
    G1 Hdr1;
    G1 Hdr2;
    G1 gG1;
    G2 gG2;
    CharmListG1 glG1;
    CharmListG2 glG2;
    G1 v;
    GT numerator = group.init(GT_t);
    G2 dotProd2 = group.init(G2_t, 1);
    GT denominator = group.init(GT_t);
    
    Hdr1 = Hdr[0].getG1();
    Hdr2 = Hdr[1].getG1();
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    glG1 = pk[2].getListG1();
    glG2 = pk[3].getListG2();
    v = pk[4].getG1();
    numerator = transformOutputList[0].getGT();
    dotProd2 = transformOutputList[1].getG2();
    denominator = group.mul(group.exp(transformOutputList[2].getGT(), bf0), transformOutputList[3].getGT());
    K = group.mul(numerator, group.exp(denominator, -1));
    return;
}

