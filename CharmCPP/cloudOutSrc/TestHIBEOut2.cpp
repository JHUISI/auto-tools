#include "TestHIBEOut2.h"

int l = 5;

void Hibe::setup(int l, int z, CharmList & mpk, CharmList & mk)
{
    ZR alpha;
    ZR beta;
    G1 g;
    G2 gb;
    G1 g1;
    G2 g1b;
    CharmListZR delta;
    CharmListG1 h;
    CharmListG2 hb;
    G2 g0b;
    GT v = group.init(GT_t);
    alpha = group.random(ZR_t);
    beta = group.random(ZR_t);
    g = group.random(G1_t);
    gb = group.random(G2_t);
    g1 = group.exp(g, alpha);
    g1b = group.exp(gb, alpha);
    for (int y = 0; y < l; y++)
    {
        delta[y] = group.random(ZR_t);
        h[y] = group.exp(g, delta[y]);
        hb[y] = group.exp(gb, delta[y]);
    }
    g0b = group.exp(gb, group.mul(alpha, beta));
    v = group.pair(g, g0b);
    mpk.insert(0, g);
    mpk.insert(1, g1);
    mpk.insert(2, h);
    mpk.insert(3, gb);
    mpk.insert(4, g1b);
    mpk.insert(5, hb);
    mpk.insert(6, v);
    mk.insert(0, g0b);
    return;
}

void Hibe::keygen(CharmList & mpk, CharmList & mk, string & id, CharmList & pk, ZR & uf0, ZR & bf0, CharmList & skBlinded)
{
    G1 g;
    G1 g1;
    CharmListG1 h;
    G2 gb;
    G2 g1b;
    CharmListG2 hb;
    GT v;
    G2 g0b;
    CharmListZR Id;
    CharmListZR r;
    CharmListG2 d;
    CharmListG2 dBlinded;
    G2 d0DotProdCalc;
    G2 d0;
    G2 d0Blinded;
    bf0 = group.random(ZR_t);
    uf0 = group.random(ZR_t);
    
    g = mpk[0].getG1();
    g1 = mpk[1].getG1();
    h = mpk[2].getListG1();
    gb = mpk[3].getG2();
    g1b = mpk[4].getG2();
    hb = mpk[5].getListG2();
    v = mpk[6].getGT();
    
    g0b = mk[0].getG2();
    Id = stringToInt(group, id, 5, 32);
    for (int y = 0; y < 5; y++)
    {
        r[y] = group.random(ZR_t);
        d[y] = group.exp(gb, r[y]);
    }
    CharmListInt d_keys = d.keys();
    int d_len = d_keys.length();
    for (int y_var = 0; y_var < d_len; y_var++)
    {
        int y = d_keys[y_var];
        dBlinded[y] = group.exp(d[y], group.div(1, bf0));
    }
    //;
    for (int y = 0; y < 5; y++)
    {
        d0DotProdCalc = group.mul(d0DotProdCalc, group.exp(group.mul(group.exp(g1b, Id[y]), hb[y]), r[y]));
    }
    d0 = group.mul(g0b, d0DotProdCalc);
    d0Blinded = group.exp(d0, group.div(1, uf0));
    pk.insert(0, id);
    skBlinded.insert(0, d0Blinded);
    skBlinded.insert(1, dBlinded);
    return;
}

void Hibe::encrypt(CharmList & mpk, CharmList & pk, GT & M, CharmList & ct)
{
    G1 g;
    G1 g1;
    CharmListG1 h;
    G2 gb;
    G2 g1b;
    CharmListG2 hb;
    GT v;
    string id;
    ZR s;
    GT A = group.init(GT_t);
    G1 B;
    CharmListZR Id;
    CharmListG1 C;
    
    g = mpk[0].getG1();
    g1 = mpk[1].getG1();
    h = mpk[2].getListG1();
    gb = mpk[3].getG2();
    g1b = mpk[4].getG2();
    hb = mpk[5].getListG2();
    v = mpk[6].getGT();
    
    id = pk[0].strPtr;
    s = group.random(ZR_t);
    A = group.mul(M, group.exp(v, s));
    B = group.exp(g, s);
    Id = stringToInt(group, id, 5, 32);
    for (int y = 0; y < 5; y++)
    {
        C[y] = group.exp(group.mul(group.exp(g1, Id[y]), h[y]), s);
    }
    ct.insert(0, A);
    ct.insert(1, B);
    ct.insert(2, C);
    return;
}

void Hibe::transform(CharmList & pk, CharmList & skBlinded, CharmList & ct, CharmList & transformOutputList)
{
    G2 d0Blinded;
    CharmListG2 dBlinded;
    GT A;
    G1 B;
    CharmListG1 C;
    GT finalLoopVar = group.init(GT_t);
    int FLrepVar1 = 0;
    CharmList transformOutputListForLoop;
    GT intermedLoopVar = group.init(GT_t);
    int FLrepVar2 = 0;
    GT D = group.init(GT_t);
    GT denominator = group.init(GT_t);
    
    d0Blinded = skBlinded[0].getG2();
    dBlinded = skBlinded[1].getListG2();
    
    A = ct[0].getGT();
    B = ct[1].getG1();
    C = ct[2].getListG1();
    transformOutputList.insert(3, A);
    transformOutputList.insert(0, group.init(GT_t));
    finalLoopVar = transformOutputList[0].getGT();
    for (int y = 0; y < 5; y++)
    {

        FLrepVar1 = 10 + (3 * y);
        transformOutputListForLoop.insert(FLrepVar1, group.pair(C[y], dBlinded[y]));
        intermedLoopVar = transformOutputListForLoop[FLrepVar1].getGT();
        FLrepVar2 = 11 + (3 * y);
        transformOutputListForLoop.insert(FLrepVar2, group.mul(finalLoopVar, intermedLoopVar));
        finalLoopVar = transformOutputListForLoop[FLrepVar2].getGT();
    }
    transformOutputList.insert(1, finalLoopVar);
    D = transformOutputList[1].getGT();
    transformOutputList.insert(2, group.pair(B, d0Blinded));
    denominator = transformOutputList[2].getGT();
    return;
}

void Hibe::decout(CharmList & pk, CharmList & transformOutputList, ZR & bf0, ZR & uf0, GT & M)
{
    GT A = group.init(GT_t);
    GT finalLoopVar = group.init(GT_t);
    GT D = group.init(GT_t);
    GT denominator = group.init(GT_t);
    GT fraction = group.init(GT_t);
    A = transformOutputList[3].getGT();
    finalLoopVar = transformOutputList[0].getGT();
    D = group.exp(transformOutputList[1].getGT(), bf0);
    denominator = group.exp(transformOutputList[2].getGT(), uf0);
    fraction = group.mul(D, group.exp(denominator, -1));
    M = group.mul(A, fraction);
    return;
}

