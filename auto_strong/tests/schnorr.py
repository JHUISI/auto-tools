import builtInFuncs
from builtInFuncs import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
group = None

secparam = "SS512"


def keygenP():
    k = group.random(ZR)
    g = group.random(G1)
    x = group.random(ZR)
    X = (g ** x)
    ppk = [k, g, X]
    psk = [k, g, x]
    output = (ppk, psk)
    return output

def keygenS(psk):
    k, g, x = psk
    y = group.random(ZR)
    Y = (g ** y)
    spk = Y
    ssk = [Y, y]
    output = (spk, ssk)
    return output

def sign(psk, ssk, m):
    k, g, x = psk
    Y, y = ssk
    c = group.hash((k, Y, m), ZR)
    s = (y + (c * x))
    output = s
    return output

def verify(ppk, spk, m, s):
    k, g, X = ppk
    c = group.hash((k, spk, m), ZR)
    if ( ( ((g ** s)) == ((spk * (X ** c))) ) ):
        output = True
        return output
    else:
        return False

def main():
    global group
    group = PairingGroup(secparam)

    (ppk, psk) = keygenP()

    (spk, ssk) = keygenS(psk)

    m = "hello world"
    sig = sign(psk, ssk, m)

    assert verify(ppk, spk, m, sig), "invalid signature!!!"
    print("Successful Verification!")

if __name__ == '__main__':
    main()

