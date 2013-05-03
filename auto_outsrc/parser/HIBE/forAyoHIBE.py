import builtInFuncs
from builtInFuncs import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
group = None

secparam = 80

def stringToInt(strID, zz, ll):
    '''Hash the identity string and break it up in to l bit pieces'''
    h = hashlib.new('sha1')
    h.update(bytes(strID, 'utf-8'))
    _hash = Bytes(h.digest())
    val = Conversion.OS2IP(_hash) #Convert to integer format
    bstr = bin(val)[2:]   #cut out the 0b header

    v=[]
    for i in range(zz):  #z must be greater than or equal to 1
        binsubstr = bstr[ll*i : ll*(i+1)]
        intval = int(binsubstr, 2)
        intelement = group.init(ZR, intval)
        v.append(intelement)
    return v

def setup(l, z):
    h = {}
    delta = {}
    hb = {}

    alpha = group.random(ZR)
    beta = group.random(ZR)
    g = group.random(G1)
    gb = group.random(G2)
    g1 = (g ** alpha)
    g1b = (gb ** alpha)
    for y in range(0, l):
        delta[y] = group.random(ZR)
        h[y] = (g ** delta[y])
        hb[y] = (gb ** delta[y])
    g0b = (gb ** (alpha * beta))
    v = pair(g, g0b)
    mpk = [g, g1, h, gb, g1b, hb, v]
    mk = [g0b]
    output = (mpk, mk)
    return output

def keygen(mpk, mk, id):
    d = {}
    dBlinded = {}
    r = {}

    bf0 = group.random(ZR)
    uf0 = group.random(ZR)
    g, g1, h, gb, g1b, hb, v = mpk
    [g0b] = mk
    Id = stringToInt(id, 5, 32)
    for y in range(0, 5):
        r[y] = group.random(ZR)
        d[y] = (gb ** r[y])
    for y in d:
        dBlinded[y] = (d[y] ** (1 / bf0))
    d0DotProdCalc = group.init(G2)
    for y in range(0, 5):
        d0DotProdCalc = (d0DotProdCalc * (((g1b ** Id[y]) * hb[y]) ** r[y]))
    d0 = (g0b * d0DotProdCalc)
    d0Blinded = (d0 ** (1 / uf0))
    pk = [id]
    skBlinded = [d0Blinded, dBlinded]
    output = (pk, uf0, bf0, skBlinded)
    return output

def encrypt(mpk, pk, M):
    C = {}

    g, g1, h, gb, g1b, hb, v = mpk
    [id] = pk
    s = group.random(ZR)
    A = (M * (v ** s))
    B = (g ** s)
    Id = stringToInt(id, 5, 32)
    for y in range(0, 5):
        C[y] = (((g1 ** Id[y]) * h[y]) ** s)
    ct = [A, B, C]
    output = ct
    return output

def transform(pk, skBlinded, ct):
    transformOutputList = {}
    transformOutputListForLoop = {}

    d0Blinded, dBlinded = skBlinded
    A, B, C = ct
    transformOutputList[3] = A
    transformOutputList[0] = group.init(GT)
    finalLoopVar = transformOutputList[0]
    for y in range(0, 5):
        pass
        FLrepVar1 = (10 + (3 * y))
        transformOutputListForLoop[FLrepVar1] = pair(C[y], dBlinded[y])
        intermedLoopVar = transformOutputListForLoop[FLrepVar1]
        FLrepVar2 = (11 + (3 * y))
        transformOutputListForLoop[FLrepVar2] = (finalLoopVar * intermedLoopVar)
        finalLoopVar = transformOutputListForLoop[FLrepVar2]
    transformOutputList[1] = finalLoopVar
    D = transformOutputList[1]
    transformOutputList[2] = pair(B, d0Blinded)
    denominator = transformOutputList[2]
    output = (transformOutputList)
    return output

def decout(pk, transformOutputList, bf0, uf0):
    A = transformOutputList[3]
    finalLoopVar = transformOutputList[0]
    D = (transformOutputList[1] ** bf0)
    denominator = (transformOutputList[2] ** uf0)
    fraction = (D * (denominator ** -1))
    M = (A * fraction)
    output = M
    return output

def main():
    global group
    #group = PairingGroup(secparam)

    group = PairingGroup("SS512")

    (mpk, mk) = setup(5, 32)
    (pkBlinded, uf0, bf0, skBlinded) = keygen(mpk, mk, "test")
    M = group.random(GT)
    print(M)
    print("\n\n\n")
    ct = encrypt(mpk, pkBlinded, M)
    transformOutputList = transform(pkBlinded, skBlinded, ct)
    M2 = decout(pkBlinded, transformOutputList, bf0, uf0)
    print(M2)

    if (M == M2):
        print("it worked")
    else:
        print("it failed")


if __name__ == '__main__':
    main()

