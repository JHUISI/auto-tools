from z3 import *
from itertools import combinations
import src.sdlpath, math
from src.benchmark_interface import *
import sdlparser.SDLParser as sdl
from sdlparser.SDLang import *
from src.outsrctechniques import HasPairings

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
pairingVarMapKeyword = "pairingVarMap"
mergedGraphKeyword = "mergedGraph"
isAutoGroupKeyword = "oldAutoGroup"

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
    #print("theList: ", someList)
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
        G1, G2, Both = 0, 1, 2
        varMap = optionDict.get(pairingVarMapKeyword)
        specificOp = optionDict.get(minKeyword)
        curve      = asymmetric_curves.get(specificOp)
        assert curve != None, "Specified an invalid type-III curve: " + specificOp
        pts = {G1: curve.get('G1'), G2: curve.get('G2'), Both: set([curve.get('G1'), curve.get('G2')])}
        #pts = {G1:1, G2:2} # simple point system (replace with
        # TODO: move this to another
        for i,j in varMap.items():
            #print(i, "=>", j)
            if i in depList:
                depMap[j] = depMap[j].union([i])
                #print("append this to ", depMap.get(j))

        resultMap = {}
        countMap = {}  # stores intermediate results
        print("<====================================>")
        print("VarMap: ", varMap)
        print("DepMap: ", depMap)
        print("evaluateSolutionsFromDepMap: ", depList)
        print("<====================================>")
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
            #print("split value: ", split_value)
            if split_value >= 0:
                resultMap[solIndex] = (split_value, self.__sumTheSets(counts))
                countMap[solIndex] = dict(counts)
            if self.verbose:
                print("Result: ", counts, ", splits:", resultMap[solIndex][0], ", sum:", resultMap[solIndex][1], "\n")
        print("Final: ", resultMap)
        # find the minimum by comparing the second element of each tuple
        #if rankSolutions:
        #    sols = sorted(resultMap.items())
        #    print("Solutions: ", sols)
        #    sys.exit(-1)

        optimal_split = min(resultMap.items(), key=lambda x: x[1])
        index = optimal_split[0]
        if self.verbose:
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

"""
Convert group assignments of (0, 1, and 2) into
strings. 0 = 'G1', 1 = 'G2' and 2 = 'Both'
"""
def convertToGroup(mod):
    result = []
    for i in range(len(list(mod))):
        k = mod[i]
        intVal = int(mod[k].as_string())
        StringVal = ""
        if intVal == 0: StringVal = "G1"
        elif intVal == 1: StringVal = "G2"
        elif intVal == 2: StringVal = "both"
        else:
            print("convertToGroup: did not get an assignment for variable='%s'" % str(k))
        # JAA: commented out for benchmarking
        #print(k, ":=", boolVal)
        result.append((str(k), StringVal))
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

def checkValidSplit(info, optionDict, a_model):
    xorMap       = optionDict.get(pairingVarMapKeyword)
    merged_graph = optionDict.get(mergedGraphKeyword)
    if merged_graph is None:
        sys.exit("Merged Graph not set.\nAdd 'graphit = True' to your scheme config.")
    # using group_info map, extract a graph split (basically, apply BFS from root)
    # also check whether the split is valid
    if info.get('single_reduction'):
        # build a complete dep map of scheme, reduction and assumption from the model
        group_info = buildCompleteMap(a_model, info, xorMap)
        # generate a split given the group info
        (graph0, graph1, is_valid_split) = generateSplit(info, group_info, merged_graph)
        if is_valid_split:
            print("SOLUTION IS A VALID SPLIT!!!")
        else:
            print("REJECTING SPLIT!!!")
            sys.exit(-1)
    else:
        # get reduction data
        reductionData = info.get('reductionData')
        assumptionData = info.get('assumptionData')
        for (index, graph) in merged_graph.items():
            #print("<===========================>")
            (reducname, assumpname) = info['merged_graph_map'][index]
            reducDeps = reductionData.get(reducname)['deps'][1]
            #reducDeps = info.get('merged_deps')
            assumpVarMap = assumptionData.get(assumpname)['varmap']
            assumpKey = assumptionData.get(assumpname)['prunedMap']
            #print(info.get('merged_deps'))

            group_info = GenerateSplitSolutionMap(a_model, xorMap, info, reducDeps)

            # print("BEFORE ==>")
            # print("Both G1 & G2: ", group_info[_bothPrefix])
            # print("Just G1: ", group_info[_G1Prefix])
            # print("Just G2: ", group_info[_G2Prefix])
            # print("<===========================>")

            for var in assumpKey.keys():
                new_key = processVarWithDep(group_info, var, info.get('merged_deps'), assumpVarMap)
                if new_key == _bothPrefix: # only conservative case
                    dep_vars_list = assumpKey.get(var)
                    for var_dep in dep_vars_list:
                        addToInfo(new_key, var_dep, group_info)
                        other_groups = set([_bothPrefix, _G1Prefix, _G2Prefix]).difference([new_key])
                        # adjust dep map as well
                        removeFromInfo(other_groups, var_dep, group_info)

            # print("AFTER ==>")
            # print("Both G1 & G2: ", group_info[_bothPrefix])
            # print("Just G1: ", group_info[_G1Prefix])
            # print("Just G2: ", group_info[_G2Prefix])
            # print("<===========================>")

            (graph0, graph1, is_valid_split) = generateSplit(info, group_info, graph)
            if is_valid_split:
                print("SOLUTION IS A VALID SPLIT FOR MERGED GRAPH %d!!!" % index)
            else:
                print("REJECTING SPLIT!!!")
                sys.exit(-1)
    return (a_model, sat)


def recordVar(vars, entire_set):
    new_list = list(entire_set)
    for a in vars:
        if str(a) not in new_list:
            new_list = list(set(new_list).union([str(a)]))
    new_list.sort()
    return new_list

def getNewSolver(clauses, Z3vars, hard_constraints, relax_list=[]):
    mySolver = Solver()
    Conditions = []
    Values = []
    entire_set = []
    for i in clauses:
        (x, y) = i # add logic for relaxing the clauses
        if Z3vars.get(x) and Z3vars.get(y):
            X = Z3vars.get(x)
            Y = Z3vars.get(y)
            Conditions.append(X != Y)
        # continue
        entire_set = recordVar([x, y], entire_set)

    for x in entire_set:
        addl_value_to_x = False
        # check if (addl_value_to_x
        X = Z3vars.get(x)
        if x not in hard_constraints and x in relax_list:
            addl_value_to_x = True

        # if quota > 0:
        #     if x not in hard_constraints:
        #         addl_value_to_x = True
        #         PossibleDuplNodes.append(str(x))
        #         quota -= 1
        if x in hard_constraints:
            Values.append(X == 0)
        else:
            x_values = Or(X == 0, X == 1)
            if addl_value_to_x:
                x_values = Or(X == 2)  # signifies both a 0 and 1 assignment
            Values.extend([x_values])

    return mySolver, Conditions, Values, entire_set

def solveUsingSMT(info, optionDict, shortOpt, timeOpt):
    verbose     = optionDict.get(verboseKeyword)
    schemeType  = optionDict.get(schemeTypeKeyword)
    #print("Scheme type: ", schemeType)
    variables   = optionDict.get(variableKeyword)
    clauses     = optionDict.get(clauseKeyword)
    constraints = optionDict.get(constraintKeyword)
    bothConst   = optionDict.get(bothKeyword)
    
    searchAll    = optionDict.get(searchKeyword)
    hard_constraints = optionDict.get(hardConstKeyword)
    pk_map_vars  = optionDict.get(pkMapKeyword)
    pk_list      = optionDict.get(pkListKeyword)
    assump_map_vars = optionDict.get(assumpKeyword)
    assump_list  = optionDict.get(assumpListKeyword)
    old_auto_group = info.get(isAutoGroupKeyword)
    # JAA: commented out for benchmarking
    #print("hardConstraints: ", hard_constraints)
    counts  = {}
    Z3vars = {}
    for v in variables:
        Z3vars[ str(v) ]   = Int(str(v)) # create Int refs
        countVar           = "c_" + str(v)
        counts[ str(v) ]   = Int(countVar)
        Z3vars[ countVar ] = counts[str(v)]


    # mySolver = Solver()
    # Conditions = []
    # Values = []
    # for i in clauses:
    #     (x, y) = i
    #     if Z3vars.get(x) and Z3vars.get(y):
    #         X = Z3vars.get(x)
    #         Y = Z3vars.get(y)
    #         Conditions.append( X != Y )
    #         if x in hard_constraints:
    #             Values.append( X == 0 )
    #         else:
    #             Values.extend( [Or(X == 0, X == 1)] )
    #         if y in hard_constraints:
    #             Values.append( Y == 0 )
    #         else:
    #             Values.extend( [Or(Y == 0, Y == 1)] )

    (mySolver, Conditions, Values, EntireSet) = getNewSolver(clauses, Z3vars, hard_constraints) # add
    M = get_models([And(Conditions), And(Values)])
    if(len(M) == 0):
        print("Failed to find a satisfiable solution given constraints. Try again with different or relaxed constraints.")
        print("Hard Constraints: ", hard_constraints)
        print("Clauses: ", clauses)
        print("M: ", [And(Conditions), And(Values)])

        #possible_dup_nodes = ['j0'] # ['a0']
        bigM = []
        potential_dup_nodes = []
        for i in EntireSet:
            possible_dup_nodes = [i]
            (mySolver, Conditions, Values, EntireSet) = getNewSolver(clauses, Z3vars, hard_constraints, possible_dup_nodes)
            M = get_models([And(Conditions), And(Values)])
            if len(M) > 0:
                bigM.extend(M)
                potential_dup_nodes.append(i)

        M = bigM
        print("Unique Solutions (after relaxing logic): ", len(M))
        #print("M: ", [And(Conditions), And(Values)])
        print("Possibly Duplicated Nodes: ", potential_dup_nodes)
        print("Models: ", M)
        #sys.exit(-1)
        #return unsat
    print("Unique solutions: ", len(M))

    # minimize the assumption, if the option is selected
    if shortOpt == SHORT_ASSUMPTION: # and schemeType == pkEncType:
        print("Using Solver to minimize the size of the assumption...")
        modEval = ModelEval(range(len(M)), variables, Z3vars, None)
        #if verbose: modEval.enableVerboseMode()
        (modRef, countMap) = modEval.evaluateSolutionsFromDepMap(M, assump_map_vars, assump_list, optionDict)
        if not old_auto_group:
            # running AutoGroup+
            return checkValidSplit(info, optionDict, convertToGroup(modRef))
        else:
            return (convertToGroup(modRef), sat)

    if shortOpt == SHORT_PUBKEYS: #and schemeType == pkEncType:
        print("Using Solver to minimize the PK constraints...")
        modEval = ModelEval(range(len(M)), variables, Z3vars, None)
        (modRef, countMap) = modEval.evaluateSolutionsFromDepMap(M, pk_map_vars, pk_list, optionDict, rankSolutions=True)
        if not old_auto_group:
            # running AutoGroup+
            return checkValidSplit(info, optionDict, convertToGroup(modRef))
        else:
            return (convertToGroup(modRef), sat)


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
    
    #return (convertToBoolean(modRef), sat)
    if not old_auto_group:
        # running AutoGroup+
        return checkValidSplit(info, optionDict, convertToGroup(modRef))
    else:
        return (convertToGroup(modRef), sat)


### METHODS FOR VERIFYING SOLUTION

_G1Prefix = 'G1'
_G2Prefix = 'G2'
_bothPrefix = 'both'

class DotGraph:
    def __init__(self, name):
        self.name = name
        self.nodes = set()
        self.edges = []
        self.rootNode = None
        self.addedEdgeToRoot = False
        self.outgoingEdges = {}
        self.pairingIdentifiers = set()


    def setPairingIds(self, ids):
        assert type(ids) == set, "cannot set an empty list of pairing IDs"
        self.pairingIdentifiers = ids
        self.nodes = self.nodes.union(ids)

    def getRootNode(self):
        if self.rootNode:
            return self.rootNode
        else:
            rootNodes = []
            for i in self.edges:
                (a, b) = i
                if b == "":
                    rootNodes.append(a)
            return rootNodes

    def getOutgoingEdges(self, e):
        if type(e) != list:
            e_list = [e]
        else:
            e_list = list(e)
        for i in e_list:
            return self.outgoingEdges.get(i)

    def setRootNode(self, var):
        if self.rootNode:
            self.rootNode.append(var)
        else:
            self.rootNode = [var]
        self.edges.append((var, ""))

    def __stripLIST(self, var):
        if LIST_INDEX_SYMBOL in var:
            return var.split(LIST_INDEX_SYMBOL)[0]
        return var

    def __processOutgoingEdge(self, tupl):
        # now process (a -> b)
        (a, b) = tupl
        if b != "":
            if self.outgoingEdges.get(a):
                self.outgoingEdges[a].append(b)
            else:
                self.outgoingEdges[a] = [b]
        return

    def computeOutgoingEdges(self):
        for i in self.edges:
            (a, b) = i
            self.__processOutgoingEdge((a, b))

        the_edges = self.edges
        the_nodes = []
        for i in self.nodes:
            if self.outgoingEdges.get(i):
                the_nodes.append(i)

        # root nodes are nodes *without* incoming edges
        root_nodes = []
        for i in self.edges:
            (a, b) = i
            if a != "" and a not in the_nodes:
                the_nodes.append(a)
            if b != "" and b not in the_nodes:
                the_nodes.append(b)
            if a != "" and b == "":
                root_nodes.append(a)

        child_nodes = set()
        for i in self.outgoingEdges.values():
            child_nodes = child_nodes.union(i)

        for k in self.outgoingEdges.keys():
            if k not in child_nodes:
                if k not in root_nodes:
                    root_nodes.append(k)

        #print("ROOT NODES: ", root_nodes)
        return (the_nodes, the_edges, self.outgoingEdges, root_nodes)

    # a -> b
    def addDirectedEdge(self, a, b):
        if a != b:
            a = self.__stripLIST(a)
            b = self.__stripLIST(b)
            # we don't want any cyclical stuff here
            self.nodes = self.nodes.union([a, b])
            if a == self.rootNode:
                self.addedEdgeToRoot = True
                self.edges.append((a, b))
            else:
                self.edges.append((a, b))
            return True
        else:
            # node has no parent
            self.edges.append((a, ""))
            return True

    def adjustByMap(self, data):
        edges = []
        for i in self.edges:
            (a, b) = i
            if a in data: # use varmap
                a = data[a]
            if b in data: # use varmap
                b = data[b]
            edges.append((a, b))
        self.edges = edges

        nodes = set()
        for i in self.nodes:
            if i in data: # use varmap
                n = data[i]
            else: # keep it
                n = i
            nodes = nodes.union([n])
        self.nodes = nodes


    # merges edges that show up for a given function
    def update(self, graph_dict):
        if self.name in graph_dict:
            self.edges.extend(graph_dict.get(self.name))
        return

    def smart_update(self, graph_dict):
        if self.name in graph_dict:
            the_edges = graph_dict.get(self.name)
            for i in the_edges:
                (a, b) = i
                if a in self.nodes or b in self.nodes:
                    self.edges.append(i)
        return

    def add(self, other):
        # just add to myself
        self.edges += other.edges
        self.edges = list(set(self.edges)) # in case there are duplicated pairs (x,y)
        self.nodes = self.nodes.union( other.nodes )
        if other.outgoingEdges:
            for i,j in other.outgoingEdges.items():
                if self.outgoingEdges.get(i):
                    self.outgoingEdges[i] = list(set(self.outgoingEdges[i]).union(j))
                else:
                    self.outgoingEdges[i] = j
        if other.pairingIdentifiers:
            self.pairingIdentifiers = self.pairingIdentifiers.union(other.pairingIdentifiers)
        return self

    def __add__(self, other):
        if type(self) == type(other):
            return self.add(other)

    def check_equal(self, other):
        return (set(self.edges) == set(other.edges) and
                set(self.nodes) == set(other.nodes))

    def __eq__(self, other):
        if type(self) == type(other):
            return self.check_equal(other)

    def __ne__(self, other):
        if type(self) == type(other):
            return not self.check_equal(other)

    # generate the
    def __str__(self):
        out_str = "digraph "
        out_str += self.name + " {\n"
        for i in self.edges:
            (a, b) = i
            out_str += str(a)
            if b != "": out_str += " -> " + str(b)
            out_str += "\n"
        out_str += "}\n"
        return out_str

def generateSplit(info, group_info, merged_graph):
    """
    :param group_info: final group assignments from split
    :param nodes: all nodes in merged graph
    :param edges: all edges in merged graph
    :param out_going: outgoing edges for each nodes (will be used w/ BFS algorithm to split)
    :return:
    """
    root_node = merged_graph.getRootNode()
    nodes, edges, out_going, other_root_node = merged_graph.computeOutgoingEdges()
    for i in other_root_node:
        if i not in root_node:
            root_node.append(i)
    #print("ROOT NODES: ", root_node)
    pair_ids = merged_graph.pairingIdentifiers
    assert pair_ids != None, "Need pairing identifiers to generate a split!"
    graph0 = DotGraph("graph0")
    graph1 = DotGraph("graph1")
    stack = []
    # build up the stack
    if type(root_node) == list:
        stack = list(root_node)
    else:
        stack.append(root_node)

    # extract group mapping
    bothList = group_info.get(_bothPrefix)
    G1List = group_info.get(_G1Prefix)
    G2List = group_info.get(_G2Prefix)
    marked = []
    hash_list = info.get('hashVarList')
    # set the root node for each graph
    # as dictated by the split
    for r in root_node:
        if hash_list and r in hash_list:
            continue
        if r in bothList:
            graph0.setRootNode(r)
            graph1.setRootNode(r)
        elif r in G1List:
            graph0.setRootNode(r)
        elif r in G2List:
            graph1.setRootNode(r)
        else:
            print("generateSplit: Root node not in one of the group maps => ", r)
            sys.exit(-1)

    # now we can begin BFS traversal
    while len(stack) > 0:
        # visit the top node
        a = stack.pop() # top node

        # get all the children
        out_going_edges = out_going.get(a)
        if out_going_edges:
            for b in out_going_edges:
                ##print("processing edge: '%s' -> '%s', action:" % (a, b), end=" ")
                # (a -> b)
                # check whether 'a' occurs in both, G1 or G2
                if a in bothList:
                    if b in bothList:
                        # must be in both
                        graph0.addDirectedEdge(a, b)
                        graph1.addDirectedEdge(a, b)
                        ##print("added to both")
                    elif b in G1List:
                        graph0.addDirectedEdge(a, b)
                        ##print("added to graph0")
                    elif b in G2List:
                        graph1.addDirectedEdge(a, b)
                        ##print("added to graph1")
                    elif b in pair_ids:
                        # have reached edges of the form "'a' -> PX[0|1]"
                        if a in group_info['pairing'][_G1Prefix]:
                            graph0.addDirectedEdge(a, b)
                            ##print("added to graph0")
                        elif a in group_info['pairing'][_G2Prefix]:
                            graph1.addDirectedEdge(a, b)
                            ##print("added to graph1")
                        else:
                            pass
                            ##print("generateSplit: Dangling node/pairing variable: ", a, "->", b)
                            #sys.exit(-1)
                    else:
                        pass
                        #if a in group_info.get('pairing'):
                        ##print("No mapping for variable: ", b)
                        # check pairing here
                elif a in G1List:
                    if b in G1List or b in bothList or b in pair_ids:
                        graph0.addDirectedEdge(a, b)
                        ##print("added to graph0")
                    else: # clearly a violation so output error msg
                        pass ##print("Doesn't make sense: G1=", a, '-> !G1=', b)
                elif a in G2List:
                    if b in G2List or b in bothList or b in pair_ids:
                        graph1.addDirectedEdge(a, b)
                        ##print("added to graph1")
                    else: # clearly a violation so output error msg
                        pass ##print("Doesn't make sense: G2=", a, '-> !G2=', b)
                else:
                    pass ##print("Var doesn't exist in map: ", a)

                if b not in marked:
                    stack.append(b)
                    marked.append(b)

    # print("<====== SHOW SPLIT ======>")
    # print("Graph0: ", graph0)
    # print("Graph1: ", graph1)
    # print("<====== SHOW SPLIT ======>")

    dup_nodes = False
    for i in hash_list:
        #print("Sanity checking ", i, "...")
        if i in graph0.nodes and i in graph1.nodes:
            #s = i + " has been duplicated!!! ERROR!"
            #print(s)
            dup_nodes = True

    if not dup_nodes:
        print("NO hash variable was duplicated in the split. Yay!!!")

    new_merged_graph = graph0 + graph1
    if merged_graph == new_merged_graph:
        is_valid_split = True
    else:
        is_valid_split = False
        for i in merged_graph.edges:
            if i not in new_merged_graph.edges:
                pass ##print("MISSING EDGE: ", i)
        for i in merged_graph.nodes:
            if i not in new_merged_graph.nodes:
                pass ##print("MISSING NODE: ", i)

    return (graph0, graph1, is_valid_split)


def buildCompleteMap(resultModel, info, xorMap):
    reductionData = info.get('reductionData')
    assumptionData = info.get('assumptionData')
    #reduceDeps1 = info.get('merged_deps')

    reducDeps0 = {}
    reducDeps1 = {}
    if info.get('single_reduction'):
        # adjust if we're dealing with one assumption, otherwise, lay off
        for (reducname, reducrecord) in reductionData.items():
            tmp0 = reducrecord['deps'][0]
            tmp1 = reducrecord['deps'][1]
            # concatenating dictionaries
            reducDeps0 = dict(list(reducDeps0.items()) + list(tmp0.items()))
            reducDeps1 = dict(list(reducDeps1.items()) + list(tmp1.items()))
        reducDeps = (reducDeps0, reducDeps1)

        #1) GenerateSplitSolutionMap
        group_info = GenerateSplitSolutionMap(resultModel, xorMap, info, reducDeps1)
        group_info['verbose'] = info['verbose']

        for (assumpname, assumprecord) in assumptionData.items():
            varmap = assumprecord['varmap']
            if info['verbose']: print("VarMap => ", varmap)
            assumpKey = assumprecord.get('prunedMap')
            if info['verbose']: print("ASSUMP KEY: ", assumpKey)
            for var in sorted(assumpKey.keys()):
                if info['verbose']: print("<============>")
                new_key = processVarWithDep(group_info, var, reducDeps1, varmap)
                if new_key:
                    # traverse the assumpKey dependencies (top half of the merged graph
                    # to see how things should be assigned
                    dep_vars_list = assumpKey.get(var)
                    for var_dep in dep_vars_list:
                        if var_dep in group_info[_bothPrefix]:
                            # no need to change anything (since there's probably a reason for that)
                            continue
                        if var_dep not in group_info[new_key]:
                            addToInfo(new_key, var_dep, group_info)
                            other_groups = set([_bothPrefix, _G1Prefix, _G2Prefix]).difference([new_key])
                            # adjust dep map as well
                            removeFromInfo(other_groups, var_dep, group_info)
                if info['verbose']: print("<============>")

        #print("Both G1 & G2: ", group_info[_bothPrefix])
        #print("Just G1: ", group_info[_G1Prefix])
        #print("Just G2: ", group_info[_G2Prefix])
    else:
        # dealing with multiple assumptions so tread very carefully for now
        return

    return group_info


def addToInfo(key, assignVar, info):
    """
    :param key: 'G1', 'G2' or 'both'
    :param assignVar: var in question
    :param info: mapping of existing group assignments
    :return:
    """
    assert key in [_G1Prefix, _G2Prefix, _bothPrefix]
    info[key] = info[key].union([assignVar])
    ##print("Added '%s' to '%s' set" % (assignVar, key))
    return

def removeFromInfo(keys, assignVar, info):
    assert type(keys) in [set, list], "invalid input for keys in removeFromInfo"
    for key in keys:
        if assignVar in info.get(key):
            info[key].remove(assignVar)
            ##print("Removed '%s' from '%s' set" % (assignVar, key))
    return


def processVarWithDep(info, assignVar, deps, varmap):
    verbose = True # info['verbose']
    numG1 = 0
    numG2 = 0
    numBoth = 0
    if(assignVar in deps.keys()):
        #print("G1 => ", info['G1'], " G2 => ", info['G2'], " both => ", info['both'])

        depList = []
        for (key,val) in deps.items():
            if(assignVar in val):
                depList.append(key)

        depListGroups = {}
        numG1 = 0
        numG2 = 0
        numBoth = 0
        for i in depList:
            if((i in varmap) and (varmap[i] in info['G1'])):
                depListGroups[i] = types.G1
                numG1+=1
            elif((i in varmap) and (varmap[i] in info['G2'])):
                depListGroups[i] = types.G2
                numG2+=1
            elif((i in varmap) and (varmap[i] in info['both'])):
                depListGroups[i] = "both"
                numBoth+=1
            elif(i in info['G1']):
                depListGroups[i] = types.G1
                numG1+=1
            elif(i in info['G2']):
                depListGroups[i] = types.G2
                numG2+=1
            elif(i in info['both']):
                depListGroups[i] = "both"
                numBoth+=1

        if ( not(numBoth == 0) or (not(numG1 == 0) and not(numG2 == 0)) ):
            if verbose: print(assignVar, ":-> split computation in G1 & G2")
            addToInfo(_bothPrefix, assignVar, info)
            # make sure it's not in G1 or G2 list
            removeFromInfo(['G1','G2'], assignVar, info)
            return _bothPrefix
        elif (not(numG1 == 0) and (numG2 == 0) and (numBoth == 0)):
            if verbose: print(assignVar, ":-> just in G1.")
            addToInfo(_G1Prefix, assignVar, info)
            removeFromInfo(['G2', 'both'], assignVar, info)
            return _G1Prefix
        elif (not(numG2 == 0) and (numG1 == 0) and (numBoth == 0)):
            if verbose: print(assignVar, ":-> just in G2.")
            addToInfo(_G2Prefix, assignVar, info)
            removeFromInfo(['G1', 'both'], assignVar, info)
            return _G2Prefix
        else:
            ##print("Safe to ignore this var: ", assignVar)
            if deps[assignVar].issubset(info['both']):
                addToInfo(_G1Prefix, assignVar, info)
                # need to think about this carefully, verify that we can safely make this assignment
            elif deps[assignVar].issubset(info['G1']):
                addToInfo(_G1Prefix, assignVar, info)
                removeFromInfo(['G2', 'both'], assignVar, info)
            elif deps[assignVar].issubset(info['G2']):
                addToInfo(_G2Prefix, assignVar, info)
                removeFromInfo(['G1', 'both'], assignVar, info)


    return None


def GenerateSplitSolutionMap(resultModel, xorMap, info, deps):
    #print("<===== Deriving Specific Solution from Results =====>")
    G1_deps = set()
    G2_deps = set()
    resultMap = {}
    newSol = {}
    # convert from z3 model to dictionary
    for tupl in resultModel:
        (k, v) = tupl
        resultMap[ k ] = v

    # map the
    pairingInfo = {}
    pairingInfo[_G1Prefix] = []
    pairingInfo[_G2Prefix] = []
    for i in info['G1_lhs'][0] + info['G1_rhs'][0]:
        # get the z3 var for it
        z3Var = xorMap.get(i) # gives us an alphabet
        # look up value in resultMap
        varValue = resultMap.get(z3Var)
        # get group
        if varValue == True:
            group = _G1Prefix
        else:
            group = _G2Prefix

        if i in info['G1_lhs'][0]:
            deps = info['G1_lhs'][1].get(i)
        else:
            deps = info['G1_rhs'][1].get(i)

        deps = list(deps); deps.append(i) # var name to the list

        newSol[ i ] = group
        if group == _G1Prefix:
            G1_deps = G1_deps.union(deps)
            pairingInfo[_G1Prefix].append(i)
        elif group == _G2Prefix:
            G2_deps = G2_deps.union(deps)
            pairingInfo[_G2Prefix].append(i)
        else:
            raise Exception("Invalid assignment: ", group)
    #print("<===== Deriving Specific Solution from Results =====>")
    both = G1_deps.intersection(G2_deps)
    G1 = G1_deps.difference(both)
    G2 = G2_deps.difference(both)
    #print("Both G1 & G2: ", both)
    #print("Just G1: ", G1)
    #print("Just G2: ", G2)
    return { 'G1':G1, 'G2':G2, 'both':both, 'pairing':pairingInfo, 'newSol':newSol }

def _assignVarOccursInBoth(varName, info):
    """determines if varName occurs in the 'both' set. For varName's that have a '#' indicator, we first split it
    then see if arg[0] is in the 'both' set."""
    if varName.find(LIST_INDEX_SYMBOL) != -1:
        varNameStrip = varName.split(LIST_INDEX_SYMBOL)[0]
    else:
        varNameStrip = None
    if varName in info['both']:
        return True
    elif varNameStrip != None and varNameStrip in info['both']:
        return True
    return False

def _assignVarOccursInG1(varName, info):
    """determines if varName occurs in the 'G1' set. For varName's that have a '#' indicator, we first split it
    then see if arg[0] is in the 'G1' set."""
    if varName.find(LIST_INDEX_SYMBOL) != -1:
        varNameStrip = varName.split(LIST_INDEX_SYMBOL)[0]
    else:
        varNameStrip = None
    if varName in info['G1']:
        return True
    elif varNameStrip != None and varNameStrip in info['G1']:
        return True
    return False

def _assignVarOccursInG2(varName, info):
    """determines if varName occurs in the 'G2' set. For varName's that have a '#' indicator, we first split it
    then see if arg[0] is in the 'G2' set."""
    if varName.find(LIST_INDEX_SYMBOL) != -1:
        varNameStrip = varName.split(LIST_INDEX_SYMBOL)[0]
    else:
        varNameStrip = None
    if varName in info['G2']:
        return True
    elif varNameStrip != None and varNameStrip in info['G2']:
        return True
    return False


def _handleVarInfo(assign, blockStmt, info, noChangeList, startLines={}):
    if Type(assign) == ops.EQ:
        assignVar = blockStmt.getAssignVar()
        # store for later
        newLine = None
        varTypeObj = info['varTypes'].get(assignVar)
        # case A: randomness and occurs in startLines
        if blockStmt.getHasRandomness() and startLines.get(assignVar) != None:
            newLines.extend( startLines[assignVar] )
            return True
            #if not assignVarIsGenerator(assignVar, info):
        # case B: randomness and varTypeObj != None
        if blockStmt.getHasRandomness() and varTypeObj != None:
            if varTypeObj.getType() in [types.ZR, types.GT]:
                pass # ignore
                #if info['verbose']: print(" :-> not a generator, so add to newLines.", end=" ")
                #newLine = str(assign) # unmodified
                #newLines.append(assign) # unmodified
                #return True
            else:
                if info['verbose']: print(assignVar, " :-> what type ?= ", info['varTypes'].get(assignVar).getType(), end=" ")
                if info['varTypes'].get(assignVar).getType() == types.G1:
                    pass # figure out what to do here

        if _assignVarOccursInBoth(assignVar, info):
            if info['verbose']: print(" :-> split computation in G1 & G2:", blockStmt.getVarDepsNoExponents(), end=" ")
            #newLine = updateAllForBoth(assign, assignVar, blockStmt, info, True, noChangeList)
        elif _assignVarOccursInG1(assignVar, info):
            if info['verbose']: print(" :-> just in G1:", blockStmt.getVarDepsNoExponents(), end=" ")
            noChangeList.append(str(assignVar))
            #newLine = updateAllForG1(assign, assignVar, blockStmt, info, False, noChangeList)
        elif _assignVarOccursInG2(assignVar, info):
            if info['verbose']: print(" :-> just in G2:", blockStmt.getVarDepsNoExponents(), end=" ")
            noChangeList.append(str(assignVar))
            #newLine = updateAllForG2(assign, assignVar, blockStmt, info, False, noChangeList)
        elif blockStmt.getHasPairings(): # in GT so don't need to touch assignVar
            if info['verbose']: print(" :-> update pairing.", end=" ")
            #noChangeList.append(str(assignVar))
            #newLine = updateForPairing(blockStmt, info, noChangeList)
        elif len(set(blockStmt.getVarDepsNoExponents()).intersection(info['generators'])) > 0:
            if info['verbose']: print(" :-> update assign iff lhs not a pairing input AND not changed by traceback.", end=" ")
            if assignVar not in info['pairing'][_G1Prefix] and assignVar not in info['pairing'][_G2Prefix]:
                noChangeList.append(str(assignVar))
                info['G1'] = info['G1'].union( assignVar )
                #newLine = updateAllForG1(assign, assignVar, blockStmt, info, False, noChangeList)
                if info['verbose']: print(":-> var deps = ", blockStmt.getVarDepsNoExponents())
        else:
            pass
            #info['myAsymSDL'].recordUsedVar(blockStmt.getVarDepsNoExponents())
            #newLine = assign
        # add to newLines
        # if type(newLine) == list:
        #     newLines.extend(newLine)
        # elif newLine != None:
        #     #if newLine not in newLines:
        #     newLines.append(newLine)
        return True
    elif Type(assign) == ops.IF:
#        print("JAA type: ", Type(assign), blockStmt.getVarDepsNoExponents())
        # TODO: there might be some missing cases in updateForIfConditional. Revise as appropriate.
        assignVars = blockStmt.getVarDepsNoExponents()
        assign2 = assign
        if not HasPairings(assign):
            for assignVar in assignVars:
                if _assignVarOccursInG1(assignVar, info):
                    if info['verbose']: print(" :-> just in G1:", assignVar, end="")
                    #assign2 = updateForIfConditional(assign2, assignVar, blockStmt, info, types.G1, noChangeList)
                elif _assignVarOccursInG2(assignVar, info):
                    if info['verbose']: print(" :-> just in G2:", assignVar, end="")
                    #assign2 = updateForIfConditional(assign2, assignVar, blockStmt, info, types.G2, noChangeList)
            #print("TODO: Not a good sign. how do we handle this case for ", assignVar, "in", assign)
        else: # pairing case
            pass
            #assign2 = updateForPairing(blockStmt, info, noChangeList)

        # if str(assign2) == str(assign):
        #     newLines.append(assign)
        # else:
        #     newLines.append(assign2)
    else:
        print("Unrecognized type: ", Type(assign))
    return False


"""
1. generic function that takes three lists of group assignments..
    { 'G1' : varList, 'G2' : varList, 'both': varList }
2. goes through a given 'block' and goes each statement:
    - exponentiation, multiplication and pairing
    - rewrite each statement where a generator appears (or derivative of one) using three lists:
        if leftAssignVar in 'both': create 2 statements
        if leftAssignVar in 'G1': create 1 statement in G1
        if leftAssignVar in 'G2': create 1 statement in G2
"""
def GenerateSchemeSplit(entireSDL, funcName, blockStmts, info, noChangeList, startLines={}):
    parser = sdl.SDLParser()
    funcNode = BinaryNode("func:" + str(funcName))
    begin = BinaryNode(ops.BEGIN, funcNode, None) # "BEGIN :: func:" + funcName
    end = BinaryNode(ops.END, funcNode, None) # "END :: func:" + funcName
    newLines = [begin] # + list(startLines)
    stack = []
    lines = list(blockStmts.keys())
    lines.sort()

    for index, i in enumerate(lines):
        assert type(blockStmts[i]) == sdl.VarInfo, "transformFunction: blockStmts must be VarInfo Objects."
        if blockStmts[i].getIsForLoopBegin():
            if blockStmts[i].getIsForType():
                pass
                #newLines.append(parser.parse("BEGIN :: for\n")) # "\n" + START_TOKEN + " " + BLOCK_SEP + ' for')
            elif blockStmts[i].getIsForAllType():
                pass
                #newLines.append(parser.parse("BEGIN :: forall\n"))  # "\n" + START_TOKEN + " " + BLOCK_SEP + ' forall')
            #newLines.append(blockStmts[i].getAssignNode())
        elif blockStmts[i].getIsForLoopEnd():
            #newLines.append(blockStmts[i].getAssignNode())
            pass
        elif blockStmts[i].getIsIfElseBegin():
            #newLines.append(parser.parse("BEGIN :: if\n")) # "\n" + START_TOKEN + " " + BLOCK_SEP + ' if')
            assign = blockStmts[i].getAssignNode()
            if info['verbose']: print(i, ":", assign, end="")
            _handleVarInfo(assign, blockStmts[i], info, noChangeList)

        elif blockStmts[i].getIsIfElseEnd():
            #newLines.append(blockStmts[i].getAssignNode())
            pass
        elif blockStmts[i].getIsElseBegin():
            #newLines.append(blockStmts[i].getAssignNode())
            pass
        else:
            assign = blockStmts[i].getAssignNode()
            if info['verbose']: print(i, ":", assign, end="")
            _handleVarInfo(assign, blockStmts[i], info, noChangeList, startLines)

        if info['verbose']: print("")
    #newLines.append(end)
    return # newLines
