import builtInFuncs
from builtInFuncs import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
group = None

secparam = 80


def setup():
    gG1 = group.random(G1)
    gG2 = group.random(G2)
    alpha = group.random(ZR)
    beta = group.random(ZR)
    hG1 = (gG1 ** beta)
    hG2 = (gG2 ** beta)
    i = (gG1 ** alpha)
    egg = (pair(gG1, gG2) ** alpha)
    mk = [beta, i]
    pk = [gG1, gG2, hG1, hG2, egg]
    output = (mk, pk)
    return output

def keygen(pk, mk, S):
    Djp = {}
    DjpBlinded = {}
    DjBlinded = {}
    Dj = {}

    bf0 = group.random(ZR)
    uf0 = group.random(ZR)
    gG1, gG2, hG1, hG2, egg = pk
    beta, i = mk
    r = group.random(ZR)
    p0 = (hG1 ** r)
    D = ((i * p0) ** (1 / beta))
    DBlinded = (D ** (1 / uf0))
    Y = len(S)
    for y in range(0, Y):
        sUSy = group.random(ZR)
        y0 = S[y]
        Dj[y0] = (p0 * (group.hash(y0, G1) ** sUSy))
        Djp[y0] = (gG2 ** sUSy)
    for y in Dj:
        DjBlinded[y] = (Dj[y] ** (1 / bf0))
    for y in Djp:
        DjpBlinded[y] = (Djp[y] ** (1 / bf0))
    skBlinded = [DBlinded, DjBlinded, DjpBlinded]
    output = (uf0, bf0, skBlinded)
    return output

def encrypt(pk, M, policyUSstr):
    Cpr = {}
    Cr = {}

    gG1, gG2, hG1, hG2, egg = pk
    policy = createPolicy(policyUSstr)
    attrs = getAttributeList(policy)
    s = group.random(ZR)
    sh = calculateSharesDict(s, policy)
    Y = len(sh)
    Ctl = (M * (egg ** s))
    C = (hG2 ** s)
    for y in range(0, Y):
        y1 = attrs[y]
        Cr[y1] = (gG2 ** sh[y1])
        Cpr[y1] = (group.hash(y1, G1) ** sh[y1])
    ct = [policyUSstr, Ctl, C, Cr, Cpr]
    output = ct
    return output

def transform(pk, skBlinded, S, ct):
    transformOutputListForLoop = {}
    transformOutputList = {}

    policyUSstr, Ctl, C, Cr, Cpr = ct
    DBlinded, DjBlinded, DjpBlinded = skBlinded
    transformOutputList[3] = Ctl
    policy = createPolicy(policyUSstr)
    attrs = prune(policy, S)
    coeff = getCoefficients(policy)
    Y = len(attrs)
    transformOutputList[0] = group.init(GT)
    reservedVarName0 = transformOutputList[0]
    for y in range(0, Y):
        pass
        yGetStringSuffix = GetString(attrs[y])
        FLrepVar1 = (10 + (5 * y))
        transformOutputListForLoop[FLrepVar1] = (pair((Cr[yGetStringSuffix] ** coeff[yGetStringSuffix]), DjBlinded[yGetStringSuffix]) * pair((DjpBlinded[yGetStringSuffix] ** -coeff[yGetStringSuffix]), Cpr[yGetStringSuffix]))
        reservedVarName1 = transformOutputListForLoop[FLrepVar1]
        FLrepVar2 = (11 + (5 * y))
        transformOutputListForLoop[FLrepVar2] = (reservedVarName0 * reservedVarName1)
        reservedVarName0 = transformOutputListForLoop[FLrepVar2]
    transformOutputList[1] = reservedVarName0
    A = transformOutputList[1]
    transformOutputList[2] = pair(C, DBlinded)
    result0 = transformOutputList[2]
    output = (transformOutputList)
    return output

def decout(pk, S, transformOutputList, bf0, uf0):
    Ctl = transformOutputList[3]
    reservedVarName0 = transformOutputList[0]
    A = (transformOutputList[1] ** bf0)
    result0 = (transformOutputList[2] ** uf0)
    result1 = (result0 * (A ** -1))
    M = (Ctl * (result1 ** -1))
    output = M
    return output

def main():
    global group
    #group = PairingGroup(secparam)
    group = PairingGroup('SS512')

    attrs = ['ONE', 'TWO', 'THREE']
    access_policy = '((four or three) and (two or one))'

    (mk, pk) = setup()

    (uf0, bf0, skBlinded) = keygen(pk, mk, attrs)

    rand_msg = group.random(GT)
    print("msg =>", rand_msg)
    ct = encrypt(pk, rand_msg, access_policy)
    transformOutputList = transform(pk, skBlinded, attrs, ct)
    rec_msg = decout(pk, attrs, transformOutputList, bf0, uf0)
    print("Rec msg =>", rec_msg)

    assert rand_msg == rec_msg, "FAILED Decryption: message is incorrect"
    print("Successful Decryption!!!")

if __name__ == '__main__':
    main()

