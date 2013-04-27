#include "TestBSW.h"

void Bsw07::setup(CharmList & mk, CharmList & pk)
{
    G1 g;
    ZR alpha;
    ZR beta;
    G1 h;
    G1 i;
    GT egg = group.init(GT_t);
    g = group.random(G1_t);
    alpha = group.random(ZR_t);
    beta = group.random(ZR_t);
    h = group.exp(g, beta);
    i = group.exp(g, alpha);
    egg = group.exp(group.pair(g, g), alpha);
    mk.insert(0, beta);
    mk.insert(1, i);
    pk.insert(0, g);
    pk.insert(1, h);
    pk.insert(2, egg);
    return;
}

void Bsw07::keygen(CharmList & pk, CharmList & mk, CharmListStr & S, CharmList & sk)
{
    G1 g;
    G1 h;
    GT egg;
    ZR beta;
    G1 i;
    ZR r;
    G1 p0;
    G1 D;
    int Y = 0;
    ZR sUSy;
    string y0;
    CharmListG1 Dj;
    CharmListG1 Djp;
    
    g = pk[0].getG1();
    h = pk[1].getG1();
    egg = pk[2].getGT();
    
    beta = mk[0].getZR();
    i = mk[1].getG1();
    r = group.random(ZR_t);
    p0 = group.exp(h, r);
    D = group.exp(group.mul(i, p0), group.div(1, beta));
    Y = S.length();
    for (int y = 0; y < Y; y++)
    {
        sUSy = group.random(ZR_t);
        y0 = S[y];
        Dj[y0] = group.mul(p0, group.exp(group.hashListToG1(y0), sUSy));
        Djp[y0] = group.exp(g, sUSy);
    }
    sk.insert(0, D);
    sk.insert(1, Dj);
    sk.insert(2, Djp);
    return;
}

void Bsw07::encrypt(CharmList & pk, GT & M, NO_TYPE & policyUSstr, CharmList & ct)
{
    G1 g;
    G1 h;
    GT egg;
    Policy policy;
    CharmListStr attrs;
    ZR s;
    CharmDictZR sh;
    int Y = 0;
    GT Ctl = group.init(GT_t);
    G1 C;
    string y1;
    CharmListG1 Cr;
    CharmListG1 Cpr;
    
    g = pk[0].getG1();
    h = pk[1].getG1();
    egg = pk[2].getGT();
    policy = util.createPolicy(policyUSstr);
    attrs = util.getAttributeList(policy);
    s = group.random(ZR_t);
    sh = util.calculateSharesDict(group, s, policy);
    Y = sh.length();
    Ctl = group.mul(M, group.exp(egg, s));
    C = group.exp(h, s);
    for (int y = 0; y < Y; y++)
    {
        y1 = attrs[y];
        Cr[y1] = group.exp(g, sh[y1]);
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
    CharmListG1 Cr;
    CharmListG1 Cpr;
    G1 D;
    CharmListG1 Dj;
    CharmListG1 Djp;
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
    Cr = ct[3].getListG1();
    Cpr = ct[4].getListG1();
    
    D = sk[0].getG1();
    Dj = sk[1].getListG1();
    Djp = sk[2].getListG1();
    policy = util.createPolicy(policystr);
    attrs = util.prune(policy, S);
    coeff = util.getCoefficients(group, policy);
    Y = attrs.length();
    //;
    for (int y = 0; y < Y; y++)
    {
        y2 = GetString(attrs[y]);
        resVarName1 = group.exp(group.div(group.pair(Cr[y2], Dj[y2]), group.pair(Djp[y2], Cpr[y2])), coeff[y2]);
        resVarName0 = group.mul(resVarName0, resVarName1);
    }
    A = resVarName0;
    result0 = group.pair(C, D);
    result1 = group.div(result0, A);
    M = group.div(Ctl, result1);
    return;
}

