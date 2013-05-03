import builtInFuncs
from builtInFuncs import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
group = None

secparam = 80


def setup(n):
    glG1 = {}
    glG2 = {}

    gG1 = group.random(G1)
    gG2 = group.random(G2)
    alpha = group.random(ZR)
    index = ((2 * n) + 1)
    for i in range(1, index):
        glG1[i] = (gG1 ** (alpha ** i))
        glG2[i] = (gG2 ** (alpha ** i))
    gamma = group.random(ZR)
    v = (gG2 ** gamma)
    pk = [gG1, gG2, glG1, glG2, v]
    msk = [gamma]
    output = (pk, msk, n)
    return output

def keygen(pk, msk, n):
    sBlinded = {}
    s = {}

    bf0 = group.random(ZR)
    gG1, gG2, glG1, glG2, v = pk
    [gamma] = msk
    for i in range(1, n+1):
        s[i] = (glG1[i] ** gamma)
    for y in s:
        sBlinded[y] = (s[y] ** (1 / bf0))
    skBlinded = [sBlinded]
    output = (bf0, skBlinded)
    return output

def encrypt(S, pk, n):
    gG1, gG2, glG1, glG2, v = pk
    t = group.random(ZR)
    K = (pair(glG1[n], glG2[1]) ** t)
    dotProd1 = group.init(G2)
    for j in S:
        dotProd1 = (dotProd1 * glG2[n+1-j])
    Hdr2 = ((v * dotProd1) ** t)
    Hdr1 = (gG2 ** t)
    Hdr = [Hdr1, Hdr2]
    ct = [Hdr, K]
    output = ct
    return output

def transform(S, i, n, Hdr, pk, skBlinded):
    transformOutputList = {}
    transformOutputListForLoop = {}

    Hdr1, Hdr2 = Hdr
    gG1, gG2, glG1, glG2, v = pk
    [sBlinded] = skBlinded
    transformOutputList[0] = pair(glG1[i], Hdr2)
    numerator = transformOutputList[0]
    transformOutputList[1] = group.init(G1)
    dotProd2 = transformOutputList[1]
    lenS = len(S)
    for k in range(0, lenS):
        pass
        j = S[k]
        if ( ( (j) != (i) ) ):
            pass
            FLrepVar2 = (10 + (5 * k))
            transformOutputListForLoop[FLrepVar2] = (dotProd2 * glG1[n+1-j+i])
            dotProd2 = transformOutputListForLoop[FLrepVar2]
    transformOutputList[2] = pair(sBlinded[i], Hdr1)
    transformOutputList[3] = pair(dotProd2, Hdr1)
    output = (transformOutputList)
    return output

def decout(S, i, n, Hdr, pk, transformOutputList, bf0):
    Hdr1, Hdr2 = Hdr
    gG1, gG2, glG1, glG2, v = pk
    numerator = transformOutputList[0]
    dotProd2 = transformOutputList[1]
    denominator = ((transformOutputList[2] ** bf0) * transformOutputList[3])
    K = (numerator * (denominator ** -1))
    output = K
    return output

def main():
    global group
    #group = PairingGroup(secparam)
    group = PairingGroup('SS512')

    (pk, msk, n) = setup(15)
    (blindingFactor0Blinded, skComplete) = keygen(pk, msk, n)
    S = [1, 3, 5, 12, 14]
    (Hdr, K) = encrypt(S, pk, n)
    print("K:  ", K)
    i = 1
    transformOutputList = transform(S, i, n, Hdr, pk, skComplete)
    Krecovered = decout(S, i, n, Hdr, pk, transformOutputList, blindingFactor0Blinded)
    print("Recovered K = ", Krecovered)
    if (K == Krecovered):
        print("Successful")
    else:
        print("Failed")

if __name__ == '__main__':
    main()

