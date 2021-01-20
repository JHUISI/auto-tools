#!/bin/sh
''''exec python -- "$0" ${1+"$@"} # '''

from z3 import *
import json
import sys
import traceback

#################################################################################
# Complex numbers, see: http://leodemoura.github.io/blog/2013/01/26/complex.html
#################################################################################

def _to_complex(a):
    if isinstance(a, ComplexExpr):
        return a
    else:
        return ComplexExpr(a, RealVal(0))

def _is_zero(a):
    return (isinstance(a, int) and a == 0) or (is_rational_value(a) and a.numerator_as_long() == 0)

class ComplexExpr:
    def __init__(self, r, i):
        self.r = r
        self.i = i

    def __add__(self, other):
        other = _to_complex(other)
        return ComplexExpr(self.r + other.r, self.i + other.i)

    def __radd__(self, other):
        other = _to_complex(other)
        return ComplexExpr(other.r + self.r, other.i + self.i)

    def __sub__(self, other):
        other = _to_complex(other)
        return ComplexExpr(self.r - other.r, self.i - other.i)

    def __rsub__(self, other):
        other = _to_complex(other)
        return ComplexExpr(other.r - self.r, other.i - self.i)

    def __mul__(self, other):
        other = _to_complex(other)
        return ComplexExpr(self.r*other.r - self.i*other.i, self.r*other.i + self.i*other.r)

    # def __mul__(self, other):
    #     other = _to_complex(other)
    #     return ComplexExpr(other.r*self.r - other.i*self.i, other.i*self.r + other.r*self.i)

    def inv(self):
        den = self.r*self.r + self.i*self.i
        return ComplexExpr(self.r/den, -self.i/den)

    def __div__(self, other):
        inv_other = _to_complex(other).inv()
        return self.__mul__(inv_other)

    def __rdiv__(self, other):
        other = _to_complex(other)
        return self.inv().__mul__(other)

    def __eq__(self, other):
        other = _to_complex(other)
        return And(self.r == other.r, self.i == other.i)

    def __neq__(self, other):
        return Not(self.__eq__(other))

    def simplify(self):
        return ComplexExpr(simplify(self.r), simplify(self.i))

    def repr_i(self):
        if is_rational_value(self.i):
            return "%s*I" % self.i
        else:
            return "(%s)*I" % str(self.i)

    def __repr__(self):
        if _is_zero(self.i):
            return str(self.r)
        elif _is_zero(self.r):
            return self.repr_i()
        else:
            return "%s + %s" % (self.r, self.repr_i())

def Complex(a):
    return ComplexExpr(Real('%s.r' % a), Real('%s.i' % a))

I = ComplexExpr(RealVal(0), RealVal(1))

def ComplexVal(i):
    return ComplexExpr(RealVal(i), RealVal(0))

def evaluate_cexpr(m, e):
    return ComplexExpr(m[e.r], m[e.i])

class CompFunction:
  def __init__(self, name):
    self.r = Function('%s_r' % name, IntSort(), RealSort())
    self.i = Function('%s_i' % name, IntSort(), RealSort())

  def __eq__(self, other):
    return ForAll([j], And( self.r(j) == other.r(j)
                          , self.i(j) == other.i(j)))

  def isZero(self):
    return ForAll([j], And( self.r(j) == Real(0)
                          , self.i(j) == Real(0)))

  def notContainsComplex(self,c):
    return Not(Exists([j], And( self.r(j) == c.r
                              , self.i(j) == c.i)))

  def app(self,j):
    return ComplexExpr(self.r(j), self.i(j))

def translate_monom(vs):
  res = None
  for v in vs:
    if res is None:
      res = Int(v)
    else:
      res = res * Int(v)
  return (1 if res is None else res)

def trans_constr(c):
  if c[0] == "int":
    return ComplexExpr(RealVal(c[1]),RealVal(0))
  elif c[0] == "scalar":
    return Complex(c[1])
  elif c[0] == "app":
    return CompFunction(c[1]).app(Int(c[2]))
  elif c[0] == "forall":
    return ForAll([Int(c[1])], trans_constr(c[2]))
  elif c[0] == "eqz":
    return (trans_constr(c[1]) == 0)
  elif c[0] == "eq":
    return (trans_constr(c[1]) == trans_constr(c[2]))
  elif c[0] == "and":
    return (And(trans_constr(c[1]),trans_constr(c[2])))
  elif c[0] == "or":
    return (Or(trans_constr(c[1]),trans_constr(c[2])))
  elif c[0] == "not":
    return (Not(trans_constr(c[1])))
  elif c[0] == "mult":
    return (trans_constr(c[1]) * trans_constr(c[2]))
  elif c[0] == "add":
    return (trans_constr(c[1]) + trans_constr(c[2]))


###############################################################################
# Infrastructure functions: Debugging, json conversion
###############################################################################

debug_enabled = True

def debug(s):
  if debug_enabled:
    sys.stderr.write('### ')
    sys.stderr.write(s)
    sys.stderr.write('\n')
    sys.stderr.flush()

def _parseJSON(obj):
  """Convert unicode strings to standard strings"""
  if isinstance(obj, dict):
      newobj = {}
      for key, value in obj.iteritems():
          key = str(key)
          newobj[key] = _parseJSON(value)
  elif isinstance(obj, list):
      newobj = []
      for value in obj:
          newobj.append(_parseJSON(value))
  elif isinstance(obj, unicode):
      newobj = str(obj)
  else:
      newobj = obj
  return newobj

def translate_monom(constr,vs):
  res = None
  for v in vs:
    if res is None:
      res = constr(v)
    else:
      res = res * constr(v)
  return (1 if res is None else res)

def translate_poly(constr,ts):
  res = None
  for t in ts:
    (m,c) = t
    pm = translate_monom(constr,m)
    pt = (pm if c == 1 else c * pm)
    #debug("res: " + str(res) + "\tts: " + str(ts) + "\tpm: " + str(pm) + "\tpt: " + str(res + pt))
    if res is None:
      res = pt
    else:
      #debug("else")
      res += pt
    #debug("res after: "+str(res)+"\n")

  #debug("return "+str(res)+"\n")
  return (0 if res is None else res)

###############################################################################
# Interpreter for GGT commands
###############################################################################

def interp(req):
  cmd = req['cmd']

  if cmd == "paramSolve":
    eqs  = req['eqs']
    leqs = req['leqs']

    s = Solver()

    for a,b in eqs:
      #debug("%s = %s"%(str(translate_poly(a)), str(translate_poly(b))))
      s.add(translate_poly(Int,a) == translate_poly(Int,b))
    for a,b in leqs:
      # debug("%s <= %s"%(str(translate_poly(a)), str(translate_poly(b))))
      s.add(translate_poly(Int,a) <= translate_poly(Int,b))
    #print s.sexpr()
    #debug(str(s.sexpr()))
    #print(s.check())
    res = s.check()
    #debug(str(res))
    if res == sat:
      return { "ok": True
             , "res": "sat"
             , "model": str(s.model())}
    elif res == unsat:
      return { "ok": True
             , "res": "unsat" }
    else:
      return { "ok": True
             , "res": "unknown" }

  if cmd == "checkSat":
    constrs = req['constrs']
    s = Solver()

    for c in constrs:
      s.add(trans_constr(c))
    #print s.sexpr()
    #debug(str(s.sexpr()))
    #print(s.check())
    res = s.check()
    if res == sat:
      return { "ok": True
             , "res": "sat"
             , "model": str(s.model())}
    elif res == unsat:
      return { "ok": True
             , "res": "unsat" }
    else:
      return { "ok": True
             , "res": "unknown" }

  if cmd == "boundedCounter":
    zero = req['zero']
    nzero = req['nzero']

    s = Solver()
    for f in zero:
      s.add( translate_poly(Real,f) == 0 )
    for disj in nzero:
      s.add( Not(And([ (translate_poly(Real,f) == 0) for f in disj])) )

    #debug(str(s.sexpr()))
    res = s.check()
    #debug(str(res))
    if res == sat:
      m = s.model()
      res = sorted(((k,str(m[k])) for k in m if str(m[k]) != "0"), lambda x,y: cmp(str(x[0]),str(y[0])))
      res = "\n".join(map(lambda x: "  %s = %s"%(x[0],x[1]),res))
      #debug(str(list((k,m[k]) for k in m)))
      return { "ok": True
             , "res": "sat"
	     , "model": "nonzero coefficients:\n"+res}
    elif res == unsat:
      return { "ok": True
             , "res": "unsat" }
    else:
      return { "ok": True
             , "res": "unknown" }

  elif cmd == "exit":
    print("end\n")
    exit()

  else:
    return { 'ok': False
           , 'error': "unknown command" }

def main():
  try:
    inp = sys.stdin.readline()
    #debug(inp)
    cmd = json.loads(inp)
    cmd = _parseJSON(cmd)
    res = interp(cmd)
    #debug(str(res))
    print(json.dumps(res))
    sys.stdout.flush()
  except Exception:
      if debug_enabled:
        traceback.print_exc()
      print(json.dumps({ 'ok': False
                       , 'error': "unknown error" }))

def test():
  print interp(
     { 'cmd': "checkSat"
     , 'constrs': [
           ["eq",["scalar","V_1"],["scalar","V_1"]]
          ,["eqz",["scalar","U_0"]]
          ,["eqz",["scalar","U_1"]]
          ,["eqz",["scalar","V_0"]]
          ,["eqz",["scalar","V_1"]]
          ,["eqz",["scalar","V_c"]]
          ,["eqz",["scalar","W_1"]]
          ,["eqz",["scalar","W_c"]]
          ,["forall","i0",["eq",["app","U_o1_0","i0"],["app","U_o1_0","i0"]]]
          ,["forall","i0",["eqz",["app","U_o1_0","i0"]]]
          ,["forall","i0",["eq",["mult",["app","m_o1_p","i0"],["app","V_o1_2","i0"]],["app","U_o1_2","i0"]]]
          ,["forall","i0",["eqz",
             ["add",["mult",["app","m_o1_p","i0"],["app","U_o1_2","i0"]],["mult",["scalar","fc_m'"],["app","U_o1_2","i0"]]]]]
          ,["forall","i0",["eqz",["app","U_o1_1","i0"]]]
          ,["forall","i0",["eqz",["app","U_o1_2","i0"]]]
          ,["forall","i0",["eqz",["app","V_o1_0","i0"]]]
          ,["forall","i0",["eqz",["app","V_o1_2","i0"]]]
          ,["forall","i0",["eqz",["app","W_o1_0","i0"]]]
          ,["forall","i0",["eqz",["app","W_o1_1","i0"]]]
          ,["forall","i0",["not",["eq",["app","m_o1_p","i0"],["int",0]]]]
          ,["forall","i0",["not",["eq",["app","m_o1_p","i0"],["scalar","fc_m'"]]]]
          ,["not",["and",["eqz",["scalar","U_0"]],["and",["eqz",["scalar","U_1"]],["and",["eqz",["scalar","V_1"]],["and",["forall","i0",["eqz",["mult",["app","m_o1_p","i0"],["app","U_o1_2","i0"]]]],["and",["forall","i0",["eqz",["app","U_o1_0","i0"]]],["and",["forall","i0",["eqz",["app","U_o1_1","i0"]]],["forall","i0",["eqz",["app","U_o1_2","i0"]]]]]]]]]]
          ,["not",["eqz",["scalar","fc_m'"]]]
      ]
  })

if __name__ == "__main__":
  if "test" in sys.argv:
    test()
  else:
    main()
