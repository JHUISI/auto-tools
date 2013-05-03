#include "SW05/forAyoSW05.h"

void Sw05::setup(int n, CharmList & pk, ZR & mk)
{
    G1 g;
    ZR y;
    G1 g1;
    G2 g2;
    CharmListG2 t;
    g = group.random(G1_t);
    y = group.random(ZR_t);
    g1 = group.exp(g, y);
    g2 = group.random(G2_t);
    for (int i = 0; i < n+1; i++)
    {
        t[i] = group.random(G2_t);
    }
    pk.insert(0, g);
    pk.insert(1, g1);
    pk.insert(2, g2);
    pk.insert(3, t);
    mk = y;
    return;
}

G2 Sw05::evalT(CharmList & pk, int n, ZR & x)
{
    G1 g;
    G1 g1;
    G2 g2;
    CharmListG2 t;
    CharmListInt N;
    CharmListZR coeffs;
    G2 prodResult;
    int lenN = 0;
    int loopVarEvalT = 0;
    int loopVarM1 = 0;
    G2 T;
    
    g = pk[0].getG1();
    g1 = pk[1].getG1();
    g2 = pk[2].getG2();
    t = pk[3].getListG2();
    for (int i = 0; i < n+1; i++)
    {
        N[i] = (i + 1);
    }
    coeffs = util.recoverCoefficientsDict(group, N);
    //;
    lenN = N.length();
    for (int i = 0; i < lenN; i++)
    {
        loopVarEvalT = N[i];
        loopVarM1 = (loopVarEvalT - 1);
        prodResult = group.mul(prodResult, group.exp(t[loopVarM1], coeffs[loopVarEvalT]));
    }
    T = group.mul(group.exp(g2, (x * n)), prodResult);
    return T;
}

void Sw05::extract(ZR & mk, CharmListStr & w, CharmList & pk, int dParam, int n, CharmListZR & blindingFactorDBlinded, ZR & bf0, CharmList & skBlinded)
{
    CharmListStr wBlinded;
    G1 g;
    G1 g1;
    G2 g2;
    CharmListG2 t;
    int lenw = 0;
    string loopVar1;
    CharmListZR wHash;
    ZR r;
    CharmListZR q;
    CharmListZR shares;
    int wHashLen = 0;
    ZR loopVar2;
    string loopVar2Str;
    G2 evalTVar;
    CharmListG2 D;
    CharmListG1 d;
    CharmListG1 dBlinded;
    CharmListG2 DBlinded;
    bf0 = group.random(ZR_t);
    wBlinded = w;
    
    g = pk[0].getG1();
    g1 = pk[1].getG1();
    g2 = pk[2].getG2();
    t = pk[3].getListG2();
    lenw = wBlinded.length();
    for (int i = 0; i < lenw; i++)
    {
        loopVar1 = wBlinded[i];
        wHash[i] = group.hashListToZR(loopVar1);
    }
    r = group.random(ZR_t);
    q[0] = mk;
    for (int i = 1; i < dParam; i++)
    {
        q.insert(i, group.random(ZR_t));
    }
    shares = util.genSharesForX(group, mk, q, wHash);
    wHashLen = wHash.length();
    for (int i = 0; i < wHashLen; i++)
    {
        loopVar2 = wHash[i];
        loopVar2Str = wBlinded[i];
        evalTVar = evalT(pk, n, loopVar2);
        D[loopVar2Str] = group.mul(group.exp(g2, shares[i]), group.exp(evalTVar, r));
        d[loopVar2Str] = group.exp(g, r);
    }
    CharmListStr d_keys = d.strkeys();
    int d_len = d_keys.length();
    for (int y_var = 0; y_var < d_len; y_var++)
    {
        string y = d_keys[y_var];
        dBlinded[y] = group.exp(d[y], group.div(1, bf0));
    }
    CharmListStr D_keys = D.strkeys();
    int D_len = D_keys.length();
    for (int y_var = 0; y_var < D_len; y_var++)
    {
        string y = D_keys[y_var];
        blindingFactorDBlinded.insert(y, group.random(ZR_t));
        DBlinded[y] = group.exp(D[y], group.div(1, blindingFactorDBlinded[y]));
    }
    skBlinded.insert(0, wBlinded);
    skBlinded.insert(1, DBlinded);
    skBlinded.insert(2, dBlinded);
    return;
}

void Sw05::encrypt(CharmList & pk, CharmListStr & wPrime, GT & M, int n, CharmList & CT)
{
    G1 g;
    G1 g1;
    G2 g2;
    CharmListG2 t;
    ZR s;
    GT Eprime = group.init(GT_t);
    G1 Eprimeprime;
    int wPrimeLen = 0;
    ZR loopVar;
    string loopVarStr;
    G2 evalTVar;
    CharmListG2 E;
    
    g = pk[0].getG1();
    g1 = pk[1].getG1();
    g2 = pk[2].getG2();
    t = pk[3].getListG2();
    s = group.random(ZR_t);
    Eprime = group.mul(M, group.exp(group.pair(g1, g2), s));
    Eprimeprime = group.exp(g, s);
    wPrimeLen = wPrime.length();
    for (int i = 0; i < wPrimeLen; i++)
    {
        loopVar = group.hashListToZR(wPrime[i]);
        loopVarStr = wPrime[i];
        evalTVar = evalT(pk, n, loopVar);
        E[loopVarStr] = group.exp(evalTVar, s);
    }
    CT.insert(0, wPrime);
    CT.insert(1, Eprime);
    CT.insert(2, Eprimeprime);
    CT.insert(3, E);
    return;
}

void Sw05::transform(CharmList & pk, CharmList & skBlinded, CharmList & CT, int dParam, CharmList & transformOutputList, CharmListStr & SKeys, int & SLen, CharmList & transformOutputListForLoop)
{
    CharmListStr wPrime;
    GT Eprime;
    G1 Eprimeprime;
    CharmListG2 E;
    CharmListStr wBlinded;
    CharmListG2 DBlinded;
    CharmListG1 dBlinded;
    CharmListZR S;
    CharmListZR coeffs;
    string loopVar3;
    int FLrepVar2 = 0;
    int FLrepVar3 = 0;
    
    wPrime = CT[0].getListStr();
    Eprime = CT[1].getGT();
    Eprimeprime = CT[2].getG1();
    E = CT[3].getListG2();
    
    wBlinded = skBlinded[0].getListStr();
    DBlinded = skBlinded[1].getListG2();
    dBlinded = skBlinded[2].getListG1();
    transformOutputList.insert(2, Eprime);
    transformOutputList.insert(0, util.intersectionSubset(group, wBlinded, wPrime, dParam));
    S = transformOutputList[0].getZR();
    transformOutputList.insert(1, util.recoverCoefficientsDict(group, S));
    coeffs = transformOutputList[1].getZR();
    SKeys = S.strkeys();
    SLen = S.length();
    for (int i = 0; i < SLen; i++)
    {

        loopVar3 = SKeys[i];
        FLrepVar2 = group.add(10, (5 * i));
        transformOutputListForLoop.insert(FLrepVar2, group.pair(group.exp(dBlinded[loopVar3], coeffs[loopVar3]), E[loopVar3]));
        FLrepVar3 = group.add(11, (5 * i));
        transformOutputListForLoop.insert(FLrepVar3, group.pair(group.exp(Eprimeprime, group.neg(coeffs[loopVar3])), DBlinded[loopVar3]));
    }
    return;
}

void Sw05::decout(CharmList & pk, int dParam, CharmList & transformOutputList, ZR & bf0, CharmListZR & blindingFactorDBlinded, CharmListStr & SKeys, int SLen, CharmList & transformOutputListForLoop, GT & M)
{
    GT Eprime = group.init(GT_t);
    CharmListZR S;
    CharmListZR coeffs;
    GT prod = group.init(GT_t);
    string loopVar3;
    int FLrepVar2 = 0;
    int FLrepVar3 = 0;
    GT loopProd = group.init(GT_t);
    Eprime = transformOutputList[2].getGT();
    S = transformOutputList[0].getZR();
    coeffs = transformOutputList[1].getZR();
    //;
    for (int i = 0; i < SLen; i++)
    {

        loopVar3 = SKeys[i];
        FLrepVar2 = group.add(10, (5 * i));
        FLrepVar3 = group.add(11, (5 * i));
        loopProd = group.mul(group.exp(transformOutputListForLoop[FLrepVar2].getGT().getGT(), bf0), group.exp(transformOutputListForLoop[FLrepVar3].getGT().getGT(), blindingFactorDBlinded[loopVar3]));
        prod = group.mul(prod, loopProd);
    }
    M = group.mul(Eprime, prod);
    return;
}

