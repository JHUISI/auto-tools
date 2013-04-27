from z3 import *
from itertools import combinations
import src.sdlpath
import sdlparser.SDLParser as sdl
from sdlparser.SDLang import *

"""
format of config file:

# default input style
variables = [ 'x', 'y', 'z' ]
clauses = [ ('x', 'y'), ('y', 'z'), ('x', 'z') ]
constraints = ['x']
mofn = ['y', 'z']

OR
# alternative input
sk = ['x', 'y']
ct = ['z']
constraints = [sk , ct] # if each index is a list instead of string
searchBoth = True # mode that forces the solver to come up w/ a bunch of solutions...

# format of results...
satisfiable = True or False
resultDictionary = [('x', True), ('y', False), ... ]
"""
verboseKeyword = "verbose"
variableKeyword = "variables"
clauseKeyword = "clauses"
constraintKeyword = "constraints"
hardConstKeyword = "hard_constraints"
bothKeyword = "both"
mofnKeyword = "mofn"
searchKeyword = "searchBoth"
weightKeyword = "weight"
countKeyword = "counts"
granOptions = ["ban", "exp", "mul"]
minKeyword = "granular"
unSat = "unsat"
isSet = "isSet"

SS512 = { 'ZR':512, 'G1': 512, 'G2': 512, 'GT': 1024 }
SS1024 = { 'ZR':1024, 'G1': 1024, 'G2': 1024, 'GT': 2048 } # TODO: need to verify this
MNT160 = { 'ZR':160, 'G1': 160, 'G2': 960, 'GT': 960 }
BN256 = { 'ZR':256, 'G1': 256, 'G2': 1024, 'GT': 3072 }

symmetric_curves = {'SS512':SS512, 'SS1024':SS1024}
asymmetric_curves = { 'MNT160':MNT160, 'BN256':BN256 }

def getConstraintSAT(vars, mofn, mCount, verbose=False):
    if verbose: print("mCount :", mCount)
    if mCount == 1:
        return Or([ vars.get(i) for i in mofn ])
    else:
        s = ""
        for i in mofn:
            s += str(i)
        # compute all combination of the variables in s
        # each case ==> AND(case1) OR AND(case2) OR AND(case3) OR ...etc...
        cases = list(combinations(s, mCount))
        orObjects = []
        for c in cases:
            orObjects.append(And([ vars.get(i) for i in c ]))
        return Or(orObjects)

def searchSAT(vars, solver, mofn, m, verbose=False):
    if verbose: print("solver before search: ", solver)
    mCount = m
    mofnCon = [ vars.get(i) for i in mofn ]
    while mCount != 0:
        if mCount == len(mofn): # first time call, so no pop
            print(mofn)
            solver.add(And(mofnCon))
        else:
            solver.pop()
            solver.add(getConstraintSAT(vars, mofn, mCount))
            # add (m-1)-of-n to solver and re-check
        #print("solver after update: ", solver)
        #print(solver.check())
        if solver.check() == unsat: mCount -= 1
        else: break # solution was satisfiable, search is complete
    return mCount

def searchBothSAT(vars, solver, key1name, key1, key2name, key2, origConstraints, verbose=False):
    if verbose: print("solver before search: ", solver)
    satisfiable = False

    if len(origConstraints) > 0:    
        solver.add(origConstraints)

    count1 = len(key1)-1
    count2 = len(key2)-1
    solver2 = None
    fixCount1 = False
    fixCount2 = False    
    while not satisfiable:
        solver2 = Solver()
        solver2.add(solver.assertions()) # revert back to solver
        solver2.add(getConstraintSAT(vars, key1, count1), getConstraintSAT(vars, key2, count2))
        #print("solver after update: ", solver2)
        if verbose: print("check: ", solver2.check())
        if solver2.check() == unsat: 
            if not fixCount1: count1 -= 1
            if not fixCount2: count2 -= 1
        else:
            satisfiable = True
            continue
        if count1 == 0 or count2 == 0: 
            # switch strategy... how?
            print("%s: %d of %d" % (key1name, count1, len(key1)))
            print("%s: %d of %d" % (key2name, count2, len(key2)))
            print("Could not find the largest m-of-n for either category.")
            # JAA: this didn't work for this scheme. perhaps, we may need to utilize the option to favor one set over the other?
            return solver

    if verbose:    
        print("final solution: ", solver2)
        print("satisfiable: ", solver2.check())
    print("%s: %d of %d" % (key1name, count1, len(key1)))
    print("%s: %d of %d" % (key2name, count2, len(key2)))
    return solver2


def solveUsingSAT(optionDict): # variables, clauses, constraints):
    verbose     = optionDict.get(verboseKeyword)
    variables   = optionDict.get(variableKeyword)
    clauses     = optionDict.get(clauseKeyword)
    constraints = optionDict.get(constraintKeyword)
    mofn        = optionDict.get(mofnKeyword)
    vars = {}
    for v in variables:
        vars[ str(v) ] = Bool(str(v)) # create Bool refs
    
    mySolver = Solver()
    for i in clauses:
        (x, y) = i
        if vars.get(x) and vars.get(y):
            mySolver.add(Xor(vars.get(x), vars.get(y)))
            mySolver.push()
        elif vars.get(x) == None:
            print("Need to add '%s' to variable list." % x)
            return
        elif vars.get(y) == None:
            print("Need to add '%s' to variable list." % y)
            return
        
    # if searchKeyword disabled
    if not optionDict.get(searchKeyword):
        andObjects = []
        for i in constraints:
            # default case where each i is a string variable
            if vars.get(i) != None:
                andObjects.append(vars.get(i))
                    
        if len(andObjects) > 0:
            mySolver.add(And(andObjects))
            mySolver.push()
        
        # flex constraints: extract the m-of-n variables
        # then perform search to determine largest m out of n that 
        m = len(mofn)
        if m > 0:
            countOutofN = search(vars, mySolver, mofn, m) # returns a number that says how far it got
            print("list: ", mofn)
            print("Result: %d of %d" % (countOutofN, m))
            print("Result constraints: ", mySolver)
    else:
        print("search for both...")
        count = 0
        constraintLists = {}
        _origConstraints = []
        for i in constraints:
            if optionDict.get(i):
                constraintLists[ count ] = (i, optionDict.get(i)); count += 1
                print(i, ":", optionDict.get(i))
            elif vars.get(i) != None: # ground truth that we can't change
                _origConstraints.append(i)
       
        print("constraintLists = ", constraintLists, len(constraintLists)) 
        assert len(constraintLists) == 2, "With this option, can only have (keys and (ciphertext or signatures))"
        key1 = list(set(constraintLists[0][1]).difference(_origConstraints))
        key1name = str(constraintLists[0][0])
        key2 = list(set(constraintLists[1][1]).difference(_origConstraints))
        key2name = str(constraintLists[1][0])

        origConstraints = [ vars.get(i) for i in _origConstraints ]
        
        mySolver = searchBothSAT(vars, mySolver, key1name, key1, key2name, key2, origConstraints, verbose=True)
    
    isSat = mySolver.check()
    if str(isSat) == unSat:
        sys.exit("Clauses are not satisfiable.") 
    else:
        pass

    model = mySolver.model()
    results = {}
    for index in range(len(variables)):
        key = model[index]
        print(key, ':', model[key])
        results[ str(key) ] = model[key]

    return (results, isSat)

def buildZ3Expression(node, varMap):
    if node == None: return None
    if node.left != None: leftNode   = buildZ3Expression(node.left, varMap)
    if node.right != None: rightNode = buildZ3Expression(node.right, varMap)
    
    # visit the root
    if Type(node) == ops.EQ_TST:
        return (leftNode == rightNode)
    elif Type(node) == ops.AND:
        return And(leftNode, rightNode)
    elif Type(node) == ops.ADD:
        return leftNode + rightNode
    elif Type(node) == ops.SUB:
        return leftNode - rightNode
    elif Type(node) == ops.MUL:
        return leftNode * rightNode
    elif Type(node) == ops.DIV:
        return leftNode / rightNode
    elif Type(node) == ops.ATTR:
        varName = str(node).split(LIST_INDEX_SYMBOL)[0] # in case it has a '#' symbol 
        if varName == "-1": return -1
        if "-" in varName: negated = True
        else: negated = False
        
        if not varName.isdigit():
            if negated: 
                varName = varName.strip("-")
                assert varName in varMap.keys(), "missing var reference: " + varName
                return -1 * varMap.get(varName)
            return varMap.get(varName)
        else:
            return int(varName)
    else:
        print("NodeType unsupported: ", Type(node))
        return None

def get_models(Formula):
    result = []
    s = Solver()
    s.add(Formula)
    while True:
        if s.check() == sat:
            m = s.model()
            result.append(m)
            # Create a new constraint the blocks the current model
            block = []
            for d in m:
                # d is a declaration
                if d.arity() > 0:
                    raise Z3Exception("uninterpreted functions are not suppported")
                # create a constant from declaration
                c = d()
                if is_array(c) or c.sort().kind() == Z3_UNINTERPRETED_SORT:
                    raise Z3Exception("arrays and uninterpreted sorts are not supported")
                block.append(c != m[d])
            s.add(Or(block))
        else:
            return result

## Given formula F, find the model the minimizes the value of X 
## using at-most M iterations.
#def minimize(solver, Formula, M):
#    s = Solver()
#    s.add(solver.assertions())
#    last_model  = None
#    i = 0
#    while True:
#        r = s.check()
#        if r == unsat:
#            if last_model != None:
#                return last_model
#            else:
#                return unsat
#        if r == unknown:
#            raise Z3Exception("failed")
#        last_model = s.model()
#        X = last_model.evaluate(Formula)
#        s.add(X < last_model[X])
#        i = i + 1
#        if (i > M):
#            raise Z3Exception("maximum not found, maximum number of iterations was reached")


class ModelEval:
    def __init__(self, variables, Z3vars, countValue):
        self.variables = variables
        self.Z3vars = Z3vars
        self.countValue = countValue
        self.verbose = False
    
    def minimizeWeightFunc(self, M, weights, counts, cache=None):
        w0 = self.Z3vars['w0'] = IntVal(weights['G1'])
        w1 = self.Z3vars['w1'] = IntVal(weights['G2'])
        formula = ""
        ADD = " + "
        for i in self.variables:
            V = self.Z3vars.get(i)
            C = self.countValue.get(i)
            formula +=  "(" + str((((1 - V)*w0 + V*w1))*C ) + ")" + ADD
        formula = formula[:-len(ADD)]
        
        parser = sdl.SDLParser()
        formulaNode = parser.parse(formula)
        weightFunc = buildZ3Expression(formulaNode, self.Z3vars) 
        print("Objective Function: ",  str(weightFunc).replace("\n", " ").replace("\t", ""))
                
        newMinValue = int(M[0].evaluate(weightFunc).as_string())
        newMinIndex = 0
        if self.verbose: print("Weight Func value: ", newMinValue, M[0])
        if cache != None: cache[ newMinIndex ] = newMinValue
        for i in range(1, len(M)):
            minValue = int(M[i].evaluate(weightFunc).as_string())
            if cache != None: cache[ i ] = minValue
            if minValue < newMinValue:
                newMinValue = minValue
                newMinIndex = i
            if self.verbose: print("Weight Func value: ", minValue, str(M[i]).replace("\n", " ").replace("\t", ""))
    
        return (M[newMinIndex], newMinValue) 
    
    def evalWeightFunc(self, solver, weights, counts):
        # for extracting other models
        #solver2 = Solver()
        #solver2.add(solver.assertions()) # revert back to solver
        w0 = self.Z3vars['w0'] = Int('w0')
        w1 = self.Z3vars['w1'] = Int('w1')
        formula = ""
        ADD = " + "
        for i in self.variables:
            V = self.Z3vars.get(i)
            C = counts.get(i)
            formula +=  "(" + str((((1 - V)*w0 + V*w1))*C ) + ")" + ADD
        formula = formula[:-len(ADD)]
        
        parser = sdl.SDLParser()
        formulaNode = parser.parse(formula)
        weightFunc = buildZ3Expression(formulaNode, self.Z3vars) 
        print("Objective Function: ",  weightFunc)
        
        solver.add(  )
        
        theModel = solver.model() # assume initial solution is satisfiable
        print("Weight Func value: ", theModel.evaluate(weightFunc))
    
        return None

def convertToBoolean(mod):
    result = []
    for i in range(len(list(mod))):
        k = mod[i]
        intVal = int(mod[k].as_string())
        boolVal = False
        if intVal == 0: boolVal = True
        print(k, ":=", boolVal)
        result.append( (str(k), boolVal ) )
    print("\n")
    return result

#def minimizeBothMode(Z3vars, mySolver, constraints, optionDict):
#    print("search for both...")
#    count = 0
#    constraintLists = {}
#    _origConstraints = []
#    for i in constraints:
#        if optionDict.get(i):
#            constraintLists[ count ] = (i, optionDict.get(i)); count += 1
#            print(i, ":", optionDict.get(i))
#        elif Z3vars.get(i) != None: # ground truth that we can't change
#            _origConstraints.append(i)
#   
#    print("constraintLists = ", constraintLists, len(constraintLists)) 
#    assert len(constraintLists) == 2, "With this option, can only have (keys and (ciphertext or signatures))"
#    key1 = list(set(constraintLists[0][1]).difference(_origConstraints))
#    key1name = str(constraintLists[0][0])
#    key2 = list(set(constraintLists[1][1]).difference(_origConstraints))
#    key2name = str(constraintLists[1][0])
#
#    origConstraints = [ vars.get(i) for i in _origConstraints ]
#    
#    mySolver = searchBothSMT(Z3vars, mySolver, key1name, key1, key2name, key2, origConstraints, verbose=True)
#    print("new Solver: ")


def convertQuery(optionDict, variables, constraints):
    """check optionDict for what user wants and create corresponding weights and counts for objective function"""
    minOps         = optionDict.get(minKeyword)
    countOpts      = optionDict.get(countKeyword) # count of certain operations e.g., exp => a0:4, b0:3, etc
    
    
    # weights can either be group sizes OR time for whatever op: (exp or mul)
    weights = { 'G1': MNT160['G1'], 'G2':MNT160['G2'] } # bandwidth
    #weights = { 'G1': 1, 'G2':2 } # bandwidth 
    
    countValue = {}
    print("constraints: ", constraints)
    for v in variables:
        if v in constraints:
            # specified when dealing w/ "exp" and "mul" type queries
            if v in countOpts.keys(): countValue[ v ] = int(countOpts[v])
            else: countValue[ v ] = 1
        else:
            countValue[ v ] = 0
    
    return (weights, countValue)
    
def findMinimalRef(M, data1, data2):
    # compute differences
    skipList = []
    data3 = {}
    for j in range(len(data1.keys())):
        diff = abs(data1[j] - data2[j])
        data3[j] = diff
    
    minVal = prevVal = data3[0]
    minRef = prevRef = 0
    for i in data3.keys():
        if data3[i] <= minVal:
            prefVal = minVal; prevRef = minRef
            minVal = data3[i]
            minRef = i
    print("min: ", data1[minRef], data2[minRef], M[minRef])
    return M[minRef]
        
def solveUsingSMT(optionDict):
    verbose     = optionDict.get(verboseKeyword)
    variables   = optionDict.get(variableKeyword)
    clauses     = optionDict.get(clauseKeyword)
    constraints = optionDict.get(constraintKeyword)
    mofn        = optionDict.get(mofnKeyword)
    bothConst   = optionDict.get(bothKeyword)
    
    searchAll   = optionDict.get(searchKeyword)    
    hard_constraints = optionDict.get(hardConstKeyword)
    print("hardConstraints: ", hard_constraints)
    # granular configuration options
    # weights     = optionDict.get(weightKeyword) # cost of operations in each group. bandwitdh => G1:100, G2:300
#    countOpts      = optionDict.get(countKeyword) # count of certain operations e.g., exp => a:4, b:3, etc
    counts  = {}
    Z3vars = {}
    for v in variables:
        Z3vars[ str(v) ]   = Int(str(v)) # create Int refs
        countVar           = "c_" + str(v)
        counts[ str(v) ]   = Int(countVar)
        Z3vars[ countVar ] = counts[str(v)]


    mySolver = Solver()
    Conditions = []
    Values = []
    for i in clauses:
        (x, y) = i
        if Z3vars.get(x) and Z3vars.get(y):
            X = Z3vars.get(x)
            Y = Z3vars.get(y)
            Conditions.append( X != Y )
            if not searchAll:
                if x in constraints:
                    Values.append( X == 0 )
                else:
                    Values.extend( [Or(X == 0, X == 1)] )
                if y in constraints:
                    Values.append( Y == 0 )
                else:
                    Values.extend( [Or(Y == 0, Y == 1)] )
            else:
                if x in hard_constraints:
                    Values.append( X == 0 )
                else:
                    Values.extend( [Or(X == 0, X == 1)] )
                if y in hard_constraints:
                    Values.append( Y == 0 )
                else:
                    Values.extend( [Or(Y == 0, Y == 1)] )
            
    M = get_models([And(Conditions), And(Values)])
    print("Unique solutions: ", len(M))
    
    # if only minimizing one aspect: SK or CT, PK or SIG
    if not bothConst[isSet]:
        weights, countValue = convertQuery(optionDict, variables, constraints)
    
        modEval             = ModelEval(variables, Z3vars, countValue)
        cacheOpts = {}
        (modRef, modVal)    = modEval.minimizeWeightFunc(M, weights, counts, cacheOpts)
        print("Results: ", cacheOpts)
        
        print("minimal Value: ", modVal) 
        #print("minimal Model: ", modRef)
    else:
        # more than one option 
        minKeys = list(set(list(bothConst.keys())).difference([isSet]))
        data = {}
        for i in minKeys: 
            print("Compute min value for: ", i)
            print("<================================================>")
            weights, countValue = convertQuery(optionDict, variables, bothConst[i])
        
            modEval             = ModelEval(variables, Z3vars, countValue)
            cacheOpts = {}
            (modRef, modVal)    = modEval.minimizeWeightFunc(M, weights, counts, cacheOpts)
            print("Cached: ", cacheOpts)
            data[i] = cacheOpts
            print("minimal Value: ", modVal) 
            #print("minimal Model: ", modRef)
            print("<================================================>")
        
        # operate on the solution
        i = minKeys[0]
        j = minKeys[1]
        modRef = findMinimalRef(M, data[i], data[j])
#        print("Operate on: ", )
#        sys.exit(0)
    return (convertToBoolean(modRef), sat)
    
#    sys.exit(0)
#    print("SMT input: ", str(mySolver).replace("\n", " ").replace("\t", ""))
#    
#    isSat = mySolver.check()
#    if isSat == unsat:
#        print("Failed!")
#    else:
#        mod = mySolver.model()
##        modEval = ModelEval(variables, Z3vars, countValue)
##        mod2 = modEval.evalWeightFunc(M, weights, counts)
#        print("Model:\t")
#        for i in range(len(list(variables))):
#            k = mod[i]
#            print(k, ":=", mod[k], end=" : ")
#        print("\n")
#    return (None, None)
