import builtInFuncs
from builtInFuncs import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
group = None

secparam = 80


def setup(n):
    t = {}

    g = group.random(G1)
    y = group.random(ZR)
    g1 = (g ** y)
    g2 = group.random(G2)
    for i in range(0, n+1):
        t[i] = group.random(G2)
    pk = [g, g1, g2, t]
    mk = y
    output = (pk, mk)
    return output

def evalT(pk, n, x):
    N = {}

    g, g1, g2, t = pk
    for i in range(0, n+1):
        N[i] = (i + 1)
    coeffs = recoverCoefficientsDict(N)
    prodResult = group.init(G2)
    lenN = len(N)
    for i in range(0, lenN):
        loopVarEvalT = N[i]
        loopVarM1 = (loopVarEvalT - 1)
        prodResult = (prodResult * (t[loopVarM1] ** coeffs[loopVarEvalT]))
    T = ((g2 ** (x * n)) * prodResult)
    output = T
    return output

def extract(mk, w, pk, dParam, n):
    DBlinded = {}
    blindingFactorDBlinded = {}
    q = {}
    D = {}
    d = {}
    dBlinded = {}
    wHash = {}

    bf0 = group.random(ZR)
    wBlinded = w
    g, g1, g2, t = pk
    lenw = len(wBlinded)
    for i in range(0, lenw):
        loopVar1 = wBlinded[i]
        wHash[i] = group.hash(loopVar1, ZR)
    r = group.random(ZR)
    q[0] = mk
    for i in range(1, dParam):
        q[i] = group.random(ZR)
    shares = genSharesForX(mk, q, wHash)
    wHashLen = len(wHash)
    for i in range(0, wHashLen):
        loopVar2 = wHash[i]
        loopVar2Str = wBlinded[i]
        evalTVar = evalT(pk, n, loopVar2)
        D[loopVar2Str] = ((g2 ** shares[i]) * (evalTVar ** r))
        d[loopVar2Str] = (g ** r)
    for y in d:
        dBlinded[y] = (d[y] ** (1 / bf0))
    for y in D:
        blindingFactorDBlinded[y] = group.random(ZR)
        DBlinded[y] = (D[y] ** (1 / blindingFactorDBlinded[y]))
    skBlinded = [wBlinded, DBlinded, dBlinded]
    output = (blindingFactorDBlinded, bf0, skBlinded)
    return output

def encrypt(pk, wPrime, M, n):
    E = {}

    g, g1, g2, t = pk
    s = group.random(ZR)
    Eprime = (M * (pair(g1, g2) ** s))
    Eprimeprime = (g ** s)
    wPrimeLen = len(wPrime)
    for i in range(0, wPrimeLen):
        loopVar = group.hash(wPrime[i], ZR)
        loopVarStr = wPrime[i]
        evalTVar = evalT(pk, n, loopVar)
        E[loopVarStr] = (evalTVar ** s)
    CT = [wPrime, Eprime, Eprimeprime, E]
    output = CT
    return output

def transform(pk, skBlinded, CT, dParam):
    transformOutputList = {}
    transformOutputListForLoop = {}

    wPrime, Eprime, Eprimeprime, E = CT
    wBlinded, DBlinded, dBlinded = skBlinded
    transformOutputList[2] = Eprime
    transformOutputList[0] = intersectionSubset(wBlinded, wPrime, dParam)
    S = transformOutputList[0]
    transformOutputList[1] = recoverCoefficientsDict(S)
    coeffs = transformOutputList[1]
    SKeys = strkeys(S)
    SLen = len(S)
    for i in range(0, SLen):
        pass
        loopVar3 = SKeys[i]
        FLrepVar2 = (10 + (5 * i))
        transformOutputListForLoop[FLrepVar2] = pair((dBlinded[loopVar3] ** coeffs[loopVar3]), E[loopVar3])
        FLrepVar3 = (11 + (5 * i))
        transformOutputListForLoop[FLrepVar3] = pair((Eprimeprime ** -coeffs[loopVar3]), DBlinded[loopVar3])
    output = (transformOutputList, SKeys, SLen, transformOutputListForLoop)
    return output

def decout(pk, dParam, transformOutputList, bf0, blindingFactorDBlinded, SKeys, SLen, transformOutputListForLoop):
    Eprime = transformOutputList[2]
    S = transformOutputList[0]
    coeffs = transformOutputList[1]
    prod = group.init(GT)
    for i in range(0, SLen):
        pass
        loopVar3 = SKeys[i]
        FLrepVar2 = (10 + (5 * i))
        FLrepVar3 = (11 + (5 * i))
        loopProd = ((transformOutputListForLoop[FLrepVar2] ** bf0) * (transformOutputListForLoop[FLrepVar3] ** blindingFactorDBlinded[loopVar3]))
        prod = (prod * loopProd)
    M = (Eprime * prod)
    output = M
    return output

def main():
    global group
    #group = PairingGroup(secparam)
    group = PairingGroup("SS512")

    max_attributes = 6
    required_overlap = 4
    #(master_public_key, master_key) = setup(max_attributes, required_overlap)
    (master_public_key, master_key) = setup(max_attributes)
    private_identity = ['insurance', 'id=2345', 'oncology', 'doctor', 'nurse', 'JHU'] #private identity
    public_identity = ['insurance', 'id=2345', 'doctor', 'oncology', 'JHU', 'billing', 'misc'] #public identity for encrypt
    (blindingFactor0Blinded, bf2, skBlinded) = extract(master_key, private_identity, master_public_key, required_overlap, max_attributes)
    msg = group.random(GT)
    cipher_text = encrypt(master_public_key, public_identity, msg, max_attributes)
    #decrypted_msg = decrypt(master_public_key, secret_key, cipher_text, required_overlap)
    (transformOutputList, SKeys, SLen, fl) = transform(master_public_key, skBlinded, cipher_text, required_overlap)
    decrypted_msg = decout(master_public_key, required_overlap, transformOutputList, bf2, blindingFactor0Blinded, SKeys, SLen, fl)

    print("msg:  ", msg)
    print("decrypted_msg:  ", decrypted_msg)
    assert msg == decrypted_msg, "failed decryption!"
    print("Successful Decryption!")

if __name__ == '__main__':
    main()

