#include "TestACDKorig.h"

void Acdk12::setup(CharmList & gk)
{
    G1 G;
    G1 C;
    G1 F;
    G1 U1;
    G1 U2;
    G = group.random(G1_t);
    C = group.random(G1_t);
    F = group.random(G1_t);
    U1 = group.random(G1_t);
    U2 = group.random(G1_t);
    gk.insert(0, G);
    gk.insert(1, C);
    gk.insert(2, F);
    gk.insert(3, U1);
    gk.insert(4, U2);
    return;
}

void Acdk12::keygen(CharmList & gk, CharmList & vk, CharmList & sk)
{
    G1 G;
    G1 C;
    G1 F;
    G1 U1;
    G1 U2;
    G1 V;
    G1 V1;
    G1 V2;
    G1 H;
    ZR a1;
    ZR a2;
    ZR b;
    ZR alpha;
    ZR rho;
    G1 B;
    G1 A1;
    G1 A2;
    G1 B1;
    G1 B2;
    G1 R1;
    G1 R2;
    G1 W1;
    G1 W2;
    G1 X1;
    G1 X2;
    G1 K1;
    G1 K2;
    
    G = gk[0].getG1();
    C = gk[1].getG1();
    F = gk[2].getG1();
    U1 = gk[3].getG1();
    U2 = gk[4].getG1();
    V = group.random(G1_t);
    V1 = group.random(G1_t);
    V2 = group.random(G1_t);
    H = group.random(G1_t);
    a1 = group.random(ZR_t);
    a2 = group.random(ZR_t);
    b = group.random(ZR_t);
    alpha = group.random(ZR_t);
    rho = group.random(ZR_t);
    B = group.exp(G, b);
    A1 = group.exp(G, a1);
    A2 = group.exp(G, a2);
    B1 = group.exp(B, a1);
    B2 = group.exp(B, a2);
    R1 = group.mul(V, group.exp(V1, a1));
    R2 = group.mul(V, group.exp(V2, a2));
    W1 = group.exp(R1, b);
    W2 = group.exp(R2, b);
    X1 = group.exp(G, rho);
    X2 = group.exp(G, group.div(group.mul(group.mul(alpha, a1), b), rho));
    K1 = group.exp(G, alpha);
    K2 = group.exp(K1, a1);
    vk.insert(0, B);
    vk.insert(1, A1);
    vk.insert(2, A2);
    vk.insert(3, B1);
    vk.insert(4, B2);
    vk.insert(5, R1);
    vk.insert(6, R2);
    vk.insert(7, W1);
    vk.insert(8, W2);
    vk.insert(9, V);
    vk.insert(10, V1);
    vk.insert(11, V2);
    vk.insert(12, H);
    vk.insert(13, X1);
    vk.insert(14, X2);
    sk.insert(0, K1);
    sk.insert(1, K2);
    return;
}

void Acdk12::sign(CharmList & gk, CharmList & vk, CharmList & sk, ZR & m1, ZR & m2, CharmList & M, CharmList & sig)
{
    G1 G;
    G1 C;
    G1 F;
    G1 U1;
    G1 U2;
    G1 B;
    G1 A1;
    G1 A2;
    G1 B1;
    G1 B2;
    G1 R1;
    G1 R2;
    G1 W1;
    G1 W2;
    G1 V;
    G1 V1;
    G1 V2;
    G1 H;
    G1 X1;
    G1 X2;
    G1 K1;
    G1 K2;
    G1 newM1;
    G1 newM2;
    G1 newM3;
    G1 newM4;
    G1 newM5;
    G1 newM6;
    ZR r1;
    ZR r2;
    ZR z1;
    ZR z2;
    ZR r;
    G1 S0;
    G1 S1;
    G1 S2;
    G1 S3;
    G1 S4;
    G1 S5;
    G1 S6;
    G1 S7;
    
    G = gk[0].getG1();
    C = gk[1].getG1();
    F = gk[2].getG1();
    U1 = gk[3].getG1();
    U2 = gk[4].getG1();
    
    B = vk[0].getG1();
    A1 = vk[1].getG1();
    A2 = vk[2].getG1();
    B1 = vk[3].getG1();
    B2 = vk[4].getG1();
    R1 = vk[5].getG1();
    R2 = vk[6].getG1();
    W1 = vk[7].getG1();
    W2 = vk[8].getG1();
    V = vk[9].getG1();
    V1 = vk[10].getG1();
    V2 = vk[11].getG1();
    H = vk[12].getG1();
    X1 = vk[13].getG1();
    X2 = vk[14].getG1();
    
    K1 = sk[0].getG1();
    K2 = sk[1].getG1();
    newM1 = group.exp(C, m1);
    newM2 = group.exp(C, m2);
    newM3 = group.exp(F, m1);
    newM4 = group.exp(F, m2);
    newM5 = group.exp(U1, m1);
    newM6 = group.exp(U2, m2);
    r1 = group.random(ZR_t);
    r2 = group.random(ZR_t);
    z1 = group.random(ZR_t);
    z2 = group.random(ZR_t);
    r = group.add(r1, r2);
    S0 = group.exp(group.mul(group.mul(newM5, newM6), H), r1);
    S1 = group.mul(K2, group.exp(V, r));
    S2 = group.mul(group.mul(group.exp(K1, -1), group.exp(V1, r)), group.exp(G, z1));
    S3 = group.exp(B, group.neg(z1));
    S4 = group.mul(group.exp(V2, r), group.exp(G, z2));
    S5 = group.exp(B, group.neg(z2));
    S6 = group.exp(B, r2);
    S7 = group.exp(G, r1);
    M.insert(0, newM1);
    M.insert(1, newM2);
    M.insert(2, newM3);
    M.insert(3, newM4);
    M.insert(4, newM5);
    M.insert(5, newM6);
    sig.insert(0, S0);
    sig.insert(1, S1);
    sig.insert(2, S2);
    sig.insert(3, S3);
    sig.insert(4, S4);
    sig.insert(5, S5);
    sig.insert(6, S6);
    sig.insert(7, S7);
    return;
}

bool Acdk12::verify(CharmList & gk, CharmList & vk, CharmList & M, CharmList & sig)
{
    G1 B;
    G1 A1;
    G1 A2;
    G1 B1;
    G1 B2;
    G1 R1;
    G1 R2;
    G1 W1;
    G1 W2;
    G1 V;
    G1 V1;
    G1 V2;
    G1 H;
    G1 X1;
    G1 X2;
    G1 newM1;
    G1 newM2;
    G1 newM3;
    G1 newM4;
    G1 newM5;
    G1 newM6;
    G1 S0;
    G1 S1;
    G1 S2;
    G1 S3;
    G1 S4;
    G1 S5;
    G1 S6;
    G1 S7;
    G1 G;
    G1 C;
    G1 F;
    G1 U1;
    G1 U2;

    G = gk[0].getG1();
    C = gk[1].getG1();
    F = gk[2].getG1();
    U1 = gk[3].getG1();
    U2 = gk[4].getG1();

    B = vk[0].getG1();
    A1 = vk[1].getG1();
    A2 = vk[2].getG1();
    B1 = vk[3].getG1();
    B2 = vk[4].getG1();
    R1 = vk[5].getG1();
    R2 = vk[6].getG1();
    W1 = vk[7].getG1();
    W2 = vk[8].getG1();
    V = vk[9].getG1();
    V1 = vk[10].getG1();
    V2 = vk[11].getG1();
    H = vk[12].getG1();
    X1 = vk[13].getG1();
    X2 = vk[14].getG1();
    
    newM1 = M[0].getG1();
    newM2 = M[1].getG1();
    newM3 = M[2].getG1();
    newM4 = M[3].getG1();
    newM5 = M[4].getG1();
    newM6 = M[5].getG1();
    
    S0 = sig[0].getG1();
    S1 = sig[1].getG1();
    S2 = sig[2].getG1();
    S3 = sig[3].getG1();
    S4 = sig[4].getG1();
    S5 = sig[5].getG1();
    S6 = sig[6].getG1();
    S7 = sig[7].getG1();
    if ( ( (( (( (( (( (( (( (group.pair(S7, group.mul(newM5, group.mul(newM6, H)))) == (group.pair(G, S0)) )) && (( (group.mul(group.pair(S1, B), group.mul(group.pair(S2, B1), group.pair(S3, A1)))) == (group.mul(group.pair(S6, R1), group.pair(S7, W1))) )) )) && (( (group.mul(group.mul(group.pair(S1, B), group.pair(S4, B2)), group.pair(S5, A2))) == (group.mul(group.mul(group.pair(S6, R2), group.pair(S7, W2)), group.pair(X1, X2))) )) )) && (( (group.pair(F, newM1)) == (group.pair(C, newM3)) )) )) && (( (group.pair(F, newM2)) == (group.pair(C, newM4)) )) )) && (( (group.pair(U1, newM1)) == (group.pair(C, newM5)) )) )) && (( (group.pair(U2, newM2)) == (group.pair(C, newM6)) )) ) )
    {
        return true;
    }
    else
    {
        return false;
    }
}

