from sage.all import *
from sage.libs.singular.function import singular_function
from sage.rings.all import ZZ


import sys

real_stdout = sys.stdout
wrong_stdout = open("/dev/null",'w')

def enable_print():
  sys.stdout = real_stdout

def disable_print():
  sys.stdout = wrong_stdout

def coeff(f, m):
  """
  Returns coefficient of monomial m in f.
  Works with univariate polynomials and multivariate
  Singular polynomials.
  """
  try:
    return f.monomial_coefficient(m)
  except AttributeError:
    return f.coeff(m)

def monomials(f):
  return [ s[1] for s in f ]

def print_matrix(name,M):
  print "%s %s:\n"%(name,str(M.dimensions())), M

def special_zeros(T,M):
  """
  Given a transformation matrix T and the transformed
  matrix M in upper triangular form, return polynomial
  g such that if g(a) <> 0, then T(a) has non-zero
  determinant and M(a) has the same zero rows as M.
  """
  # FIXME: find more principled way to do this
  def wfactor(g):
    # try:
    #   return g.factor()
    # except AttributeError:
      try:
        if g.is_unit():
          return []
        else:
          return [(g,1)]
      except NotImplementedError:
        return [(g,1)]

  from_det    =  [ x[0] for x in wfactor(det(T)) ]
  from_pivots = []
  for i in range(min(M.ncols(), M.nrows())):
    if M[i,i] != 0:
      from_pivots += [ f[0] for f in wfactor(M[i,i]) ]
  return prod(list(set(from_det + from_pivots)),1)

def apply_swap(M,swapped):
  """
  Takes a (column) swap tuple produced by bareiss(M) and
  applies it to M.
  swapped[j] = k means that column k was moved to position j
  """
  if swapped is None:
    return None
  Mres = M.__copy__() # copy to get a matrix of the right dimension
  for j in range(len(swapped)):
    #print "swapped: j", j, "becomes", swapped[j]
    Mres[:,j] = M[:,swapped[j]]
  not_swapped = [i for i in range(M.ncols()) if i not in swapped]
  for j in range(len(not_swapped)):
    #print "not_swapped: j", j+len(swapped), "becomes", not_swapped[j]
    Mres[:,j+len(swapped)] = M[:,not_swapped[j]]
  return Mres

def echelon_form_trans(M0):
  """
  Compute bareiss and also return transformation matrix.
  """
  R = M0.base_ring()

  MI = MatrixSpace(R,M0.nrows()).identity_matrix()

  M = M0.augment(MI)

  #print "\nbefore: \n", M

  rn = M0.nrows()
  cn = M0.ncols()
  swapped = range(cn)

  def find_pivot(M,i):
    for j in range(i,cn):
      for w in range(i,rn):
        if not M[w,j].is_zero():
          return j,w
    return None

  for i in range(rn):
    #print "#"*70
    #print "i: ", i
    #print "M:\n", M
    #print "swapped: ", swapped
    # swap if necessary
    pivot = find_pivot(M,i)
    #print "pivot: ", pivot
    if pivot is None:
      # print "No nonzero found, done"
      break
    (j,w) = pivot
    if i != j:
      #print "swapping column i,j: ", i, j
      M.swap_columns(i,j)
      sj = swapped[j]
      swapped[j] = swapped[i]
      swapped[i] = sj
    if w != i:
      M.swap_rows(i,w)
    for u in range(i+1,rn):
      if not M[u,i].is_zero():
        # FIXME: find better way to do this
        #print "gcd", M[i,i], M[u,i]
        # try:
        #   g = gcd(M[i,i], M[u,i])
        # except TypeError:
        #   g = R(1)
        # a = R(M[i,i] / g)
        # b = R(M[u,i] / g)
        a = R(M[i,i])
        b = R(M[u,i])
        #print "g:", g, "a:", a, "b:", b
        M.set_row_to_multiple_of_row(u, u, a)
        M.add_multiple_of_row(u,i,-b)

  #print "\nafter: \n", M

  Mt = M[:,- MI.nrows():]
  Mres = M[:,:M0.ncols()]

  assert(Mt*(apply_swap(M0,swapped)) == Mres)

  return Mres,Mt,tuple(swapped)

from sage.libs.singular.function import singular_function
from sage.libs.singular.function import lib as singular_lib
singular_lib('primdecint.lib')
primdecZ = singular_function('primdecZ')
radicalZ = singular_function('radicalZ')

def primdec_ZZ(I):
  R = I.ring()
  P = primdecZ(I)
  V = [ R.ideal(X[0]) for X in P]
  return V

def radical_ZZ(I):
  R = I.ring()
  r = radicalZ(I)
  return R.ideal(r)

class FoundAttack(Exception):
  def __init__(self, value):
    self.descr = value


def get_kernel(H,T):
  return [ T[i] for i in range(H.nrows()) if H[i].is_zero() ]

def map_coefficient(f,g):
  return sum([ f(c) * m for (c,m) in g ])

explored = 0
leaves = 0
visited = set([])
attacks = set([])

def check_decision_aux(BR,I,Ml0,Mr0,left,right,depth=0):
  global explored
  global leaves
  global attacks

  print "checking for V(I) where I = ", I.gens_reduced()
  print "Depth: ", depth, " explored: ", explored, " leaves:", leaves

  explored += 1
  if I.is_zero():
    BRQ = BR
    pi = lambda x : x
    lift = lambda x : x
  else:
    BRQ = BR.quotient(I)
    pi = BRQ.cover()
    lift = lambda x: BRQ.lift(x)

  Ml = matrix([ [ pi(e) for e in r] for r in Ml0 ])
  Mr = matrix([ [ pi(e) for e in r] for r in Mr0 ])

  (Hl,Tl,_) = echelon_form_trans(Ml)
  (Hr,Tr,_) = echelon_form_trans(Mr)
  # print_matrix("\nTl:", Tl)
  # print_matrix("\nHl:", Hl)
  # print_matrix("\nTr:", Tr)
  # print_matrix("\nHr:", Hr)

  Kl = get_kernel(Hl,Tl)
  Kr = get_kernel(Hr,Tr)

  # print_matrix("\nKl:", matrix(Kl))
  # print_matrix("\nKr:", matrix(Kr))

  def reduce_I(f):
    return map_coefficient( lambda f: f.reduce(I), f)

  def check_eqs(eqs,M,M_other,side,side_other,l,l_other):
    R = l_other[0].base_ring()
    for v in eqs:
      assert (v * M == 0)
      r = v * M_other
      if r != 0:
        eq = " + ".join([ "(%s) * L[%d]"%(str(lift(f)), i)  for i,f in enumerate(v) if f != 0])
        eqs_o = " + ".join([ "(%s)"%(str(reduce_I(lift(f)*l_other[i])))
                             for i,f in enumerate(v) ])
        eq_res_o = map_coefficient( lambda f: f.reduce(I)
                                  , sum([ R(lift(f))*l_other[i] for i,f in enumerate(v) ]))
        eqs = " + ".join([ "(%s)"%(str(reduce_I(lift(f)*l[i])))
                           for i,f in enumerate(v) ])
        eq_res = reduce_I(sum([ R(lift(f))*l[i] for i,f in enumerate(v) ]))

        attack = (eq,
          "The following equality holds for %s, but not for %s (%d varieties explored so far):\n"%(
             side,side_other,explored)
          + "%s\n [on the %s] \n = %s\n = %s\n"%(eq,side_other,eqs_o,str(eq_res_o))
          + " [on the %s] \n = %s\n = %s\n"%(side,eqs,str(eq_res))
          + "for choices of parameters in V(I) for I = %s."%str(sorted(I.gens_reduced())))

        attacks.add(attack)

  check_eqs(Kl,Ml,Mr,"left","right",left,right)
  check_eqs(Kr,Mr,Ml,"right","left",right,left)

  # still have to check the exceptional values
  gl = lift(special_zeros(Tl,Hl))
  gr = lift(special_zeros(Tr,Hr))

  Il = primdec_ZZ(radical_ZZ(BR.ideal(gl) + I)) if gl != 1 else []
  Ir = primdec_ZZ(radical_ZZ(BR.ideal(gr) + I)) if gr != 1 else []
  Is = list(set(Il+Ir))
  #print "\nexceptional values:", Is
  for I in Is:
    if I != BR.ideal(1) and not I in visited:
      check_decision_aux(BR,I,Ml0,Mr0,left,right,depth=depth+1)
      visited.add(I)

  leaves += 1

def check_decision(PR,left,right):
  global explored
  global leaves
  global visited
  global attacks
  explored = 0
  leaves = 0
  visited = set([])
  attacks = set([])

  BR = PR.base_ring()

  mons = list(set([m for f in left + right for m in monomials(f)]))

  Ml_aug = matrix(  [ [ m for m in mons ] ]
                     + [ [ BR(coeff(f,m)) for m in mons] for f in left ])
  print_matrix("Ml_aug", Ml_aug)
  Ml = matrix([ [ coeff(f,m) for m in mons] for f in left ])
  Mr_aug = matrix(  [ [ m for m in mons ] ]
                      + [ [ BR(coeff(f,m)) for m in mons ] for f in right ])
  print_matrix("\nMr_aug", Mr_aug)
  Mr = matrix([ [ coeff(f,m) for m in mons ] for f in right ])

  check_decision_aux(BR,BR.ideal(BR(0)),Ml,Mr,left,right)
  if attacks == set([]):
    print "Verified assumption."
  else:
    attacks = sorted(list(attacks), key=lambda x: len(x[0]))
    print "%d attack(s) found."%len(attacks)
    print "1. Smallest attack:"
    print attacks[0][1]
    print "\nOther attacks:"
    for i, a in enumerate(attacks[1:]):
      print "%d."%(i+2), a[1], "\n"

# ##############################################################################
#
# # Handling the second assumption of Abdalla and Pointcheval (CDDH2)

def CDDH2(left_string,right_string):
  BR = PolynomialRing(ZZ,'x0,x1,x2,y0,y1,y2')
  (x0,x1,x2,y0,y1,y2) = BR.gens()
  
  PR = PolynomialRing(BR, 'U,V,R0,R1')
  (U,V,R0,R1) = PR.gens()
  
  # X = g^x0 * U^x1 * V^x2
  X = x0 + x1*U + x2*V
  # Y = g^y0 * U^y1 * V^y2
  Y = y0 + y1*U + y2*V
  
  # We have four cases:
  # l1: left  /\ b0 = 0 /\ b1 = 0
  l1_1 = (X - U)*R0
  l1_2 = (X -V)*R0
  l1_3 = Y*R0
  
  # l2: left  /\ b0 = 1 /\ b1 = 1
  l2_1 = (X - U)*R1
  l2_2 = (X -V)*R1
  l2_3 = Y*R0
  
  # r1: right /\ b0 = 0 /\ b1 = 1
  r1_1 = (X - U)*R0
  r1_2 = (X -V)*R1
  r1_3 = Y*R0
  
  # r2: right /\ b0 = 1 /\ b0 = 0
  r2_1 = (X - U)*R1
  r2_2 = (X -V)*R0
  r2_3 = Y*R0
  
  l1 = [l1_1,l1_2,l1_3]
  l2 = [l2_1,l2_2,l2_3]
  r1 = [r1_1,r1_2,r1_3]
  r2 = [r2_1,r2_2,r2_3]
  
  probs = {'l1':l1, 'l2':l2, 'r1':r1, 'r2':r2}
  left_prob = probs[left_string]
  right_prob = probs[right_string]
  check_decision(PR,left_prob,right_prob)
  # check_decision(PR,l1,l2)
  # check_decision(PR,r1,r2)
  #
  # check_decision(PR,l1,r1)
  # check_decision(PR,l1,r2)
  #
  # check_decision(PR,l2,r1)
  # check_decision(PR,l2,r2)

##############################################################################

# Handling the first assumption of Abdalla and Pointcheval (CDDH1)

def CDDH1(left_string,right_string):
  BR = PolynomialRing(ZZ,'y0,y1,y2,y3')
  (y0,y1,y2,y3) = BR.gens()

  PR = PolynomialRing(BR, 'U,V,X,R0,R1')
  (U,V,X,R0,R1) = PR.gens()

  # Y = g^y0 * U^y1 * V^y2 * X^y3
  Y = y0 + y1*U + y2*V + y3*X

  # We have four cases:
  # l1: left  /\ b0 = 0 /\ b1 = 0
  l1_1 = (X - U)*R0
  l1_2 = (X - U)*Y*R0
  l1_3 = (X - V)*R0
  l1_4 = (X - V)*Y*R0
  l1_5 = Y*R0

  # l2: left  /\ b0 = 1 /\ b1 = 1
  l2_1 = (X - U)*R1
  l2_2 = (X - U)*Y*R1
  l2_3 = (X - V)*R1
  l2_4 = (X - V)*Y*R1
  l2_5 = Y*R0

  # r1: right /\ b0 = 0 /\ b1 = 1
  r1_1 = (X - U)*R0
  r1_2 = (X - U)*Y*R0
  r1_3 = (X - V)*R1
  r1_4 = (X - V)*Y*R1
  r1_5 = Y*R0

  # r2: right /\ b0 = 1 /\ b1 = 0
  r2_1 = (X - U)*R1
  r2_2 = (X - U)*Y*R1
  r2_3 = (X - V)*R0
  r2_4 = (X - V)*Y*R0
  r2_5 = Y*R0

  l1 = [l1_1,l1_2,l1_3,l1_4,l1_5]
  l2 = [l2_1,l2_2,l2_3,l2_4,l2_5]
  r1 = [r1_1,r1_2,r1_3,r1_4,r1_5]
  r2 = [r2_1,r2_2,r2_3,r2_4,r2_5]

  # check_decision(PR,l1,l2)
  # check_decision(PR,r1,r2)

  # check_decision(PR,l1,r1)
  # check_decision(PR,l1,r2)

  # check_decision(PR,l2,r1)
  # check_decision(PR,l2,r2)
  probs = {'l1':l1, 'l2':l2, 'r1':r1, 'r2':r2}
  left_prob = probs[left_string]
  right_prob = probs[right_string]
  check_decision(PR,left_prob,right_prob)

def usage():
  print "interactive <1|2> <l1|l2|r1|r2> <l1|l2|r1|r2>"

print sys.argv
if len(sys.argv) != 4:
  usage()

prob = sys.argv[1]
left_string = sys.argv[2]
right_string = sys.argv[3]

if prob == "1":
  CDDH1(left_string,right_string)
elif prob == "2":
  CDDH2(left_string,right_string)
else:
  usage()
