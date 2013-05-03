import builtInFuncs
from builtInFuncs import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
group = None

secparam = 80


def setup():
    gG1 = group.random(G1)
    gG2 = group.random(G2)
    gpk = [gG1, gG2]
    output = gpk
    return output

def authsetup(gpk, authS):
    msk = {}
    pk = {}

    gG1 = group.random(G1)
    gG2 = group.random(G2)
    gG1, gG2 = gpk
    Y = len(authS)
    for i in range(0, Y):
        alpha = group.random(ZR)
        y = group.random(ZR)
        z = authS[i]
        eggalph = (pair(gG1, gG2) ** alpha)
        gy = (gG2 ** y)
        msk[z] = [alpha, y]
        pk[z] = [eggalph, gy]
    output = (msk, pk)
    return output

def keygen(gpk, msk, gid, userS):
    K = {}
    KBlinded = {}
    blindingFactorKBlinded = {}

    gidBlinded = gid
    gG1, gG2 = gpk
    h = group.hash(gidBlinded, G1)
    Y = len(userS)
    for i in range(0, Y):
        z = userS[i]
        K[z] = ((gG1 ** msk[z][0]) * (h ** msk[z][1]))
    for y in K:
        blindingFactorKBlinded[y] = group.random(ZR)
        KBlinded[y] = (K[y] ** (1 / blindingFactorKBlinded[y]))
    skBlinded = [gidBlinded, KBlinded]
    output = (blindingFactorKBlinded, skBlinded)
    return output

def encrypt(pk, gpk, M, policy_str):
    C2 = {}
    C1 = {}
    C3 = {}

    gG1, gG2 = gpk
    policy = createPolicy(policy_str)
    attrs = getAttributeList(policy)
    s = group.random(ZR)
    w = 0
    s_sh = calculateSharesDict(s, policy)
    w_sh = calculateSharesDict(w, policy)
    Y = len(s_sh)
    egg = pair(gG1, gG2)
    C0 = (M * (egg ** s))
    for y in range(0, Y):
        r = group.random(ZR)
        k = attrs[y]
        C1[k] = ((egg ** s_sh[k]) * (pk[k][0] ** r))
        C2[k] = (gG2 ** r)
        C3[k] = ((pk[k][1] ** r) * (gG2 ** w_sh[k]))
    ct = [policy_str, C0, C1, C2, C3]
    output = ct
    return output

def transform(skBlinded, userS, ct):
    transformOutputListForLoop = {}
    transformOutputList = {}

    policy_str, C0, C1, C2, C3 = ct
    gidBlinded, KBlinded = skBlinded
    transformOutputList[1] = C0
    policy = createPolicy(policy_str)
    attrs = prune(policy, userS)
    coeff = getCoefficients(policy)
    transformOutputList[0] = group.hash(gidBlinded, G1)
    h_gid = transformOutputList[0]
    Y = len(attrs)
    for y in range(0, Y):
        pass
        kDecrypt = GetString(attrs[y])
        FLrepVar1 = (10 + (8 * y))
        transformOutputListForLoop[FLrepVar1] = pair(h_gid, C3[kDecrypt])
        result0 = transformOutputListForLoop[FLrepVar1]
        FLrepVar2 = (11 + (8 * y))
        transformOutputListForLoop[FLrepVar2] = ((result0 ** coeff[kDecrypt]) * (C1[kDecrypt] ** coeff[kDecrypt]))
        numerator = transformOutputListForLoop[FLrepVar2]
        FLrepVar3 = (12 + (8 * y))
        transformOutputListForLoop[FLrepVar3] = pair((KBlinded[kDecrypt] ** coeff[kDecrypt]), C2[kDecrypt])
        denominator = transformOutputListForLoop[FLrepVar3]
    output = (transformOutputList, attrs, Y, transformOutputListForLoop)
    return output

def decout(userS, transformOutputList, blindingFactorKBlinded, attrs, Y, transformOutputListForLoop):
    C0 = transformOutputList[1]
    h_gid = transformOutputList[0]
    dotProd = group.init(GT)
    for y in range(0, Y):
        pass
        kDecrypt = GetString(attrs[y])
        FLrepVar1 = (10 + (8 * y))
        result0 = transformOutputListForLoop[FLrepVar1]
        FLrepVar2 = (11 + (8 * y))
        numerator = transformOutputListForLoop[FLrepVar2]
        FLrepVar3 = (12 + (8 * y))
        denominator = (transformOutputListForLoop[FLrepVar3] ** blindingFactorKBlinded[kDecrypt])
        fraction = (numerator * (denominator ** -1))
        dotProd = (dotProd * fraction)
    M = (C0 * (dotProd ** -1))
    output = M
    return output

def main():
    global group
    #group = PairingGroup(secparam)
    group = PairingGroup("SS512")

    gpk = setup()
    (msk, pk) = authsetup(gpk, ['ONE', 'TWO', 'THREE', 'FOUR'])
    (blindingFactorKBlinded, skBlinded) = keygen(gpk, msk, "john@example.com", ['ONE', 'TWO', 'THREE'])
    M = group.random(GT)
    ct = encrypt(pk, gpk, M, '((four or three) and (two or one))')
    (transformOutputList, attrs, Y, forLoop) = transform(skBlinded, ['ONE', 'TWO', 'THREE'], ct)
    M2 = decout(['ONE', 'TWO', 'THREE'], transformOutputList, blindingFactorKBlinded, attrs, Y, forLoop)
    print(M)
    print("\n\n\n")
    print(M2)
    print("\n\n")
    if (M == M2):
        print("success")
    else:
        print("failed")

if __name__ == '__main__':
    main()

