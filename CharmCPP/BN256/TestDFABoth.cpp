#include "TestDFABoth.h"

void Dfa12::setup(CharmListStr & alphabet, CharmList & mpk, G2 & msk)
{
    G1 gG1;
    G2 gG2;
    ZR z;
    G1 zG1;
    ZR hstart;
    G1 hstartG1;
    ZR hend;
    G2 hendG2;
    int A = 0;
    string a;
    ZR h;
    CharmListG1 hG1;
    CharmListG2 hG2;
    ZR alpha;
    GT egg = group.init(GT_t);
    gG1 = group.random(G1_t);
    gG2 = group.random(G2_t);
    z = group.random(ZR_t);
    zG1 = group.exp(gG1, z);
    hstart = group.random(ZR_t);
    hstartG1 = group.exp(gG1, hstart);
    hend = group.random(ZR_t);
    hendG2 = group.exp(gG2, hend);
    A = alphabet.length();
    for (int i = 0; i < A; i++)
    {
        a = dfaUtil.getString(alphabet[i]);
        h = group.random(ZR_t);
        hG1[a] = group.exp(gG1, h);
        hG2[a] = group.exp(gG2, h);
    }
    alpha = group.random(ZR_t);
    egg = group.exp(group.pair(gG1, gG2), alpha);
    msk = group.exp(gG2, group.neg(alpha));
    mpk.insert(0, egg);
    mpk.insert(1, gG1);
    mpk.insert(2, gG2);
    mpk.insert(3, zG1);
    mpk.insert(4, hG1);
    mpk.insert(5, hstartG1);
    mpk.insert(6, hendG2);
    return;
}

void Dfa12::keygen(CharmList & mpk, G2 & msk, CharmListInt & Q, CharmMetaListInt & T, CharmListInt & F, CharmList & sk)
{
    GT egg;
    G1 gG1;
    G2 gG2;
    G1 zG1;
    CharmListG1 hG1;
    G1 hstartG1;
    G2 hendG2;
    int qlen = 0;
    CharmListG1 DG1;
    CharmListG2 DG2;
    ZR rstart;
    G1 Kstart1;
    G2 Kstart2;
    int Tlen = 0;
    ZR r;
    CharmListInt t;
    int t0 = 0;
    int t1 = 0;
    string t2;
    string key;
    CharmListG1 K1;
    CharmListG2 K2;
    CharmListG1 K3;
    int Flen = 0;
    int x = 0;
    ZR rx;
    CharmListG2 KendList1;
    CharmListG1 KendList2;
    
    egg = mpk[0].getGT();
    gG1 = mpk[1].getG1();
    gG2 = mpk[2].getG2();
    zG1 = mpk[3].getG1();
    hG1 = mpk[4].getListG1();
    hstartG1 = mpk[5].getG1();
    hendG2 = mpk[6].getG2();
    qlen = Q.length();
    for (int i = 0; i < qlen+1; i++)
    {
        DG1[i] = group.random(G1_t);
        DG2[i] = group.random(G2_t);
    }
    rstart = group.random(ZR_t);
    Kstart1 = group.mul(DG1[0], group.exp(hstartG1, rstart));
    Kstart2 = group.exp(gG2, rstart);
    Tlen = T.length();
    for (int i = 0; i < Tlen; i++)
    {
        r = group.random(ZR_t);
        t = T[i];
        t0 = t[0];
        t1 = t[1];
        t2 = dfaUtil.getString(t[2]);
        key = dfaUtil.hashToKey(t);
        K1[key] = group.mul(group.exp(DG1[t0], -1), group.exp(zG1, r));
        K2[key] = group.exp(gG2, r);
        K3[key] = group.mul(DG1[t1], group.exp(hG1[t2], r));
    }
    Flen = F.length();
    for (int i = 0; i < Flen; i++)
    {
        x = F[i];
        rx = group.random(ZR_t);
        KendList1[x] = group.mul(msk, group.mul(DG2[x], group.exp(hendG2, rx)));
        KendList2[x] = group.exp(gG1, rx);
    }
    sk.insert(0, Kstart1);
    sk.insert(1, Kstart2);
    sk.insert(2, KendList1);
    sk.insert(3, KendList2);
    sk.insert(4, K1);
    sk.insert(5, K2);
    sk.insert(6, K3);
    return;
}

void Dfa12::encrypt(CharmList & mpk, CharmListStr & w, GT & M, CharmList & ct)
{
    GT egg;
    G1 gG1;
    G2 gG2;
    G1 zG1;
    CharmListG1 hG1;
    G1 hstartG1;
    G2 hendG2;
    int l = 0;
    CharmListZR s;
    GT Cm = group.init(GT_t);
    CharmListG2 C1;
    CharmListG1 C2;
    string a;
    G1 Cend1;
    G2 Cend2;
    
    egg = mpk[0].getGT();
    gG1 = mpk[1].getG1();
    gG2 = mpk[2].getG2();
    zG1 = mpk[3].getG1();
    hG1 = mpk[4].getListG1();
    hstartG1 = mpk[5].getG1();
    hendG2 = mpk[6].getG2();
    l = w.length();
    for (int i = 0; i < l+1; i++)
    {
        s[i] = group.random(ZR_t);
    }
    Cm = group.mul(M, group.exp(egg, s[l]));
    C1[0] = group.exp(gG2, s[0]);
    C2[0] = group.exp(hstartG1, s[0]);
    for (int i = 1; i < l+1; i++)
    {
        a = dfaUtil.getString(w[i]);
        C1.insert(i, group.exp(gG2, s[i]));
        C2.insert(i, group.mul(group.exp(hG1[a], s[i]), group.exp(zG1, s[i-1])));
    }
    Cend1 = group.exp(gG1, s[l]);
    Cend2 = group.exp(hendG2, s[l]);
    ct.insert(0, Cend1);
    ct.insert(1, Cend2);
    ct.insert(2, w);
    ct.insert(3, C1);
    ct.insert(4, C2);
    ct.insert(5, Cm);
    return;
}

void Dfa12::decrypt(CharmList & sk, CharmList & ct, GT & M)
{
    G1 Kstart1;
    G2 Kstart2;
    CharmListG2 KendList1;
    CharmListG1 KendList2;
    CharmListG1 K1;
    CharmListG2 K2;
    CharmListG1 K3;
    G1 Cend1;
    G2 Cend2;
    CharmListStr w;
    CharmListG2 C1;
    CharmListG1 C2;
    GT Cm;
    int l = 0;
    CharmMetaListInt Ti;
    CharmListGT B;
    string key;
    int j = 0;
    GT result0 = group.init(GT_t);
    int x = 0;
    GT result1 = group.init(GT_t);
    GT Bend = group.init(GT_t);
    
    Kstart1 = sk[0].getG1();
    Kstart2 = sk[1].getG2();
    KendList1 = sk[2].getListG2();
    KendList2 = sk[3].getListG1();
    K1 = sk[4].getListG1();
    K2 = sk[5].getListG2();
    K3 = sk[6].getListG1();
    
    Cend1 = ct[0].getG1();
    Cend2 = ct[1].getG2();
    w = ct[2].getListStr();
    C1 = ct[3].getListG2();
    C2 = ct[4].getListG1();
    Cm = ct[5].getGT();
    l = w.length();
    if ( ( (dfaUtil.accept(w)) == (false) ) )
    {
        cout << "Error occurred!" << endl;
        return;
    }
    Ti = dfaUtil.getTransitions(w);
    B[0] = group.mul(group.pair(Kstart1, C1[0]), group.pair(group.exp(C2[0], -1), Kstart2));
    for (int i = 1; i < l+1; i++)
    {
        key = dfaUtil.hashToKey(Ti[i]);
        j = (i - 1);
        result0 = group.mul(group.pair(K1[key], C1[j]), group.mul(group.pair(group.exp(C2[i], -1), K2[key]), group.pair(K3[key], C1[i])));
        B.insert(i, group.mul(B[i-1], result0));
    }
    x = dfaUtil.getAcceptState(Ti);
    result1 = group.mul(group.pair(group.exp(Cend1, -1), KendList1[x]), group.pair(KendList2[x], Cend2));
    Bend = group.mul(B[l], result1);
    M = group.div(Cm, Bend);
    return;
}

