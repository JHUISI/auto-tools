#include "TestCKRSOut.h"

int n = 5;
int l = 32;

void Ibeckrs09::setup(int n, int l, CharmList & mpk, CharmList & msk)
{
    ZR alpha;
    ZR t1;
    ZR t2;
    ZR t3;
    ZR t4;
    G1 g;
    G2 h;
    GT omega = group.init(GT_t);
    CharmListZR z;
    CharmListG1 gl;
    CharmListG2 hl;
    G1 v1;
    G1 v2;
    G1 v3;
    G1 v4;
    alpha = group.random(ZR_t);
    t1 = group.random(ZR_t);
    t2 = group.random(ZR_t);
    t3 = group.random(ZR_t);
    t4 = group.random(ZR_t);
    g = group.random(G1_t);
    h = group.random(G2_t);
    omega = group.exp(group.pair(g, h), group.mul(t1, group.mul(t2, alpha)));
    for (int y = 0; y < n; y++)
    {
        z.insert(y, group.random(ZR_t));
        gl.insert(y, group.exp(g, z[y]));
        hl.insert(y, group.exp(h, z[y]));
    }
    v1 = group.exp(g, t1);
    v2 = group.exp(g, t2);
    v3 = group.exp(g, t3);
    v4 = group.exp(g, t4);
    mpk.insert(0, omega);
    mpk.insert(1, g);
    mpk.insert(2, h);
    mpk.insert(3, gl);
    mpk.insert(4, hl);
    mpk.insert(5, v1);
    mpk.insert(6, v2);
    mpk.insert(7, v3);
    mpk.insert(8, v4);
    mpk.insert(9, n);
    mpk.insert(10, l);
    msk.insert(0, alpha);
    msk.insert(1, t1);
    msk.insert(2, t2);
    msk.insert(3, t3);
    msk.insert(4, t4);
    return;
}

void Ibeckrs09::extract(CharmList & mpk, CharmList & msk, string & id, ZR & uf1, CharmList & skBlinded)
{
    string idBlinded;
    GT omega;
    G1 g;
    G2 h;
    CharmListG1 gl;
    CharmListG2 hl;
    G1 v1;
    G1 v2;
    G1 v3;
    G1 v4;
    int n;
    int l;
    ZR alpha;
    ZR t1;
    ZR t2;
    ZR t3;
    ZR t4;
    ZR r1;
    ZR r2;
    CharmListZR hID;
    G2 reservedVarName0;
    G2 reservedVarName1;
    G2 hashIDDotProd;
    G2 hashID;
    G2 d0;
    G2 d0Blinded;
    G2 halpha;
    G2 hashID2r1;
    G2 d1;
    G2 d1Blinded;
    G2 d2;
    G2 d2Blinded;
    G2 hashID2r2;
    G2 d3;
    G2 d3Blinded;
    G2 d4;
    G2 d4Blinded;
    G2 d5;
    G2 d5Blinded;
    uf1 = group.random(ZR_t);
    idBlinded = id;
    
    omega = mpk[0].getGT();
    g = mpk[1].getG1();
    h = mpk[2].getG2();
    gl = mpk[3].getListG1();
    hl = mpk[4].getListG2();
    v1 = mpk[5].getG1();
    v2 = mpk[6].getG1();
    v3 = mpk[7].getG1();
    v4 = mpk[8].getG1();
    n = mpk[9].getInt();
    l = mpk[10].getInt();
    
    alpha = msk[0].getZR();
    t1 = msk[1].getZR();
    t2 = msk[2].getZR();
    t3 = msk[3].getZR();
    t4 = msk[4].getZR();
    r1 = group.random(ZR_t);
    r2 = group.random(ZR_t);
    hID = stringToInt(group, idBlinded, n, l);
    //;
    for (int y = 0; y < n; y++)
    {
        reservedVarName1 = group.exp(hl[y], hID[y]);
        reservedVarName0 = group.mul(reservedVarName0, reservedVarName1);
    }
    hashIDDotProd = reservedVarName0;
    hashID = group.mul(hl[0], hashIDDotProd);
    d0 = group.exp(h, group.add(group.mul(r1, group.mul(t1, t2)), group.mul(r2, group.mul(t3, t4))));
    d0Blinded = group.exp(d0, group.div(1, uf1));
    halpha = group.exp(h, group.neg(alpha));
    hashID2r1 = group.exp(hashID, group.neg(r1));
    d1 = group.mul(group.exp(halpha, t2), group.exp(hashID2r1, t2));
    d1Blinded = group.exp(d1, group.div(1, uf1));
    d2 = group.mul(group.exp(halpha, t1), group.exp(hashID2r1, t1));
    d2Blinded = group.exp(d2, group.div(1, uf1));
    hashID2r2 = group.exp(hashID, group.neg(r2));
    d3 = group.exp(hashID2r2, t4);
    d3Blinded = group.exp(d3, group.div(1, uf1));
    d4 = group.exp(hashID2r2, t3);
    d4Blinded = group.exp(d4, group.div(1, uf1));
    d5 = group.mul(group.exp(h, t1), group.exp(h, t2));
    d5Blinded = group.exp(d5, group.div(1, uf1));
    skBlinded.insert(0, idBlinded);
    skBlinded.insert(1, d0Blinded);
    skBlinded.insert(2, d1Blinded);
    skBlinded.insert(3, d2Blinded);
    skBlinded.insert(4, d3Blinded);
    skBlinded.insert(5, d4Blinded);
    skBlinded.insert(6, d5Blinded);
    return;
}

void Ibeckrs09::encrypt(CharmList & mpk, GT & M, string & id, CharmList & ct)
{
    GT omega;
    G1 g;
    G2 h;
    CharmListG1 gl;
    CharmListG2 hl;
    G1 v1;
    G1 v2;
    G1 v3;
    G1 v4;
    int n;
    int l;
    ZR s;
    ZR s1;
    ZR s2;
    CharmListZR hID1;
    G1 reservedVarName2;
    G1 reservedVarName3;
    G1 hashID1DotProd;
    G1 hashID1;
    GT cpr = group.init(GT_t);
    G1 c0;
    G1 c1;
    G1 c2;
    G1 c3;
    G1 c4;
    
    omega = mpk[0].getGT();
    g = mpk[1].getG1();
    h = mpk[2].getG2();
    gl = mpk[3].getListG1();
    hl = mpk[4].getListG2();
    v1 = mpk[5].getG1();
    v2 = mpk[6].getG1();
    v3 = mpk[7].getG1();
    v4 = mpk[8].getG1();
    n = mpk[9].getInt();
    l = mpk[10].getInt();
    s = group.random(ZR_t);
    s1 = group.random(ZR_t);
    s2 = group.random(ZR_t);
    hID1 = stringToInt(group, id, n, l);
    //;
    for (int y = 0; y < n; y++)
    {
        reservedVarName3 = group.exp(gl[y], hID1[y]);
        reservedVarName2 = group.mul(reservedVarName2, reservedVarName3);
    }
    hashID1DotProd = reservedVarName2;
    hashID1 = group.mul(gl[0], hashID1DotProd);
    cpr = group.mul(group.exp(omega, s), M);
    c0 = group.exp(hashID1, s);
    c1 = group.exp(v1, group.sub(s, s1));
    c2 = group.exp(v2, s1);
    c3 = group.exp(v3, group.sub(s, s2));
    c4 = group.exp(v4, s2);
    ct.insert(0, c0);
    ct.insert(1, c1);
    ct.insert(2, c2);
    ct.insert(3, c3);
    ct.insert(4, c4);
    ct.insert(5, cpr);
    return;
}

void Ibeckrs09::transform(CharmList & skBlinded, CharmList & ct, CharmList & transformOutputList)
{
    string idBlinded;
    G2 d0Blinded;
    G2 d1Blinded;
    G2 d2Blinded;
    G2 d3Blinded;
    G2 d4Blinded;
    G2 d5Blinded;
    G1 c0;
    G1 c1;
    G1 c2;
    G1 c3;
    G1 c4;
    GT cpr;
    GT result = group.init(GT_t);
    
    idBlinded = skBlinded[0].strPtr;
    d0Blinded = skBlinded[1].getG2();
    d1Blinded = skBlinded[2].getG2();
    d2Blinded = skBlinded[3].getG2();
    d3Blinded = skBlinded[4].getG2();
    d4Blinded = skBlinded[5].getG2();
    d5Blinded = skBlinded[6].getG2();
    
    c0 = ct[0].getG1();
    c1 = ct[1].getG1();
    c2 = ct[2].getG1();
    c3 = ct[3].getG1();
    c4 = ct[4].getG1();
    cpr = ct[5].getGT();
    transformOutputList.insert(1, cpr);
    transformOutputList.insert(0, group.mul(group.mul(group.mul(group.mul(group.pair(c0, d0Blinded), group.pair(c1, d1Blinded)), group.pair(c2, d2Blinded)), group.pair(c3, d3Blinded)), group.pair(c4, d4Blinded)));
    result = transformOutputList[0].getGT();
    return;
}

void Ibeckrs09::decout(CharmList & transformOutputList, ZR & uf1, GT & M)
{
    GT cpr = group.init(GT_t);
    GT result = group.init(GT_t);
    cpr = transformOutputList[1].getGT();
    result = group.exp(transformOutputList[0].getGT(), uf1);
    M = group.mul(cpr, result);
    return;
}

