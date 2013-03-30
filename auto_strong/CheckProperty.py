from __future__ import print_function
from z3 import *

I = IntSort()
e = Function('E', I, I, I)
x, y, z = Ints('x y z')

my_solver = Then(With('simplify', arith_lhs=True), 'normalize-bounds', 'solve-eqs', 'smt').solver()
my_solver.add( ForAll([x, y], e(x, y) == x*y) )
my_solver.add( ForAll([x, y, z], e(x+y, z) == (x*z + y*z)) )
my_solver.add( ForAll([x, y, z], e(x, y+z) == (y*x + z*x)) )

rules = [ ForAll([x, y], e(x, y) == x*y), ForAll([x, y, z], e(x+y, z) == (x*z + y*z)), ForAll([x, y, z], e(x, y+z) == (y*x + z*x)) ]

# x := random(ZR)
# y := random(ZR)
# X := g^x
# Y := g^y
# a := random(G2)
# m := H(M, ZR)
# b := a^y
# c := a^(x + (m * x * y))
# sig := list{a, b, c}
p = 2 ** 32 # upper bound

t, b, bb, c, cc, m = Ints('t b bb c cc m')
tt, xx, yy, mm = Ints('tt xx yy mm')
#my_solver.add( And(g == a, a == 2, b == 4, c == 6, d == 3 ) )
#my_solver.add( And(g == t, t != 0, t != 1) ) # , a > 1, a < p-1) )
#my_solver.add( And(x == 3, y == 4, m == 5) )
#my_solver.add( And(m == 3, ))
b = t * yy
#c = t * (x + (m * x * y))
#c = t * (xx + (m * xx * yy))


#b = a ** y
#c = a ** (x + (m * x * y))
#X = g ** x
#Y = g ** y

print(my_solver)
my_solver.check()
M = my_solver.model()
print(M, "\n")
#Verify1 = M.evaluate(e(a, Y) == e(g, b))
#Verify2 = M.evaluate(((e(X, a) + (e(X, b**m)) == e(g, c))))
#Verify2 = M.evaluate(e(X, a*(b ** m)) == e(g, c))

verify1 = e(t, y) == e(1, b)
verify2_0 = (((e(x, t) + (e(x, b) * m))) == e(1, c))
verify2_1 = (((e(x, t) + (e(x, b) * m))) == e(1, cc))


#print("Evaluate: e(a+b, c) == e(a, c+b) : ", m.evaluate(e(a+b, c) == e(a, c+b)))
##print(m.evaluate(e(a, c+1)))
#print("Evaluate: e(a, c) == e(b, d) : ", m.evaluate(e(a, c) == e(b, d)))
#print("Evaluate: (e(a, c) * e(b, c) / e(a, c) ) == e(b, c) : ", m.evaluate(((e(a, c) * e(b, c)) / e(a, c)) == e(b, c)))
#print("Evaluate: ((e(a, c) * e(b, c)) == e(b, c) * e(a, c)) : ", m.evaluate(((e(a, c) * e(b, c)) == e(b, c) * e(a, c))))

##print("Evaluate: e(a, Y) == e(g, b) : ", M.evaluate(e(a, y) == e(g, b)))
#print("Evaluate: e(X, a) * e(X, b)^M == e(g, c) : ", M.evaluate(((e(x, a) * (e(x, b) * m)) )))
#print("Evaluate: e(g, c) : ", M.evaluate(e(g, c)))
##print("Evaluate: e(X, a) * e(X, b)^M == e(g, c) : ", M.evaluate(((e(x, a) + (e(x, b*m))) == e(g, c))))

#result1 = solve(verify1, verify2, m > 1, g > 1, a > 1, y > 1) #, x > 1)
#print("Evaluate 1: ", M.evaluate(verify1), "\tSimplify: ", simplify(verify1, eq2ineq=False, ite_extra_rules=True, mul_to_power=True))
#print("Evaluate 2: ", M.evaluate(verify2), "\tSimplify: ", simplify(verify2, eq2ineq=False, ite_extra_rules=True, mul_to_power=True))
#Verify2 = simplify(M.evaluate(verify2), eq2ineq=False, ite_extra_rules=True, mul_to_power=True)

#g = Solver()
##g.add(rules)
#
#g.add(Verify2)
#g.add(x > 1, xx > 1, y > 1, ) #, m == 4, y == 5)
#g.add(x != xx, t != 0) # , m > 1, yy > 1, t > 1)
#
#if g.check() == sat:
#    print(g.model())
#else:
#    print("FAILED: ", g.check())
#max = 20
#solve_using(my_solver, verify1, verify2, t != 0, x != 0, y != 0, x != xx) #, And(t > 1, t < max), And(x > 1, x < max), And(y > 1, y < max), And(m > 1, m < max), x != xx)

t1 = Tactic("qfnra-nlsat")
t2 = Tactic("ctx-simplify")
t3 = Tactic("horn") #horn-simplify")

s  = Then(t1, t2)

g2 = Goal()
g3 = Goal()
##g.add(And(t*x + m*x*t*y == t*(xx + yy*m*xx), t > 1, y > 1, m > 1, x > 1, xx > 1, yy > 1, x != xx, y == yy) )
#g1.add(And( M.evaluate(verify1), t > 1, y > 1, yy > 1, y != yy) )
g2.add( And(M.evaluate(verify2_0), M.evaluate(verify2_1), c != cc) ) #, t > 1, m > 1, x > 1, xx > 1, yy > 1, x != xx) )


#print("Goal 1: ", g1)
#print("Result for G1: ",  s(g1) ) 
#print()
print("Goal 2: ", g2)
print("Result for G2: ",  s(g2) ) 
print("")

alpha, r = Ints('alpha r')
alpha1, r1, t1 = Ints('alpha1 r1 t1')

#s1, s1pr = Ints('s1 s1pr') # alpha * m * r
s1 = Int('s1') #alpha * t + m * r
s1pr = Int('s1pr') #alpha1 * t1 + m * r1
s2 = r

#verify3_0 = ((e(t*alpha, 1) + e(m*r, 1)) - e(s2, m)) == e(alpha, t) 
#verify3_1 = ((e(t1*alpha1, 1) + e(m*r1, 1)) - e(s2, m)) == e(alpha, t)
verify3_0 = (e(s1, 1) == (e(alpha, t) + e(s2, m))) 
verify3_1 = (e(s1pr, 1) == (e(alpha, t) + e(s2, m)))

g3.add( And(M.evaluate(verify3_0), M.evaluate(verify3_1), s1 != s1pr) )#alpha1 != alpha, r1 != r, t1 != t) ) # , r > 1, r1 > 1, t > 1, m > 1, alpha > 1, alpha1 > 1) )
print("Goal 3: ", g3)
print("Result for G3: ",  s(g3) )
print("")

verify3 = M.evaluate( ((e(t*alpha, 1) + e(m*r, 1)) - e(s2, m)) == e(alpha, t) )
print("verify3 : ", verify3)
g4 = Goal()
g4.add( And(verify3) ) #, t1 == t) )

print("Result G4: ", s(g4))

g5 = Goal()
g5.add( And( r + b == c, t + b == c, t == 0, m != s2 ))

print("Bogus: ", s(g5))

#t3 = Tactic("horn-simplify") 
#s1 = Then(t2, t3)
#
#print("New Goal 3: ", g3)
#print("Result for G3: ",  s1(g3) )

#print("EQ1: ", And(Or(M.evaluate(verify2_0), cc == 1), c != cc) )
#solve(And(Or(M.evaluate(verify2_0), cc == 1), c != cc, c > 0, cc > 0, t > 0, m > 0, x > 0, xx > 0, yy > 0))

#print("EQ2: ", M.evaluate(verify2_0), M.evaluate(verify2_1), c != cc)
#solve(And( M.evaluate(verify2_0), M.evaluate(verify2_1), c != cc, c > 0, cc > 0, t > 0, m > 0, x > 0, xx > 0, yy > 0))