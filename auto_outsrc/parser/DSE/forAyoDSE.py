import builtInFuncs
from builtInFuncs import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
group = None

secparam = 80


def setup():
    gG1 = group.random(G1)
    gG2 = group.random(G2)
    w = group.random(ZR)
    wG1 = (gG1 ** w)
    wG2 = (gG2 ** w)
    u = group.random(ZR)
    uG1 = (gG1 ** u)
    uG2 = (gG2 ** u)
    h = group.random(ZR)
    hG1 = (gG1 ** h)
    hG2 = (gG2 ** h)
    v = group.random(ZR)
    vG1 = (gG1 ** v)
    vG2 = (gG2 ** v)
    v1 = group.random(ZR)
    v1G1 = (gG1 ** v1)
    v1G2 = (gG2 ** v1)
    v2 = group.random(ZR)
    v2G1 = (gG1 ** v2)
    v2G2 = (gG2 ** v2)
    a1 = group.random(ZR)
    a2 = group.random(ZR)
    b = group.random(ZR)
    alpha = group.random(ZR)
    gbG1 = (gG1 ** b)
    gbG2 = (gG2 ** b)
    ga1 = (gG2 ** a1)
    ga2 = (gG2 ** a2)
    gba1 = (gbG2 ** a1)
    gba2 = (gbG2 ** a2)
    tau1 = (vG2 * (v1G2 ** a1))
    tau2 = (vG2 * (v2G2 ** a2))
    tau1b = (tau1 ** b)
    tau2b = (tau2 ** b)
    egga = (pair(gG1, gG2) ** (alpha * (a1 * b)))
    galpha = (gG1 ** alpha)
    galphaUSa1 = (galpha ** a1)
    mpk = [gG1, gG2, gbG1, gbG2, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, wG1, wG2, uG1, uG2, hG1, hG2, egga]
    msk = [galpha, galphaUSa1, vG1, vG2, v1G1, v1G2, v2G1, v2G2, alpha]
    output = (mpk, msk)
    return output

def keygen(mpk, msk, id):
    uf0 = group.random(ZR)
    bf0 = group.random(ZR)
    uf1 = group.random(ZR)
    idBlinded = id
    gG1, gG2, gbG1, gbG2, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, wG1, wG2, uG1, uG2, hG1, hG2, egga = mpk
    galpha, galphaUSa1, vG1, vG2, v1G1, v1G2, v2G1, v2G2, alpha = msk
    r1 = group.random(ZR)
    r2 = group.random(ZR)
    z1 = group.random(ZR)
    z2 = group.random(ZR)
    tagUSk = group.random(ZR)
    tagUSkBlinded = (tagUSk ** (1 / bf0))
    r = (r1 + r2)
    idUShash = group.hash(idBlinded, ZR)
    D1 = (galphaUSa1 * (vG1 ** r))
    D1Blinded = (D1 ** (1 / uf0))
    D2 = (((gG1 ** -alpha) * (v1G1 ** r)) * (gG1 ** z1))
    D2Blinded = (D2 ** (1 / bf0))
    D3 = (gbG1 ** -z1)
    D3Blinded = (D3 ** (1 / bf0))
    D4 = ((v2G1 ** r) * (gG1 ** z2))
    D4Blinded = (D4 ** (1 / bf0))
    D5 = (gbG1 ** -z2)
    D5Blinded = (D5 ** (1 / bf0))
    D6 = (gbG1 ** r2)
    D6Blinded = (D6 ** (1 / bf0))
    D7 = (gG1 ** r1)
    D7Blinded = (D7 ** (1 / bf0))
    K = ((((uG1 ** idUShash) * (wG1 ** tagUSkBlinded)) * hG1) ** r1)
    KBlinded = (K ** (1 / uf1))
    skBlinded = [idBlinded, D1Blinded, D2Blinded, D3Blinded, D4Blinded, D5Blinded, D6Blinded, D7Blinded, KBlinded, tagUSkBlinded]
    output = (uf0, bf0, uf1, skBlinded)
    return output

def encrypt(mpk, M, id):
    gG1, gG2, gbG1, gbG2, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, wG1, wG2, uG1, uG2, hG1, hG2, egga = mpk
    s1 = group.random(ZR)
    s2 = group.random(ZR)
    t = group.random(ZR)
    tagUSc = group.random(ZR)
    s = (s1 + s2)
    idUShash2 = group.hash(id, ZR)
    C0 = (M * (egga ** s2))
    C1 = (gbG2 ** s)
    C2 = (gba1 ** s1)
    C3 = (ga1 ** s1)
    C4 = (gba2 ** s2)
    C5 = (ga2 ** s2)
    C6 = ((tau1 ** s1) * (tau2 ** s2))
    C7 = (((tau1b ** s1) * (tau2b ** s2)) * (wG2 ** -t))
    E1 = ((((uG2 ** idUShash2) * (wG2 ** tagUSc)) * hG2) ** t)
    E2 = (gG2 ** t)
    ct = [C0, C1, C2, C3, C4, C5, C6, C7, E1, E2, tagUSc]
    output = ct
    return output

def transform(ct, skBlinded):
    transformOutputList = {}

    idBlinded, D1Blinded, D2Blinded, D3Blinded, D4Blinded, D5Blinded, D6Blinded, D7Blinded, KBlinded, tagUSkBlinded = skBlinded
    C0, C1, C2, C3, C4, C5, C6, C7, E1, E2, tagUSc = ct
    transformOutputList[6] = C0
    transformOutputList[0] = ((tagUSc - tagUSkBlinded) ** -1)
    tag = transformOutputList[0]
    transformOutputList[1] = pair(C1, D1Blinded)
    transformOutputList[2] = (((pair(C2, D2Blinded) * pair(C3, D3Blinded)) * pair(C4, D4Blinded)) * pair(C5, D5Blinded))
    transformOutputList[3] = (pair(C6, D6Blinded) * pair(C7, D7Blinded))
    A2 = transformOutputList[3]
    transformOutputList[4] = pair(E1, D7Blinded)
    transformOutputList[5] = pair((E2 ** -1), KBlinded)
    output = transformOutputList
    return output

def decout(transformOutputList, bf0, uf0, uf1):
    C0 = transformOutputList[6]
    tag = transformOutputList[0]
    A1 = ((transformOutputList[1] ** uf0) * (transformOutputList[2] ** bf0))
    A2 = (transformOutputList[3] ** bf0)
    A3 = (A1 * (A2 ** -1))
    A4 = ((transformOutputList[4] ** bf0) * (transformOutputList[5] ** uf1))
    result0 = (A4 ** tag)
    result1 = (A3 * (result0 ** -1))
    M = (C0 * (result1 ** -1))
    output = M
    return output

def main():
    global group
    #group = PairingGroup(secparam)
    group = PairingGroup('SS512')

    (mpk, msk) = setup()
    (uf0, bf0, uf1, skBlinded) = keygen(mpk, msk, "john@example.com")
    M = group.random(GT)
    print(M)
    print("\n\n\n")
    ct = encrypt(mpk, M, "john@example.com")
    transformOutputList = transform(ct, skBlinded)
    M2 = decout(transformOutputList, bf0, uf0, uf1)


    print(M2)
    if (M == M2):
        print("successful decryption for outsourcing!!!")
    else:
        print("failed decryption.")

if __name__ == '__main__':
    main()

