from z3 import *
from itertools import combinations
import src.sdlpath, math
from src.benchmark_interface import *
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
SHORT_ASSUMPTION = "assumption"
SHORT_SECKEYS = "secret-keys" # for minimizing secret-key representation
SHORT_PUBKEYS = "public-keys" # for minimizing public-key representation
SHORT_CIPHERTEXT = "ciphertext" # in case, an encryption scheme
SHORT_SIGNATURE  = "signature" # in case, a sig algorithm
SHORT_FORALL = "both"
SHORT_OPTIONS = [SHORT_SECKEYS, SHORT_PUBKEYS, SHORT_CIPHERTEXT, SHORT_SIGNATURE, SHORT_FORALL]
assumpKeyword = "assump_map"
assumpListKeyword = "assump_list"
schemeTypeKeyword = "scheme"
verboseKeyword = "verbose"
variableKeyword = "variables"
clauseKeyword = "clauses"
constraintKeyword = "constraints"
hardConstKeyword = "hard_constraints"
bothKeyword = "both"
dropFirstKeyword = "dropFirst"
pkMapKeyword = "pk_map"
pkListKeyword = "pk_list"
mofnKeyword = "mofn"
searchKeyword = "searchBoth"
weightKeyword = "weight"
countKeyword = "counts"
sizeOp = "size"
expOp = "exp"
mulOp = "mul"
minKeyword = "operationTime"
curveKeyword = "findCurve"
dropKeyword  = "dropFirst"
unSat = "unsat"
isSet = "isSet"
pkEncType = "PKENC" # encryption
pkSigType = "PKSIG" # signatures


SS512 = { 'ZR':512, 'G1': 512, 'G2': 512, 'GT': 1024 }
MNT160 = { 'ZR':160, 'G1': 160, 'G2': 960, 'GT': 960 }
SS1536 = { 'ZR':1536, 'G1': 1536, 'G2': 1536, 'GT': 3072 }
BN256 = { 'ZR':256, 'G1': 256, 'G2': 1024, 'GT': 3072 }

symmetric_curves = {'SS512':SS512, 'SS1536':SS1536}
asymmetric_curves = { 'MNT160':MNT160, 'BN256':BN256 } # TODO: add additional curves 

def estimateSize(theVarTypes, curveDict):
    sum = 0
    #print("estimateSize input => ", list(theVarTypes.keys()))
    for i in theVarTypes.keys():
        _type = str(theVarTypes[i])
        if _type in ['ZR', 'G1', 'G2', 'GT']:
            #print("Adding ", _type, " = ", curveDict[_type])
            sum += curveDict[_type]
    return sum
    

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

def initDict(someList):
    d = {}
    print("theList: ", someList)
    for i in someList:
        d[i] = set()
    return d

def sumDict(d):
    assert type(d) == dict, "Expected d to be a dictionary!"
    c = 0
    for i,j in d.items():
        c += sum(list(j), 0)
    return c


class ModelEval:
    def __init__(self, indexList, variables, Z3vars, countValue):
        self.indexList = indexList
        self.variables = variables
        self.Z3vars = Z3vars
        self.countValue = countValue
        self.verbose = None

    def enableVerboseMode(self):
        self.verbose = True

    def disableVerboseMode(self):
        self.verbose = None

    def __sumTheSets(self, d):
        c = 0
        for i,j in d.items():
            c += sum(list(j), 0)
        return c

    def __countSplits(self, d):
        s = 0
        for i,j in d.items():
            if len(j) > 1: # meaning we have a split
                s += 1 # increment split count
        return s

    def evaluateSolutionsFromDepMap(self, M, depMap, depList, optionDict, rankSolutions=None):
        first = self.indexList[0]
        G1, G2 = 0, 1
        specificOp = optionDict.get(minKeyword)
        curve      = asymmetric_curves.get(specificOp)
        assert curve != None, "Specified an invalid type-III curve: " + curve
        pts = {G1: curve.get('G1'), G2: curve.get('G2')}
        #pts = {G1:1, G2:2} # simple point system (replace with

        resultMap = {}
        countMap = {} # stores intermediate results
        print("evaluateSolutionsFromDepMap: ", depList)
        for solIndex in self.indexList:
            counts = initDict(depList)
            if self.verbose:
                print(solIndex, "=> Solution:", M[solIndex])
            for v in M[solIndex]:
                assign = int(str(M[solIndex][v]))
                key = str(v)
                #print(v, ":", assign, depMap.get(key))
                if depMap.get(key):
                    for j in depMap.get(key):
                        counts[j] = counts[j].union({pts[assign]})
            split_value = self.__countSplits(counts)
            if split_value > 0:
                resultMap[solIndex] = (split_value, self.__sumTheSets(counts))
                countMap[solIndex] = dict(counts)
            if self.verbose:
                print("Result: ", counts, ", splits:", resultMap[solIndex][0], ", sum:", resultMap[solIndex][1], "\n")
        #print("Final: ", resultMap)
        # find the minimum by comparing the second element of each tuple
        #if rankSolutions:
        #    sols = sorted(resultMap.items())
        #    print("Solutions: ", sols)
        #    sys.exit(-1)

        optimal_split = min(resultMap.items(), key=lambda x: x[1])
        index = optimal_split[0]
        print("Min splits: ", optimal_split[1][0])
        print("The sum: ", optimal_split[1][1])
        print("Found Solution: ", M[index])
        print("Results: ", countMap[index])
        return M[index], countMap[index]



    def minimizeWeightFunc(self, M, weights, counts, cache=None):
        w0 = self.Z3vars['w0'] = weights['G1'] # IntVal(weights['G1'])
        w1 = self.Z3vars['w1'] = weights['G2'] # IntVal(weights['G2'])
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
        # JAA: commented out for benchmarking        
        if self.verbose: print("Objective Function: ",  str(weightFunc).replace("\n", " ").replace("\t", ""))
    
# TODO: make this an option where we don't set weights and figure out which curve satisfies a condition
#        for i in range(len(M)):
#            print(i, "=>", end="")
#            solve(M[i].evaluate(weightFunc) < 512, And(w0 == 160, w1 == 960))
#            print("")
#
#        sys.exit(0)
        
        first = self.indexList[0]
        newMinValue = int(M[first].evaluate(weightFunc).as_string())
        newMinIndex = first
        if self.verbose: print("Weight Func value: ", newMinValue, M[0])
        if cache != None: cache[ newMinIndex ] = newMinValue
        for i in self.indexList[1:]: # range(1, len(M))
            minValue = int(M[i].evaluate(weightFunc).as_string())
            if cache != None: cache[ i ] = minValue
            if minValue < newMinValue:
                newMinValue = minValue
                newMinIndex = i
            if self.verbose: print("Weight Func value: ", minValue, str(M[i]).replace("\n", " ").replace("\t", ""))
    
        return (M[newMinIndex], newMinValue) 
    
#    def evalWeightFunc(self, solver, weights, counts):
#        # for extracting other models
#        #solver2 = Solver()
#        #solver2.add(solver.assertions()) # revert back to solver
#        w0 = self.Z3vars['w0'] = Int('w0')
#        w1 = self.Z3vars['w1'] = Int('w1')
#        formula = ""
#        ADD = " + "
#        for i in self.variables:
#            V = self.Z3vars.get(i)
#            C = counts.get(i)
#            formula +=  "(" + str((((1 - V)*w0 + V*w1))*C ) + ")" + ADD
#        formula = formula[:-len(ADD)]
#        
#        parser = sdl.SDLParser()
#        formulaNode = parser.parse(formula)
#        weightFunc = buildZ3Expression(formulaNode, self.Z3vars) 
#        print("Objective Function: ",  weightFunc)
#        
#        solver.add(  )
#        
#        theModel = solver.model() # assume initial solution is satisfiable
#        print("Weight Func value: ", theModel.evaluate(weightFunc))
#    
#        return None

def convertToBoolean(mod):
    result = []
    for i in range(len(list(mod))):
        k = mod[i]
        intVal = int(mod[k].as_string())
        boolVal = False
        if intVal == 0: boolVal = True
        # JAA: commented out for benchmarking        
        #print(k, ":=", boolVal)
        result.append( (str(k), boolVal ) )
    #print("\n")
    return result

def getWeights(option, specificOp):
    if option in SHORT_OPTIONS:
        # specificOp could be the curve
        curve = asymmetric_curves.get(specificOp)
        assert curve != None, "specified invalid curve identifier: " + specificOp
        return {'G1': IntVal(curve.get('G1')), 'G2': IntVal(curve.get('G2'))}
    elif option == expOp or option == mulOp:
        (curve, paramid) = getBenchmarkInfo() # miracl by default
        assert curve != None, "error occurred with " + paramid + " benchmark info."
        assert paramid.upper() == specificOp.upper(), "need to create benchmark dictionary for " + paramid
        return {'G1':IntVal(math.ceil(curve[paramid][option]['G1'])), 'G2':IntVal(math.ceil(curve[paramid][option]['G2'])) }

def convertQuery(configOpt, optionDict, variables, constraints):
    """check optionDict for what user wants and create corresponding weights and counts for objective function"""
    specificOp           = optionDict.get(minKeyword)
    if configOpt in SHORT_OPTIONS:
        countOpts        = {}
    else:
        countOpts        = optionDict.get(countKeyword) # count of certain operations e.g., exp => a0:4, b0:3, etc
    findCurve            = optionDict.get(curveKeyword)
    
    # weights can either be group sizes OR time for whatever op: (exp or mul)
    print("<====================>")
    if findCurve:
        weights = { 'G1': Int('w0'), 'G2':Int('w1') } # if we want to figure out appropriate weights
    else: # specify specific one
        weights = getWeights(configOpt, specificOp)
    # JAA: commented out for benchmarking        
    #print("selected weights: ", weights)
    #print("count values: ", countOpts)
    #print("constraints: ", constraints)
    countValue = {}
    for v in variables:
        if v in constraints:
            # specified when dealing w/ "exp" and "mul" type queries
            if v in countOpts.keys(): countValue[ v ] = int(countOpts[v])
            else: countValue[ v ] = 1
        else:
            if v in countOpts.keys(): countValue[ v ] = int(countOpts[v])
            else: countValue[ v ] = 0
    print("<====================>")    
    print("selected weights: ", weights)
    print("selected costs: ", countValue)
    print("<====================>")    
    return (weights, countValue)
    
def findMinimalRef(M, data1, data2, skipList=[]):
    # compute differences
    data3 = {}
    data3Count = {}
    data3Index = {}
    first = None
    for j in range(len(data1.keys())):
        if j not in skipList:
            diff = abs(data1[j] - data2[j])
            data3[j] = diff
            # count up solutions
            if data3Count.get(diff) == None: 
                data3Count[diff] = 1
                data3Index[diff] = [j]
            else: 
                data3Count[diff] += 1
                data3Index[diff].append(j)
            if first == None: first = j

    minVal = data3[first]
    minRef = first
    for i in data3.keys():
        if data3[i] <= minVal:
            minVal = data3[i]
            minRef = i
            minCount = data3Count[minVal]
            minRefList = data3Index[minVal]
    #print("min: ", data1[minRef], data2[minRef], str(M[minRef]).replace("\n", "").replace("\t", ""))
    return minRef, minCount, minRefList # M[minRef]
        
def solveUsingSMT(optionDict, shortOpt, timeOpt):
    verbose     = optionDict.get(verboseKeyword)
    schemeType  = optionDict.get(schemeTypeKeyword)
    print("Scheme type: ", schemeType)
    variables   = optionDict.get(variableKeyword)
    clauses     = optionDict.get(clauseKeyword)
    constraints = optionDict.get(constraintKeyword)
    bothConst   = optionDict.get(bothKeyword)
    
    searchAll   = optionDict.get(searchKeyword)    
    hard_constraints = optionDict.get(hardConstKeyword)
    pk_map_vars = optionDict.get(pkMapKeyword)
    pk_list     = optionDict.get(pkListKeyword)
    assump_map_vars = optionDict.get(assumpKeyword)
    assump_list = optionDict.get(assumpListKeyword)

    # JAA: commented out for benchmarking    
    #print("hardConstraints: ", hard_constraints)
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
            if x in hard_constraints:
                Values.append( X == 0 )
            else:
                Values.extend( [Or(X == 0, X == 1)] )
            if y in hard_constraints:
                Values.append( Y == 0 )
            else:
                Values.extend( [Or(Y == 0, Y == 1)] )
            
    M = get_models([And(Conditions), And(Values)])
    if(len(M) == 0):
        print("Failed to find a satisfiable solution given constraints. Try again with different or relaxed constraints.")
        return unsat
    print("Unique solutions: ", len(M))

    # minimize the assumption, if the option is selected
    if shortOpt == SHORT_ASSUMPTION: # and schemeType == pkEncType:
        print("Using Solver to minimize the size of the assumption...")
        modEval = ModelEval(range(len(M)), variables, Z3vars, None)
        if verbose: modEval.enableVerboseMode()
        (modRef, countMap) = modEval.evaluateSolutionsFromDepMap(M, assump_map_vars, assump_list, optionDict)
        return (convertToBoolean(modRef), sat)

    if shortOpt == SHORT_PUBKEYS: #and schemeType == pkEncType:
        print("Using Solver to minimize the PK constraints...")
        modEval = ModelEval(range(len(M)), variables, Z3vars, None)
        (modRef, countMap) = modEval.evaluateSolutionsFromDepMap(M, pk_map_vars, pk_list, optionDict, rankSolutions=True)
        return (convertToBoolean(modRef), sat)


    # if only minimizing one aspect: size: SK or CT, PK or SIG OR time: exp or mul
    if not bothConst[isSet]:
        if shortOpt != "": # minimize SK or CT OR PK or SIG
            weights, countValue = convertQuery(shortOpt, optionDict, variables, constraints)
        elif timeOpt != "": # minimize exp or mul
            weights, countValue = convertQuery(timeOpt, optionDict, variables, constraints)
    
        modEval             = ModelEval(range(len(M)), variables, Z3vars, countValue)
        cacheOpts = {}
        (modRef, modVal)    = modEval.minimizeWeightFunc(M, weights, counts, cacheOpts)
        #print("Results: ", cacheOpts)
        
        #print("minimal Value: ", modVal) 
        #print("minimal Model: ", modRef)
    elif bothConst[isSet]: # and len(optionDict.get(countKeyword).keys()) == 0: # in other words, just size (but SK and CT or PK and SIG), but NOT time
        # more than one option 
        minKeys = list(set(list(bothConst.keys())).difference([isSet]))
        data = {}
        for i in minKeys: 
            if verbose: 
                print("Compute min value for: ", i)
                print("<================================================>")
            weights, countValue = convertQuery(shortOpt, optionDict, variables, bothConst[i])
        
            modEval             = ModelEval(range(len(M)), variables, Z3vars, countValue)
            cacheOpts = {}
            (modRef, modVal)    = modEval.minimizeWeightFunc(M, weights, counts, cacheOpts)
            data[i] = cacheOpts
            if verbose:
                print("Cached: ", cacheOpts)
                print("minimal Value: ", modVal) 
                print("minimal Model: ", modRef)
                print("<================================================>")
        
        # operate on the solution
        i = minKeys[0]
        j = minKeys[1]
#        topSolCount = 1 + math.floor(len(M) * 0.1)
#        topList = []
#        for k in range(topSolCount):
#            topList.append(minIndex)
        minIndex, minCount, minIndexList = findMinimalRef(M, data[i], data[j])
        #print("Final Solution: ", minIndex)
        #print("Found ", minCount, " such solutions that minimize both.")
        #print("Index List: ", minIndexList)
        modRef = M[minIndex]
        
        if minCount > 1 and timeOpt != "": # short => both & time option = mul or exp
            #print("<================================================>")
            weights, countValue = convertQuery(timeOpt, optionDict, variables, hard_constraints)
            #print("Time option: ", weights)
            #print("Cost count: ", countValue)
            modEval             = ModelEval(minIndexList, variables, Z3vars, countValue)
            cacheOpts = {}
            (modRef, modVal)    = modEval.minimizeWeightFunc(M, weights, counts, cacheOpts)
            #print("Cached: ", cacheOpts)
            data[i] = cacheOpts
            #print("minimal Value: ", modVal)
            #print("minimal model: ", modRef)
        elif minCount > 1 and optionDict['dropFirst'] != None:
            dropFirst = optionDict['dropFirst']
            if verbose:
                print("More than 1 solution left && short = both && time = None. dropFirst = ", dropFirst)
                print("minIndex: ", minIndex)
                print("minCount: ", minCount, minIndexList)
            weights, countValue = convertQuery(shortOpt, optionDict, variables, bothConst[dropFirst])
            modEval             = ModelEval(minIndexList, variables, Z3vars, countValue)
            cacheOpts = {}
            (modRef, modVal)    = modEval.minimizeWeightFunc(M, weights, counts, cacheOpts)
            if verbose:
                print("minimal Value: ", modVal)
                print("minimal model: ", modRef)
        else:
            # return original solution if no dropFirst option was selected
            pass
    else:
        pass
    
    return (convertToBoolean(modRef), sat)
