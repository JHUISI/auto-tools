import builtInFuncs
from builtInFuncs import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
group = None

secparam = 80


def setup():
    g1 = group.random(G1)
    g2 = group.random(G2)
    alpha = group.random(ZR)
    a = group.random(ZR)
    egg = (pair(g1, g2) ** alpha)
    g1alph = (g1 ** alpha)
    g2alph = (g2 ** alpha)
    g1a = (g1 ** a)
    g2a = (g2 ** a)
    msk = [g1alph, g2alph]
    pk = [g1, g2, egg, g1a, g2a]
    output = (msk, pk)
    return output

def keygen(pk, msk, S):
    KlBlinded = {}
    Kl = {}

    bf0 = group.random(ZR)
    g1, g2, egg, g1a, g2a = pk
    g1alph, g2alph = msk
    t = group.random(ZR)
    K = (g2alph * (g2a ** t))
    KBlinded = (K ** (1 / bf0))
    L = (g2 ** t)
    LBlinded = (L ** (1 / bf0))
    Y = len(S)
    for y in range(0, Y):
        z = S[y]
        Kl[z] = (group.hash(z, G1) ** t)
    for y in Kl:
        KlBlinded[y] = (Kl[y] ** (1 / bf0))
    skBlinded = [KBlinded, LBlinded, KlBlinded]
    output = (bf0, skBlinded)
    return output

def encrypt(pk, M, policy_str):
    Dn = {}
    Cn = {}

    g1, g2, egg, g1a, g2a = pk
    policy = createPolicy(policy_str)
    attrs = getAttributeList(policy)
    s = group.random(ZR)
    sh = calculateSharesList(s, policy)
    Y = len(sh)
    C = (M * (egg ** s))
    Cpr = (g1 ** s)
    for y in range(0, Y):
        r = group.random(ZR)
        k = attrs[y]
        x = sh[y]
        Cn[k] = ((g1a ** x) * (group.hash(k, G1) ** -r))
        Dn[k] = (g2 ** r)
    ct = [policy_str, C, Cpr, Cn, Dn]
    output = ct
    return output

def transform(pk, skBlinded, S, ct):
    transformOutputListForLoop = {}
    transformOutputList = {}

    policy_str, C, Cpr, Cn, Dn = ct
    KBlinded, LBlinded, KlBlinded = skBlinded
    transformOutputList[3] = C
    policy = createPolicy(policy_str)
    attrs = prune(policy, S)
    coeff = getCoefficients(policy)
    Y = len(attrs)
    transformOutputList[0] = group.init(GT)
    reservedVarName0 = transformOutputList[0]
    for y in range(0, Y):
        pass
        yGetStringSuffix = GetString(attrs[y])
        FLrepVar1 = (1000 + (5 * y))
        transformOutputListForLoop[FLrepVar1] = (pair((Cn[yGetStringSuffix] ** coeff[yGetStringSuffix]), LBlinded) * pair((KlBlinded[yGetStringSuffix] ** coeff[yGetStringSuffix]), Dn[yGetStringSuffix]))
        reservedVarName1 = transformOutputListForLoop[FLrepVar1]
        FLrepVar2 = (1001 + (5 * y))
        transformOutputListForLoop[FLrepVar2] = (reservedVarName0 * reservedVarName1)
        reservedVarName0 = transformOutputListForLoop[FLrepVar2]
    transformOutputList[1] = reservedVarName0
    A = transformOutputList[1]
    transformOutputList[2] = pair(Cpr, KBlinded)
    result0 = transformOutputList[2]
    output = (transformOutputList)
    return output

def decout(pk, S, transformOutputList, bf0):
    C = transformOutputList[3]
    reservedVarName0 = transformOutputList[0]
    A = (transformOutputList[1] ** bf0)
    result0 = (transformOutputList[2] ** bf0)
    result1 = (result0 * (A ** -1))
    M = (C * (result1 ** -1))
    output = M
    return output

def main():
    global group
    #group = PairingGroup(secparam)
    group = PairingGroup("SS512")

    (msk, pk) = setup()
    S = ['THREE', 'ONE', 'TWO']
    (blindingFactor0Blinded, skBlinded) = keygen(pk, msk, S)
    policy_str = '((ONE or THREE) and (TWO or FOUR))'
    M = group.random(GT)
    print(M)
    print("\n\n\n")
    ct = encrypt(pk, M, policy_str)
    transformOutputList = transform(pk, skBlinded, S, ct)
    M2 = decout(pk, S, transformOutputList, blindingFactor0Blinded)
    print(M2)

    if (M == M2):
        print("it worked")
    else:
        print("it failed")

if __name__ == '__main__':
    main()

