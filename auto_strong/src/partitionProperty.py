import src.sdlpath, sys, os, random, string, re, importlib
import sdlparser.SDLParser as sdl
from sdlparser.SDLang import *
from src.sdltechniques import *
from src.bswTransform import BSWTransform
from src.bsTransform import applyBSTransform
from z3 import *
import subprocess
from os.path import abspath, dirname, join
  
expTimeout = 60 # 21600 # 6 hours
stringToInt = "stringToInt"
intToBits   = "intToBits"
skipTransform = "skipTransform"

AND = " && "
def runAutoStrong(sdlFile, config, options, sdlVerbose=False):
    sdl.parseFile(sdlFile, sdlVerbose, ignoreCloudSourcing=True)
    global assignInfo
    assignInfo = sdl.getAssignInfo()
    setting = sdl.assignInfo[sdl.NONE_FUNC_NAME][ALGEBRAIC_SETTING].getAssignNode().getRight().getAttribute()
    assert setting == sdl.SYMMETRIC_SETTING, "AutoStrong requires a symmetric scheme for simplicity."
    origVarTypes = dict(sdl.getVarTypes().get(sdl.TYPES_HEADER))
    
    # extract property 1 details...
    generators = []
    if hasattr(config, "setupFuncName"):
        setupConfig  = sdl.getVarInfoFuncStmts( config.setupFuncName )
        theStmt, theTypes = setupConfig[0], setupConfig[1]
        extractGenerators(theStmt, theTypes, generators)
    if hasattr(config, "keygenFuncName"):
        keygenConfig  = sdl.getVarInfoFuncStmts( config.keygenFuncName )
        theStmt, theTypes = keygenConfig[0], keygenConfig[1]
        extractGenerators(theStmt, theTypes, generators)

    signConfig  = sdl.getVarInfoFuncStmts( config.signFuncName )
    signStmts, signTypes = signConfig[0], signConfig[1]
    extractGenerators(signStmts, signTypes, generators)
    
    verifyConfig  = sdl.getVarInfoFuncStmts( config.verifyFuncName )
    theStmt, theTypes = verifyConfig[0], verifyConfig[1]
    extractGenerators(theStmt, theTypes, generators)
    
    assert len(generators) != 0, "signature scheme does not select any generators?"
    baseGen = generators[0]
    print("Base generator: ", baseGen)
    generators.remove(baseGen)    
    print("Other generator: ", generators)

    #get config parameters
    msg     = config.messageVar
    msgList = traceMessage(signStmts, signTypes, msg)
    if len(msgList) == 0:
        # msg used directly
        msgVar = msg
    else:
        # indirection on msg
        msgList.append(msg)
        msgVar = msgList
    print("msgVar: ", msgVar)
    sigVar = config.signatureVar
    
    (name, varInf) = getVarNameEntryFromAssignInfo(assignInfo, sigVar)
    if name != config.signFuncName:
        sys.exit("runAutoStrong: '%s' not in the sign function." % sigVar)
    #print("identified signature: ", varInf.getAssignNode())
    listVars = varInf.getListNodesList()
    if len(listVars) == 0:
        listVars.append(sigVar) # probably just one element in signature
    #print("list of possible vars: ", listVars)
    sigma = property1Extract(config.signFuncName, assignInfo, listVars, msgVar)
    #if testForSUCMA:
        # quick test for whether scheme is SU-CMA secure already
    #    sigma['sigma1'] += sigma['sigma2']
    #    sigma['sigma2'] = []
    if sdlVerbose:
        print("sigma1 => ", sigma['sigma1'])
        print("sigma2 => ", sigma['sigma2'])
        
    prop2Result = property2Extract(config.verifyFuncName, assignInfo, baseGen, generators, sigma)
    noSigma2Result = noSigma2Check(sigma)

    if options.get(skipTransform): return "skip_transform"
    
    if prop2Result and not noSigma2Result:
        print("Applying BSW transformation...")
        # extract types for all variables
        varTypes = sdl.getVarTypes().get(TYPES_HEADER)
        for i in config.functionOrder:
            #print("Processing func: ", i)
            varTypes.update( sdl.getVarTypes().get(i) )
        
        #print("Type variables for all: ", varTypes.keys())
        bsw = BSWTransform(assignInfo, origVarTypes, varTypes, msgVar, msgList)
        newSDL = bsw.constructSDL(config, options, sigma)
        return newSDL
    
    elif prop2Result and noSigma2Result:
        #print("Signature Scheme Already Strongly Unforgeable!")
        sys.exit(0)
    else:
        print("Applying BS transformation...")
        return applyBSTransform(sdlFile, config)
        
def extractGenerators(stmt, _types, generators):
    assert type(generators) == list, "generator should a list."
    lines = list(stmt.keys())
    lines.sort()
    for i in lines:
        if type(stmt[i]) == sdl.VarInfo and stmt[i].getHasRandomness() and Type(stmt[i].getAssignNode()) == ops.EQ:
            t = stmt[i].getAssignVar()
            if _types.get(t) == None:
                typ = stmt[i].getAssignNode().right.left.attr
            else:
                typ = _types[t].getType()
            if typ == types.G1:
                if (stmt[i].getOutsideForLoopObj() != None): inForLoop = True
                else: inForLoop = False
                print(i, ": ", typ, " :=> ", stmt[i].getAssignNode(), ", loop :=> ", inForLoop)
                if not inForLoop: 
                    generators.append(str(stmt[i].getAssignVar()))
                else:
                    listRef = stmt[i].getAssignVar().split(LIST_INDEX_SYMBOL)[0]
                    generators.append(listRef)
    return None

def traceMessage(Stmt, _types, msgVar):
    if type(msgVar) != str: 
        #"messageVar should be a str."
        return []
    lines = list(Stmt.keys())
    lines.sort()
    msgVarList = []
    for i in lines:
        assert type(Stmt[i]) == sdl.VarInfo, "traceMessage: not a VarInfo object."
        if Type(Stmt[i].getAssignNode()) == ops.EQ and Stmt[i].getAssignVar() not in [inputKeyword, outputKeyword]: # assignment node
            if msgVar in Stmt[i].getVarDeps() and isHashCall(Stmt[i].getAssignNode()):
                # expecting a hash call to a specified group type               
                if Stmt[i].getAssignVar() not in msgVarList: msgVarList.append( Stmt[i].getAssignVar() )
            elif msgVar in Stmt[i].getVarDeps() and Type(Stmt[i].getAssignNode().getRight()) == ops.FUNC:
                # expecting stringToInt or intToBits
                if Stmt[i].getAssignNode().getRight().attr in [stringToInt, intToBits]:
                    if Stmt[i].getAssignVar() not in msgVarList: msgVarList.append( Stmt[i].getAssignVar() )
                else:
                    print("DEBUG: Unrecognized function over " + msgVar)

    #print("msgVarList: ", msgVarList)
    assert len(msgVarList) <= 1, "perhaps, inconsistent functions over " + msgVar
    return msgVarList


def getProgramSlice(funcName, assignInfo, varName, sliceList):
    assert type(sliceList) == list, "invalid input for sliceList"
    (name, varInf) = getVarNameEntryFromAssignInfo(assignInfo, varName)
    if name != funcName: return
    sliceList.append(varInf.getLineNo())
    print(varInf.getLineNo(), ":", varInf.getAssignNode())
    varDeps = list(varInf.getVarDeps())
    # prevent endless recursion in case we have varA := varA * varB
    if varName in varDeps: varDeps.remove(varName)
    for i in varDeps:
        getProgramSlice(funcName, assignInfo, i, sliceList)    
    return None

def isPresentInVarDeps(targetFuncName, assignInfo, msg, depList):
    for i in depList:
        (name, varInf) = getVarNameEntryFromAssignInfo(assignInfo, i)
        if name != targetFuncName: continue
        if msg in varInf.getVarDeps() or len(set(msg).intersection(varInf.getVarDeps())) > 0:
            return True
    return False

def noSigma2Check(sigma):
    if len(sigma['sigma2']) == 0: return True
    return False 

"""Extracts candidate sigma_1 and sigma_2 values from the signature"""
def property1Extract(targetFuncName, assignInfo, listVars, msg):
    # need to find 'msg' in the list.
    sigma = {'sigma1':[], 'sigma2':[]}
    
    for i in listVars:
        (name, varInf) = getVarNameEntryFromAssignInfo(assignInfo, i)
        if name != targetFuncName: 
            print("DEBUG: ", i, " NOT in ", targetFuncName, ". Perhaps, naming conflict?")
            continue
        print(i, " : ", varInf.getAssignNode())
        deps = list(varInf.getVarDeps())
        if varInf.getHasRandomness():
            deps.append(i)
        print(" deps: ", deps)
        print("")
        if msg in deps or isPresentInVarDeps(targetFuncName, assignInfo, msg, deps):
            sigma['sigma1'].append(i)
        elif (type(msg) == list and len(set(msg).intersection(deps)) > 0) or isPresentInVarDeps(targetFuncName, assignInfo, msg, deps):
            sigma['sigma1'].append(i) # alternative check where there are multiple variables that make up message
        else:
            sigma['sigma2'].append(i)
        
    print("<=== Candidate sigma1 and sigma2 ===>")
    #print("sigma1 => ", sigma['sigma1'])
    #print("sigma2 => ", sigma['sigma2'])
    
    if len(sigma['sigma1']) == 0: sys.exit("Signature scheme does not satisfy partitioning property. Property 1 check failed!")
    return sigma

"""
Step 1 for property 2 check. Decompose each verification condition to base elements and exponents.
"""
class Decompose:
    def __init__(self, assignInfo, baseGen, freeVars):
        self.assignInfo = assignInfo
        self.baseGen    = baseGen
        self.freeVars = freeVars
        self.verbose = False
        
    def visit(self, node, data):
        pass
            
    def visit_attr(self, node, data):
        varName = node.getRefAttribute()
        if varName in self.freeVars: return
        name, varInf = getVarNameEntryFromAssignInfo(self.assignInfo, varName)
        if varInf == None: return
        node2 = varInf.getAssignBaseElemsOnly()
        if node2 == None: return
        elif str(node2) == varName:
            if isHashCallNonZR(varInf.getAssignNode()):
                node2 = BinaryNode.copy(varInf.getAssignNode().getRight())
        varDeps = varInf.getVarDeps()

        if self.verbose:
            print("<=====>")
            print("varName: ", varName)
            print("varInf: ", node2) #varInf.getAssignBaseElemsOnly())
            print("varDeps: ", varDeps)
        if varName in varDeps:
            print("isIterator: ", varName in varDeps)
            DeleteThisVar(varName, node2)
        else:
            for i in varDeps:
                # see if any variables need to be removed
                name, varInf2 = getVarNameEntryFromAssignInfo(self.assignInfo, i)
                if varInf2 != None and i in varInf2.getVarDeps(): print("\t Delete ", i, ":", varInf2.getVarDeps()); DeleteThisVar(i, node2)

        if varName != str(node2):
            # make the substitution
            if node == data['parent'].left:
                data['parent'].left = node2
            elif node == data['parent'].right:
                data['parent'].right = node2
        if self.verbose: print("<=====>")        
        return 

class Transform:
    def __init__(self, baseGen, generators, varTypes):
        self.baseGen    = baseGen
        self.generators = generators
        self.varTypes   = varTypes
        self.reapplyTransform = False
    
    def shouldReapply(self):
        return self.reapplyTransform
    
    def visit(self, node, data):
        return
    
    def visit_exp(self, node, data):
        # this node is visited last in a post-order traversal
        if Type(node.left) == ops.ATTR and str(node.left) == "1":
            # promote the right node
            addAsChildNodeToParent(data, node.right)
        return
    
    def visit_hash(self, node, data):
        #print("Transforming...: ", node)
        if str(node.right) == 'G1':
            new_hash = BinaryNode(ops.EXP, BinaryNode("1"), BinaryNode.copy(node.left))
            BinaryNode.setNodeAs(node, new_hash)
            #print("Result: ", node)
            self.reapplyTransform = True
        else:
            print("Transform class: need to handle other hash cases: ", node.right)
        return
    
    def visit_mul(self, node, data):
        if Type(node.left) == ops.PAIR or Type(node.right) == ops.PAIR:
            node.type = ops.ADD
        return

    def visit_div(self, node, data):
        if Type(node.left) == ops.PAIR or Type(node.right) == ops.PAIR:
            node.type = ops.SUB
        return
    
    def visit_attr(self, node, data):
        varName = str(node)
        if varName == self.baseGen:
            node.setAttribute("1") # replace generators
        return
        
def property2Extract(verifyFuncName, assignInfo, baseGen, generators, sigma):
    #TODO: use term rewriter to breakdown and extract the verification equation
    # 1) convert the pairing equation to the version expected by our Z3 solver
    # 2) determine whether the equation satisfies the following constraint:
    #    - \sigma_1 != \sigma_1pr && verify(pk, m, \sigma_1pr, \sigma_2) ==> True
    # Goal: verify that there is at most one \sigma_1 verifies with \sigma_2 under pk
    verifyConfig = sdl.getVarInfoFuncStmts( verifyFuncName )    
    Stmts = verifyConfig[0]
    lines = list(Stmts.keys())
    lines.sort()
    verifyConds = []
    
    for index, i in enumerate(lines):
        assert type(Stmts[i]) == sdl.VarInfo, "Stmts not VarInfo Objects for some reason."
        if Stmts[i].getIsIfElseBegin():
            node = Stmts[i].getAssignNode()
            print("Conditional: ", node.left) # extract equality and decompose... then test whether pairings exist manually
            verifyConds.append( BinaryNode.copy(node.left) )
    
    genMap = {}
    for i in generators:
        new_node = BinaryNode(ops.EXP, BinaryNode(baseGen), BinaryNode(i + "Exp"))
        genMap[ i ] = new_node
    
    freeVars = list(sigma['sigma1'])
    newVerifyConds = []
    verifyThese = []
    goalCond = {}
    for i in verifyConds:
        if HasPairings(i):
            print("Original: ", i)
            v = BinaryNode.copy(i)
            dep = Decompose(assignInfo, baseGen, freeVars)
            sdl.ASTVisitor(dep).postorder(i) 

            dep2 = Decompose(assignInfo, baseGen, [])
            sdl.ASTVisitor(dep2).postorder(v)
            for x in generators:
                subVar = SubstituteVarWithNode(x, genMap[x])
                sdl.ASTVisitor(subVar).postorder(i)
                sdl.ASTVisitor(subVar).postorder(v)
            
            print("\nStep 1: Decomposed: ", i)
            #print("\nFull Decomp: ", v)
            
            j = BinaryNode.copy(i)
            j = SimplifyExponents(j, baseGen)
            v = SimplifyExponents(v, baseGen)

            tf1 = Transform(baseGen, generators, None)
            tf2 = Transform(baseGen, generators, None)            
            sdl.ASTVisitor(tf1).postorder(j)
            sdl.ASTVisitor(tf2).postorder(v)
            if tf1.shouldReapply(): sdl.ASTVisitor(tf1).postorder(j)
            if tf2.shouldReapply(): sdl.ASTVisitor(tf2).postorder(v)
                
            print("\nStep 2: Simplify & Transform: ", j)
            #print("\nFull Final: ", v)
            verifyThese.append( v )
            newVerifyConds.append( j )
            h = BinaryNode.copy(j)
            for x in freeVars:
                newVar = x + "pr"
                goalCond[ x ] = newVar # used to construct sigma_1 != sigma_1
                sdl.ASTVisitor( SubstituteVar(x, newVar) ).postorder(h)
            newVerifyConds.append( h )

                
    # 2. breakdown
    varListMap = {}
    for i in newVerifyConds:
        ga = GetAttrs(dropPounds=True)
        sdl.ASTVisitor(ga).postorder(i)
        varListMap[ str(i) ] = ga.getVarList()
    
    # Uncomment for correctness test with the original verification equation.
    varListMap2 = {}
    for i in verifyThese:
        ga = GetAttrs(dropPounds=True)
        sdl.ASTVisitor(ga).postorder(i)
        varListMap2[ str(i) ] = ga.getVarList()
    
    isCorrect = testCorrectWithZ3(verifyThese, varListMap2)
    if isCorrect == True:
        print("Verification Equation Correct!!")
    else:
        print("Equation NOT consistent: take a look at your SDL.")
        print("Result: ", isCorrect)
    print("\nStep 3: test partition using Z3.")

    return testPartWithZ3(newVerifyConds, goalCond, varListMap)

def buildZ3Expression(node, varMap, Z3Funcs):
    if node == None: return None
    if node.left != None: leftNode   = buildZ3Expression(node.left, varMap, Z3Funcs)
    if node.right != None: rightNode = buildZ3Expression(node.right, varMap, Z3Funcs)
    
    # visit the root
    if Type(node) == ops.EQ_TST:
        return (leftNode == rightNode)
    elif Type(node) == ops.AND:
        return And(leftNode, rightNode)
    elif Type(node) == ops.PAIR:
        return Z3Funcs['pair'](leftNode, rightNode)
    elif Type(node) == ops.ADD:
        return leftNode + rightNode
    elif Type(node) == ops.SUB:
        return leftNode - rightNode
    elif Type(node) == ops.MUL or Type(node) == ops.EXP:
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

def doesPartHoldWithZ3(subGoals):
    """ Z3 documentation ==>
        unsat : unsatisfiable. Proves that equations and constraints are impossible and thus, partitioning property holds. Action: return True
        unkown : means that the solver is not sure. As a result, means could NOT find proof that confirms that the scheme is partitioned. Action: return False.
    """
    # test
    timeout = 60000 # 1 minute
    testSolver = TryFor(Then("qfnra-nlsat", "nlsat"), timeout).solver()
    testSolver.add( subGoals )
    result = testSolver.check()
    print(result)
    if result == unsat:
        print("Signature is PARTITIONED!!!")        
        return True
    elif result == unknown:
        # this indicates that the solver could not confirm that the equation was indeed impossible to satisfy
        return False
    else:
        # found solution which is also not good
        print(testSolver.model())
        return False    

def doesPartHoldWithMath(vars, equations, timeout=60): # default is 1 minute
    equations_str = ""
    vars_str = ""
    for i in equations:
        j = str(i)
#        if "And" in j: j = j.replace("And", "").replace(",", AND)
        equations_str += str(j).replace("\n", " ").replace("\t", "") + AND
    equations_str = equations_str[:-len(AND)]
    for i in vars:
        vars_str += str(i) + ","
    vars_str = vars_str[:-1] # Modulus -> 17, FindInstance
    #reduce_cmd = [pathToExe, "TimeConstrained[FindInstance[" + equations_str + ", {" + vars_str + "}, Reals], " + str(timeout) + "]"]
    reduce_cmd = "TimeConstrained[FindInstance[" + equations_str + ", {" + vars_str + "}, Reals], " + str(timeout) + "]"
    #reduce_cmd = ["src/runMath", "TimeConstrained[Reduce[" + equations_str + ", {" + vars_str + "}, Integers], " + str(timeout) + "]"]    
    print("Mathematica cmd: ", reduce_cmd)
#    my_env = os.environ
#    my_env["PATH"] = "/usr/bin:" + my_env["PATH"]
    #p = subprocess.Popen(reduce_cmd, stdout=subprocess.PIPE, shell=True, env={'PATH':'/Users/waldoayo/Documents/Projects/auto-tools/auto_strong/src'})
    #preprocessed, _ = p.communicate()
    #result = preprocessed.strip()
    os.system("src/runMath '%s'" % (reduce_cmd))
    
    f = open('file.txt', 'r')
    answer = f.readlines()
    f.close()
    if len(answer) == 0: result = b'{}'
    else: result = answer[0]
    
    print("Mathematica output: ", result)
    if result == b'{}': # b'False':
        #print("FindInstance could find NO solutions...")
        print("Signature is PARTITIONED!!!")        
        return True
    return False

def testCorrectWithZ3(verifyEqs, varListMap):
    I = IntSort()
    E = Function('E', I, I, I)
    x, y, z = Ints('x y z')
    
    my_solver = Then(With('simplify', arith_lhs=True), 'solve-eqs', 'smt').solver() # 'normalize-bounds'
    my_solver.add( ForAll([x, y], E(x, y) == x*y) )
    my_solver.add( ForAll([x, y, z], E(x+y, z) == (x*z + y*z)) )
    my_solver.add( ForAll([x, y, z], E(x, y+z) == (y*x + z*x)) )
    
    print(my_solver)
    if my_solver.check() == unsat:
        sys.exit("ERROR: Z3 setup failed.")

    M = my_solver.model()
    print(M, "\n")

    Z3Funcs = {'pair': E }
    equations = []
    varMap = {}
    timeout = 60000 # 1 minute
    for i in verifyEqs:
        varList = varListMap[str(i)]
        print("<====================>")
        print("Creating Z3 ints for... ", varList)
        for j in varList:
            if j not in varMap.keys(): varMap[ j ] = Int(j)
        print("varMap: ", varMap)
        # TODO: need recursive algorithm to model pairings
        print("Creating Z3 expression for... ", i)
        eqList = retrieveAnds(i)
        eqList.reverse()
        finalExp = ""
        for k in eqList:
            print("Z3 input: ", k)
            newExp = buildZ3Expression(k, varMap, Z3Funcs)
            result = str(M.evaluate(newExp)).replace("\n", " ").replace("\t", "")
            print("Z3 output: ", newExp)
            print("Z3 simplified: ", result)
            print("<====================>")
            finalExp += result + AND
        
        finalExp = finalExp[:-len(AND)]
#        print("PATH: ", os.environ['PATH'])
#        print("PYTHONPATH: ", os.environ.get('PYTHONPATH'))
        #simplify_cmd = ["runMath", "Simplify[" + str(finalExp).replace("\n", " ") + "]"]
        #print("Verify with Mathematica:  ", simplify_cmd )
        simplify_cmd = "Simplify[" + str(finalExp).replace("\n", " ") + "]"
        
        os.system("src/runMath '%s'" % (simplify_cmd))
        
        f = open('file.txt', 'r')
        answer = f.readlines()
        f.close()
        if len(answer) == 0: result = b'{}'
        else: result = answer[0]

#        p = subprocess.Popen(simplify_cmd, stdout=subprocess.PIPE, shell=True)
#        preprocessed, _ = p.communicate()
#        result = preprocessed.strip()
        print("Mathematica output: ", result)
        if result == 'True':
            continue
        else:
            return result
    
    return True

def testPartWithZ3(verifyEqs, goalCond, varListMap):    
    I = IntSort()
    E = Function('E', I, I, I)
    x, y, z = Ints('x y z')
    
    my_solver = Then(With('simplify', arith_lhs=True), 'solve-eqs', 'smt').solver() # 'normalize-bounds'
    my_solver.add( ForAll([x, y], E(x, y) == x*y) )
    my_solver.add( ForAll([x, y, z], E(x+y, z) == (x*z + y*z)) )
    my_solver.add( ForAll([x, y, z], E(x, y+z) == (y*x + z*x)) )
    
    print(my_solver)
    if my_solver.check() == unsat:
        sys.exit("ERROR: Z3 setup failed.")

    M = my_solver.model()
    print(M, "\n")
    
    Z3Funcs = {'pair': E }
    equations = []
    varMap = {}
    
    for i in verifyEqs:
        varList = varListMap[str(i)]
        #print("<====================>")
        #print("Creating Z3 ints for... ", varList)
        for j in varList:
            if j not in varMap.keys(): varMap[ j ] = Int(j)
        #print("varMap: ", varMap)
        # TODO: need recursive algorithm to model pairings
        #print("Creating Z3 expression for... ", i)
        eqList = retrieveAnds(i)
        eqList.reverse()
        finalExp = ""
        for k in eqList:
            newExp = buildZ3Expression(k, varMap, Z3Funcs)
            #print("Z3 result: ", newExp)
            #print("Z3 simplified: ", M.evaluate(newExp))
            #print("<====================>")
            equations.append( M.evaluate(newExp) )
    
    constraints = []
    constraints_str = "("
    OR = " || "
    equations1 = list(equations)
    #equations2 = list(equations)
    for i in goalCond.keys():
        _var1 = i 
        _var2 = goalCond[i]
        var1, var2 = varMap.get(_var1), varMap.get(_var2)
        #print("constraints: ", var1 != var2)
        constraints.append(var1 != var2)
        constraints_str += str(var1 != var2) + OR
    
    constraints_str = constraints_str[:-len(OR)] + ")"
    equations1.append( constraints_str ) # Mathematica construction
    #equations2.append( Or(constraints) ) # Z3 construction
    
    for i in varMap.keys():
        equations1.append( varMap.get(i) != 0 ) 
        #equations2.append( varMap.get(i) != 0 ) 
    
    #print("subGoal list: ", equations)
    
    if doesPartHoldWithMath(list(varMap.keys()), equations1, expTimeout):
        return True 
    #elif doesPartHoldWithZ3(equations2):
    #    return True 
    
    print("Could NOT confirm that this scheme satisfies the partition property!")
    return False
    