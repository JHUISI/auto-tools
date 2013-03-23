from userFuncs import *

from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.core.engine.util import *
from charm.core.math.integer import randomBits

group = None

N = 2

secparam = 80


def setup(n):
    M = {}
    V = {}
    m = {}
    r = {}
    t = {}
    v = {}
    R = {}
    T = {}

    input = n
    g1 = group.random(G1)
    g2 = group.random(G2)
    egg = pair(g1, g2)
    y = group.random(ZR)
    Y = (egg ** y)
    for i in range(0, n):
        t[i] = group.random(ZR)
        v[i] = group.random(ZR)
        r[i] = group.random(ZR)
        m[i] = group.random(ZR)
        T[i] = (g1 ** t[i])
        V[i] = (g1 ** v[i])
        R[i] = (g1 ** r[i])
        M[i] = (g1 ** m[i])
    pk = [g1, g2, n, Y, T, V, R, M]
    msk = [y, t, v, r, m]
    output = (pk, msk)
    return output

def keygen(pk, msk, yVector):
    LVectorBlinded = {}
    LVector = {}
    YVectorBlinded = {}
    a = {}
    blindingFactorLVectorBlinded = {}
    blindingFactorYVectorBlinded = {}
    YVector = {}

    input = [pk, msk, yVector]
    zz = group.random(ZR)
    g1 = pk[0]
    g2 = pk[1]
    n = pk[2]
    y = msk[0]
    numNonDontCares = 0
    for i in range(0, n):
        if ( ( (yVector[i]) != (2) ) ):
            numNonDontCares = (numNonDontCares + 1)
    sumUSaisUSsoFar = 0
    endForLoop = (numNonDontCares - 1)
    for i in range(0, endForLoop):
        a[i] = group.random(ZR)
        sumUSaisUSsoFar = (sumUSaisUSsoFar + a[i])
    a[numNonDontCares-1] = (y - sumUSaisUSsoFar)
    currentUSaUSindex = 0
    for i in range(0, n):
        if ( ( (yVector[i]) == (0) ) ):
            YVector[i] = (g2 ** (a[currentUSaUSindex] / msk[3][i]))
            LVector[i] = (g2 ** (a[currentUSaUSindex] / msk[4][i]))
            currentUSaUSindex = (currentUSaUSindex + 1)
        if ( ( (yVector[i]) == (1) ) ):
            YVector[i] = (g2 ** (a[currentUSaUSindex] / msk[1][i]))
            LVector[i] = (g2 ** (a[currentUSaUSindex] / msk[2][i]))
            currentUSaUSindex = (currentUSaUSindex + 1)
        if ( ( (yVector[i]) == (2) ) ):
            YVector[i] = group.init(G2)
            LVector[i] = group.init(G2)
    yLength = len(LVector)
    LVectorKeysSuffix = list(LVector.keys())
    for y in range(0, yLength):
        LVectorKeyLoopVar = LVectorKeysSuffix[y]
        blindingFactorLVectorBlinded[y] = group.random(ZR)
        LVectorBlinded[LVectorKeyLoopVar] = (LVector[LVectorKeyLoopVar] ** (1 / blindingFactorLVectorBlinded[y]))
    yLength = len(YVector)
    YVectorKeysSuffix = list(YVector.keys())
    for y in range(0, yLength):
        YVectorKeyLoopVar = YVectorKeysSuffix[y]
        blindingFactorYVectorBlinded[y] = group.random(ZR)
        YVectorBlinded[YVectorKeyLoopVar] = (YVector[YVectorKeyLoopVar] ** (1 / blindingFactorYVectorBlinded[y]))
    sk2 = [YVectorBlinded, LVectorBlinded]
    sk2Blinded = [YVectorBlinded, LVectorBlinded]
    output = (blindingFactorYVectorBlinded, blindingFactorLVectorBlinded, sk2Blinded)
    return output

def encrypt(Message, xVector, pk):
    WVector = {}
    sUSi = {}
    XVector = {}

    input = [Message, xVector, pk]
    g1 = pk[0]
    n = pk[2]
    Y = pk[3]
    s = group.random(ZR)
    for i in range(0, n):
        sUSi[i] = group.random(ZR)
    omega = (Message * (Y ** -s))
    C0 = (g1 ** s)
    for i in range(0, n):
        if ( ( (xVector[i]) == (0) ) ):
            XVector[i] = (pk[6][i] ** (s - sUSi[i]))
            WVector[i] = (pk[7][i] ** sUSi[i])
        if ( ( (xVector[i]) == (1) ) ):
            XVector[i] = (pk[4][i] ** (s - sUSi[i]))
            WVector[i] = (pk[5][i] ** sUSi[i])
    CT = [omega, C0, XVector, WVector]
    output = CT
    return output

def transform(CT, sk):
    transformOutputList = {}

    input = [CT, sk]
    omega, C0, XVector, WVector = CT
    YVector, LVector = sk
    transformOutputList[0] = len(YVector)
    n = transformOutputList[0]
    for i in range(0, n):
        if ( ( (( (YVector[i]) != (group.init(G2)) )) and (( (LVector[i]) != (group.init(G2)) )) ) ):
            transformOutputList[1000+7*i] = pair(XVector[i], YVector[i])
            intermediateResults = transformOutputList[1000+7*i]
            transformOutputList[1001+7*i] = pair(WVector[i], LVector[i])
            intermediateResults = transformOutputList[1001+7*i]
    output = transformOutputList
    return output

def decout(CT, sk, transformOutputList, blindingFactorYVectorBlinded, blindingFactorLVectorBlinded):
    input = [CT, sk, transformOutputList, blindingFactorYVectorBlinded, blindingFactorLVectorBlinded]
    omega, C0, XVector, WVector = CT
    YVector, LVector = sk
    dotProd = group.init(GT)
    n = transformOutputList[0]
    for i in range(0, n):
        if ( ( (( (YVector[i]) != (group.init(G2)) )) and (( (LVector[i]) != (group.init(G2)) )) ) ):
            intermediateResults = ((transformOutputList[1000+7*i] ** blindingFactorYVectorBlinded[i]) * (transformOutputList[1001+7*i] ** blindingFactorLVectorBlinded[i]))
            dotProd = (dotProd * intermediateResults)
    Message2 = (omega * dotProd)
    output = Message2
    return output

def SmallExp(bits=80):
    return group.init(ZR, randomBits(bits))

def main():
    global group
    group = PairingGroup(secparam)

    (pk, msk) = setup(4)
    (blindingFactorYVectorBlinded, blindingFactorLVectorBlinded, sk2Blinded) = keygen(pk, msk, [2, 1, 0, 2])
    M = group.random(GT)
    print(M)
    print("\n\n")
    CT = encrypt(M, [1, 1, 0, 1], pk)
    transformOutputList = transform(CT, sk2Blinded)
    M2 = decout(CT, sk2Blinded, transformOutputList, blindingFactorYVectorBlinded, blindingFactorLVectorBlinded)

    print(M2)
    if (M == M2):
        print("success")
    else:
        print("failed")



if __name__ == '__main__':
    main()

