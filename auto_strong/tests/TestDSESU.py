import builtInFuncs
from builtInFuncs import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
import schnorr
import dse09sig
group = None

secparam = "SS512"


def keygen():
    varK = dse09sig.keygen()
    pk = varK[0]
    sk = varK[1]
    keyP = schnorr.keygenP()
    ppk = keyP[0]
    psk = keyP[1]
    suSK = [sk, psk]
    suPK = [pk, ppk]
    output = (suSK, suPK)
    return output

def sign(suSK, pk, m):
    sk, psk = suSK
    keyS = schnorr.keygenS(psk)
    spk = keyS[0]
    ssk = keyS[1]
    varM = (spk, m)
    varM1 = DeriveKey(varM)
    sig1 = dse09sig.sign(pk, sk, varM1)
    sig2 = schnorr.sign(psk, ssk, sig1)
    sig = [sig1, sig2, spk]
    output = sig
    return output

def verify(suPK, m, sig):
    sig1, sig2, spk = sig
    pk, ppk = suPK
    varM = (spk, m)
    varM1 = DeriveKey(varM)
    if ( ( (( (dse09sig.verify(pk, varM1, sig1)) == (True) )) and (( (schnorr.verify(ppk, spk, sig1, sig2)) == (True) )) ) ):
        output = True
        return output
    else:
        return False

def main():
    global group
    group = PairingGroup(secparam)
    schnorr.group = group
    dse09sig.group = group
    builtInFuncs.groupObj = group

    (suSK, suPK) = keygen()
    pk, ppk = suPK

    m = "hello world"
    sig = sign(suSK, pk, m)
       
    assert verify(suPK, m, sig), "invalid signature!"
    print("Successful Verification!!!")

if __name__ == '__main__':
    main()

