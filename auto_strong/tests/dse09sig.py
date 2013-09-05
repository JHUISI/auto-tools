import builtInFuncs
from builtInFuncs import *
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
group = None

secparam = 80


def keygen():
    g = group.random(G1)
    w = group.random(G1)
    u = group.random(G1)
    h = group.random(G1)
    v = group.random(G1)
    v1 = group.random(G1)
    v2 = group.random(G1)
    a1 = group.random(ZR)
    a2 = group.random(ZR)
    b = group.random(ZR)
    alpha = group.random(ZR)
    gb = (g ** b)
    ga1 = (g ** a1)
    ga2 = (g ** a2)
    gba1 = (gb ** a1)
    gba2 = (gb ** a2)
    tau1 = (v * (v1 ** a1))
    tau2 = (v * (v2 ** a2))
    tau1b = (tau1 ** b)
    tau2b = (tau2 ** b)
    A = (pair(g, g) ** (alpha * (a1 * b)))
    galpha = (g ** alpha)
    galphaa1 = (galpha ** a1)
    pk = [g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, A]
    sk = [galpha, galphaa1, v, v1, v2, alpha]
    output = (pk, sk)
    return output

def sign(pk, sk, m):
    g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, A = pk
    galpha, galphaa1, v, v1, v2, alpha = sk
    r1 = group.random(ZR)
    r2 = group.random(ZR)
    z1 = group.random(ZR)
    z2 = group.random(ZR)
    tagk = group.random(ZR)
    r = (r1 + r2)
    M = group.hash(m, ZR)
    S1 = (galphaa1 * (v ** r))
    S2 = (((g ** -alpha) * (v1 ** r)) * (g ** z1))
    S3 = (gb ** -z1)
    S4 = ((v2 ** r) * (g ** z2))
    S5 = (gb ** -z2)
    S6 = (gb ** r2)
    S7 = (g ** r1)
    SK = ((((u ** M) * (w ** tagk)) * h) ** r1)
    sig = [S1, S2, S3, S4, S5, S6, S7, SK, tagk]
    output = sig
    return output

def verify(pk, m, sig):
    g, gb, ga1, ga2, gba1, gba2, tau1, tau2, tau1b, tau2b, w, u, h, A = pk
    S1, S2, S3, S4, S5, S6, S7, SK, tagk = sig
    s1 = group.random(ZR)
    s2 = group.random(ZR)
    t = group.random(ZR)
    tagc = group.random(ZR)
    s = (s1 + s2)
    M = group.hash(m, ZR)
    theta = (1 / (tagc - tagk))
    if ( ( ((pair((gb ** s), S1) * (pair((gba1 ** s1), S2) * (pair((ga1 ** s1), S3) * (pair((gba2 ** s2), S4) * pair((ga2 ** s2), S5)))))) == ((pair(S6, ((tau1 ** s1) * (tau2 ** s2))) * (pair(S7, ((tau1b ** s1) * ((tau2b ** s2) * (w ** -t)))) * (((pair(S7, (((u ** (M * t)) * (w ** (tagc * t))) * (h ** t))) * pair((g ** -t), SK)) ** theta) * (A ** s2))))) ) ):
        output = True
        return output
    else:
        return False

def main():
    global group
    group = PairingGroup(secparam)

if __name__ == '__main__':
    main()

