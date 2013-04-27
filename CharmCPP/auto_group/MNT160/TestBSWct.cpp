#include "TestBSWct.h"

void Bsw07::setup(CharmList & mk, CharmList & pk)
{
    G1 gG1;
    G2 gG2;
    ZR alpha;
    ZR beta;
    G1 hG1;
    G2 hG2;
    G2 i;
    GT egg = group.init(GT_t);
    gG1 = group.random(G1_t);
    gG2 = group.random(G2_t);
    alpha = group.random(ZR_t);
    beta = group.random(ZR_t);
    hG1 = group.exp(gG1, beta);
    hG2 = group.exp(gG2, beta);
    i = group.exp(gG2, alpha);
    egg = group.exp(group.pair(gG1, gG2), alpha);
    mk.insert(0, beta);
    mk.insert(1, i);
    pk.insert(0, gG1);
    pk.insert(1, gG2);
    pk.insert(2, hG1);
    pk.insert(3, hG2);
    pk.insert(4, egg);
    return;
}

void Bsw07::keygen(CharmList & pk, CharmList & mk, CharmListStr & S, CharmList & sk)
{
    G1 gG1;
    G2 gG2;
    G1 hG1;
    G2 hG2;
    GT egg;
    ZR beta;
    G2 i;
    ZR r;
    G1 p0G1;
    G2 p0G2;
    G2 D;
    int Y = 0;
    ZR sUSy;
    string y0;
    CharmListG1 Dj;
    CharmListG2 Djp;
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    hG1 = pk[2].getG1();
    hG2 = pk[3].getG2();
    egg = pk[4].getGT();
    
    beta = mk[0].getZR();
    i = mk[1].getG2();
    r = group.random(ZR_t);
    p0G1 = group.exp(hG1, r);
    p0G2 = group.exp(hG2, r);
    D = group.exp(group.mul(i, p0G2), group.div(1, beta));
    Y = S.length();
    for (int y = 0; y < Y; y++)
    {
        sUSy = group.random(ZR_t);
        y0 = S[y];
        Dj[y0] = group.mul(p0G1, group.exp(group.hashListToG1(y0), sUSy));
        Djp[y0] = group.exp(gG2, sUSy);
    }
    sk.insert(0, D);
    sk.insert(1, Dj);
    sk.insert(2, Djp);
    return;
}

void Bsw07::encrypt(CharmList & pk, GT & M, NO_TYPE & policyUSstr, CharmList & ct)
{
    G1 gG1;
    G2 gG2;
    G1 hG1;
    G2 hG2;
    GT egg;
    Policy policy;
    CharmListStr attrs;
    ZR s;
    CharmDictZR sh;
    int Y = 0;
    GT Ctl = group.init(GT_t);
    G1 C;
    string y1;
    CharmListG2 Cr;
    CharmListG1 Cpr;
    
    gG1 = pk[0].getG1();
    gG2 = pk[1].getG2();
    hG1 = pk[2].getG1();
    hG2 = pk[3].getG2();
    egg = pk[4].getGT();
    policy = util.createPolicy(policyUSstr);
    attrs = util.getAttributeList(policy);
    s = group.random(ZR_t);
    sh = util.calculateSharesDict(group, s, policy);
    Y = sh.length();
    Ctl = group.mul(M, group.exp(egg, s));
    C = group.exp(hG1, s);
    for (int y = 0; y < Y; y++)
    {
        y1 = attrs[y];
        Cr[y1] = group.exp(gG2, sh[y1]);
        Cpr[y1] = group.exp(group.hashListToG1(y1), sh[y1]);
    }
    ct.insert(0, policystr);
    ct.insert(1, Ctl);
    ct.insert(2, C);
    ct.insert(3, Cr);
    ct.insert(4, Cpr);
    return;
}

void Bsw07::decrypt(CharmList & pk, CharmList & sk, CharmListStr & S, CharmList & ct, GT & M)
{
    string policystr;
    GT Ctl;
    G1 C;
    CharmListG2 Cr;
    CharmListG1 Cpr;
    G2 D;
    CharmListG1 Dj;
    CharmListG2 Djp;
    Policy policy;
    CharmListStr attrs;
    CharmDictZR coeff;
    int Y = 0;
    GT resVarName0 = group.init(GT_t);
    string y2;
    GT resVarName1 = group.init(GT_t);
    GT A = group.init(GT_t);
    GT result0 = group.init(GT_t);
    GT result1 = group.init(GT_t);
    
    policystr = ct[0].strPtr;
    Ctl = ct[1].getGT();
    C = ct[2].getG1();
    Cr = ct[3].getListG2();
    Cpr = ct[4].getListG1();
    
    D = sk[0].getG2();
    Dj = sk[1].getListG1();
    Djp = sk[2].getListG2();
    policy = util.createPolicy(policystr);
    attrs = util.prune(policy, S);
    coeff = util.getCoefficients(group, policy);
    Y = attrs.length();
    //;
    for (int y = 0; y < Y; y++)
    {
        y2 = GetString(attrs[y]);
        resVarName1 = group.exp(group.mul(group.pair(Dj[y2], Cr[y2]), group.exp(group.pair(Cpr[y2], Djp[y2]), -1)), coeff[y2]);
        resVarName0 = group.mul(resVarName0, resVarName1);
    }
    A = resVarName0;
    result0 = group.pair(C, D);
    result1 = group.div(result0, A);
    M = group.div(Ctl, result1);
    return;
}

