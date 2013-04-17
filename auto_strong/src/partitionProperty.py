import src.sdlpath, sys, os, random, string, re, importlib
import sdlparser.SDLParser as sdl
from sdlparser.SDLang import *
from src.sdltechniques import *
from z3 import *
import subprocess

stringToInt = "stringToInt"

def runAutoStrong(sdlFile, config, sdlVerbose=False):
    sdl.parseFile2(sdlFile, sdlVerbose, ignoreCloudSourcing=True)
    global assignInfo
    assignInfo = sdl.getAssignInfo()
    setting = sdl.assignInfo[sdl.NONE_FUNC_NAME][ALGEBRAIC_SETTING].getAssignNode().getRight().getAttribute()
    assert setting == sdl.SYMMETRIC_SETTING, "AutoStrong requires a symmetric scheme for simplicity."
    
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
    print("identified signature: ", varInf.getAssignNode())
    listVars = varInf.getListNodesList()
    print("list of possible vars: ", listVars)
    sigma = property1Extract(config.signFuncName, assignInfo, listVars, msgVar)
    
    if property2Extract(config.verifyFuncName, assignInfo, baseGen, generators, sigma):
        print("Applying BSW transformation...")
        # extract types for all variables
        varTypes = sdl.getVarTypes().get(TYPES_HEADER)
        for i in config.functionOrder:
            #print("Processing func: ", i)
            varTypes.update( sdl.getVarTypes().get(i) )
        
        print("Type variables for all: ", varTypes.keys())
        #bsw = BSWTransform(varTypes, msgVar, msgVarList)
        #bsw.construct(config, sigma)
        pass
    else:
        #Bellare-Shoup transformation
        pass
#    print("Program Slice for sigma1: ", sigma['sigma1'])
#    for i in sigma['sigma1']:
#        sliceListSigma1 = []
#        getProgramSlice(config.signFuncName, assignInfo, i, sliceListSigma1)
#        sliceListSigma1.sort()
#        print("sliceList: ", sliceListSigma1)
#    print("")    
#    print("Program Slice for sigma2: ", sigma['sigma2'])
#    for i in sigma['sigma2']:
#        sliceListSigma2 = []
#        getProgramSlice(config.signFuncName, assignInfo, i, sliceListSigma2)
#        sliceListSigma2.sort()
#        print("sliceList: ", sliceListSigma2)
            
    sys.exit(0)
    #newSDL = None
    #if property2Check(config.verifyFuncName, assignInfo, sigma): # TODO: needs a lot of work
    #    pass # proceed with BSW transform
    #else:
    #    pass # proceed with Bellare-X transform
    
    # writeSDL(newSDL)    
    return None
        
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
    assert type(msgVar) == str, "messageVar should be a str."
    lines = list(Stmt.keys())
    lines.sort()
    msgVarList = []
    for i in lines:
        assert type(Stmt[i]) == sdl.VarInfo, "traceMessage: not a VarInfo object."
        if Type(Stmt[i].getAssignNode()) == ops.EQ and Stmt[i].getAssignVar() not in [inputKeyword, outputKeyword]: # assignment node
            if msgVar in Stmt[i].getVarDeps() and Stmt[i].getIsUsedInHashCalc():
                # expecting a hash call to a specified group type                
                if Stmt[i].getAssignVar() not in msgVarList: msgVarList.append( Stmt[i].getAssignVar() )
            elif msgVar in Stmt[i].getVarDeps() and Type(Stmt[i].getAssignNode().getRight()) == ops.FUNC:
                # expecting stringToInt
                if stringToInt == Stmt[i].getAssignNode().getRight().attr:
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
    print("sigma1 => ", sigma['sigma1'])
    print("sigma2 => ", sigma['sigma2'])
    
    if len(sigma['sigma1']) == 0: sys.exit("Signature scheme does not satisfy partitioning property. Property 1 check failed!")
    return sigma

def deleteThisVar(varName, node):
    dv = DeleteVar(varName)
    print("Before Deletion: ", node)    
    sdl.ASTVisitor(dv).preorder( node )
    print("After Deletion: ", node)
    return

"""
Step 1 for property 2 check. Decompose each verification condition to base elements.
"""
class Decompose:
    def __init__(self, assignInfo, baseGen, freeVars):
        self.assignInfo = assignInfo
        self.baseGen    = baseGen
        self.freeVars = freeVars
        self.verbose = True
        
    def visit(self, node, data):
        pass
            
    def visit_attr(self, node, data):
        varName = node.getRefAttribute()
        if varName in self.freeVars: return
        name, varInf = getVarNameEntryFromAssignInfo(self.assignInfo, varName)
        if varInf == None: return
        node2 = varInf.getAssignBaseElemsOnly()
        if node2 == None: return
        varDeps = varInf.getVarDeps()
#        if varName in self.generators:
#            node2 = self.generatorMap[varName] # BinaryNode(ops.EXP, BinaryNode(self.baseGen), BinaryNode(varName + "E"))
        if self.verbose:
            print("<=====>")
            print("varName: ", varName)
            print("varInf: ", node2) #varInf.getAssignBaseElemsOnly())
            print("varDeps: ", varDeps)
        if varName in varDeps:
            print("isIterator: ", varName in varDeps)
            deleteThisVar(varName, node2)
            #dv = DeleteVar(varName)
            #sdl.ASTVisitor(dv).preorder( node2 )
            #print("Result: ", node2)
        else:
            for i in varDeps:
                # see if any variables need to be removed
                name, varInf2 = getVarNameEntryFromAssignInfo(self.assignInfo, i)
                if varInf2 != None and i in varInf2.getVarDeps(): print("\t Delete ", i, ":", varInf2.getVarDeps()); deleteThisVar(i, node2)

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
        pass
    
    def visit_exp(self, node, data):
        # this node is visited last in a post-order traversal
        if Type(node.left) == ops.ATTR and str(node.left) == "1":
            # promote the right node
            addAsChildNodeToParent(data, node.right)
    
    def visit_hash(self, node, data):
        print("Transforming...: ", node)
        if str(node.right) == 'G1':
            new_hash = BinaryNode(ops.EXP, BinaryNode("1"), BinaryNode.copy(node.left))
            BinaryNode.setNodeAs(node, new_hash)
            print("Result: ", node)
            self.reapplyTransform = True
        else:
            print("Transform class: need to handle other hash cases: ", node.right)
    
    def visit_mul(self, node, data):
        if Type(node.left) == Type(node.right) and Type(node.left) == ops.PAIR:
            node.type = ops.ADD

    def visit_div(self, node, data):
        if Type(node.left) == Type(node.right) and Type(node.left) == ops.PAIR:
            node.type = ops.SUB
    
    def visit_attr(self, node, data):
        varName = str(node)
        if varName == self.baseGen:
            node.setAttribute("1") # replace generators
        #elif varName in self.generators: # one of the other generators?            
        #elif varName in self.varTypes.keys(): # convert group elements in G1 or G2 too g^t
        #    varT = self.varTypes.get(varName)

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
    
    # TODO: extract generator from setup routine
    #baseGen = 'g'
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
    
    testCorrectWithZ3(verifyThese, varListMap2)
    print("\nStep 3: test partition using Z3.")
    #sys.exit(0)
    return testPartitionWithZ3(newVerifyConds, goalCond, varListMap)

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
        if not varName.isdigit():
            if "-" in varName: 
                varName = varName.strip("-")
                return -1 * varMap.get(varName)
            return varMap.get(varName)
        else:
            return int(varName)
    else:
        print("NodeType unsupported: ", Type(node))
        return None

def doesPartitionHold(subGoals):
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
        newExp = buildZ3Expression(i, varMap, Z3Funcs)
        print("Z3 result: ", newExp)
        print("Z3 simplified: ", M.evaluate(newExp))
        print("<====================>")
        constraints = []
        for j in varMap.keys():
            constraints.append( varMap.get(j) ) # > 1 ) # constraint that values are non-zero        

        simplify_cmd = ["src/runMath", "Simplify[" + str(M.evaluate(newExp)).replace("\n", " ") + "]"]
        print("Verify with Mathematica:  ", simplify_cmd ) # , And(constraints) )
        p = subprocess.Popen(simplify_cmd, stdout=subprocess.PIPE)
        preprocessed, _ = p.communicate()
        result = preprocessed.strip()
        print("Mathematica output: ", result)
        if eval(result) == True: 
            continue
        else:
            return result
    
    return True

def testPartitionWithZ3(verifyEqs, goalCond, varListMap):    
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
        print("<====================>")
        print("Creating Z3 ints for... ", varList)
        for j in varList:
            if j not in varMap.keys(): varMap[ j ] = Int(j)
        print("varMap: ", varMap)
        # TODO: need recursive algorithm to model pairings
        print("Creating Z3 expression for... ", i)
        newExp = buildZ3Expression(i, varMap, Z3Funcs)
        print("Z3 result: ", newExp)
        print("Z3 simplified: ", M.evaluate(newExp))
        print("<====================>")
        equations.append( M.evaluate(newExp) )
    
    constraints = []
    for i in goalCond.keys():
        _var1 = i 
        _var2 = goalCond[i]
        var1, var2 = varMap.get(_var1), varMap.get(_var2)
        print("constraints: ", var1 != var2)
        constraints.append(var1 != var2)
    equations.append( Or(constraints) )
    
    for i in varMap.keys():
        equations.append( varMap.get(i) > 1 ) # > 1 ) # constraint that values are non-zero            
    
    print("subGoal list: ", equations)
    if doesPartitionHold(equations):
        return True # safe route: can find 
    
    print("Does NOT satisfy partition property!")
    return False
    
    
ch = "ch"

def print_sdl(verbose, *args):
    if verbose:
        print("<===== new SDL =====>")    
        for block in args:
            for i in block:
                print(i)
            print("\n\n")
        print("<===== new SDL =====>")
    return


class BSWTransform:
    def __init__(self, theVarTypes, messageVar, messageVarList):
        self.messageVar     = messageVar
        self.messageVarList = messageVarList 
        self.listToCRHash = []
        self.chamHashFunc = []
        assert type(theVarTypes) == dict, "invalid type for varTypes"
        self.varTypes = theVarTypes
        self.varKeys = list(self.varTypes.keys())
        
    def construct(self, config, sigma):
        self.__chooseVariables(config)
        
        funcVisited = []
        chamHashLines = self.__constructChamHash()
        key, setupDict  = self.modifySetup(config, funcVisited)
        signLines   = self.modifySign(config, sigma, funcVisited)
        verifyLines = self.modifyVerify(config, sigma, funcVisited)
        remFuncs = list(set(config.functionOrder).difference(funcVisited))
        print_sdl(True, chamHashLines, setupDict[key], signLines, verifyLines)
        print("Functions to copy: ", remFuncs)
        
    def __chooseVariables(self, config):
        suffix = "New"
        self.chamH = "chamH"
        self.chK, self.ch0, self.ch1, self.chpk = ch+"K", ch+"0", ch+"1", ch+"pk"
        self.t0, self.t1 = "t0", "t1"
        self.chZr, self.chVal = ch+"Zr", ch+"Val"
        self.chPrefix = "1"
        seedVar = "s"
        self.seed = seedVar + "0"
        self.hashVal = seedVar + "1"
        self.newMsgVal = self.messageVar + "pr"
        
        # search for each one
        sdlVars = [self.chK, self.ch0, self.ch1, self.chpk, self.t0, self.t1, self.chZr, self.chVal, self.seed, self.hashVal, self.newMsgVal]
        
        for i,j in enumerate(sdlVars):
            if j in self.varKeys:
               setattr(self, j, j+suffix)
    
    def __constructChamHash(self):
        sdlLines = []
        sdlLines.append( "BEGIN :: func:%s" % self.chamH )
        sdlLines.append( "input := list{%s, %s, %s}" % (self.chpk, self.t0, self.t1) )
        sdlLines.append( "%s := expand{%s, %s}" % (self.chpk, self.ch0, self.ch1) )
        sdlLines.append( "%s := (%s ^ %s) * (%s ^ %s)" % (self.chVal, self.ch0, self.t0, self.ch1, self.t1) )
        if True: # type check message 
            sdlLines.append( "%s := H(concat{%s, %s}, ZR)" % (self.chZr, self.chPrefix, self.chVal) )
            sdlLines.append( "output := %s" % self.chZr ) # if ZR output required
        else:
            sdlLines.append( "output := %s" % self.chVal ) # if G1 output required
        sdlLines.append( "END :: func:%s" % self.chamH )
        return sdlLines
    
    def modifySetup(self, config, funcVisited):
        # append to Setup or Keygen       
        # add chpk to output list, and chK to pk 
        (name, varInf) = getVarNameEntryFromAssignInfo(assignInfo, config.keygenPubVar)        
        funcVisited.append(name)
        print("Fount public key in: ", name)
        # (stmt, types, depList, depListNoExp, infList, infListNoExp) = getVarInfoFuncStmts
        if name == "setup": # hasattr(config, "setupFuncName"):
            setupConfig  = sdl.getVarInfoFuncStmts( config.setupFuncName )
            Stmts = setupConfig[0]
            begin = "BEGIN :: func:" + config.setupFuncName
            end   = "END :: func:" + config.setupFuncName
        elif name == "keygen": # and hasattr(config, "keygenFuncName"):
            keygenConfig = sdl.getVarInfoFuncStmts( config.keygenFuncName )
            Stmts = keygenConfig[0]
            begin = "BEGIN :: func:" + config.keygenFuncName
            end   = "END :: func:" + config.keygenFuncName            
        
        lines = list(Stmts.keys())
        lines.sort()
        newLines = [begin]
        
        for index, i in enumerate(lines):
            assert type(Stmts[i]) == sdl.VarInfo, "transformFunction: blockStmts must be VarInfo Objects."
            if Stmts[i].getIsExpandNode() or Stmts[i].getIsList():
                if str(Stmts[i].getAssignVar()) == config.keygenPubVar:
                    Stmts[i].getAssignNode().getRight().listNodes.insert(0, self.chK)
                    print("new list: ", Stmts[i].getAssignNode().getRight())
                    newLines.append( self.chK + " := random(ZR)" )
                    newLines.append( self.ch0 + " := random(G1)" )
                    newLines.append( self.ch1 + " := random(G1)" )
                    newLines.append( self.chpk + " := list{" + self.ch0 + ", " + self.ch1 + "}" )
                elif str(Stmts[i].getAssignVar()) == outputKeyword:
                    Stmts[i].getAssignNode().getRight().listNodes.append(self.chpk)
                                        
                newLines.append( str(Stmts[i].getAssignNode()) )
            elif Stmts[i].getIsForLoopBegin():
                if Stmts[i].getIsForType(): newLines.append("\n" + START_TOKEN + " " + BLOCK_SEP + ' for')
                elif Stmts[i].getIsForAllType(): newLines.append("\n" + START_TOKEN + " " + BLOCK_SEP + ' forall')
                newLines.append(str(Stmts[i].getAssignNode()))
            elif Stmts[i].getIsForLoopEnd():
                newLines.append(str(Stmts[i].getAssignNode()))
            
            elif Stmts[i].getIsIfElseBegin():
                newLines.append("\n" + START_TOKEN + " " + BLOCK_SEP + ' if')
                newLines.append( str(Stmts[i].getAssignNode()) )
            else:
                newLines.append(str(Stmts[i].getAssignNode()))
        
        newLines.append( end )
        return name, { name : newLines } # key, dict[key] = value
    
    def modifySign(self, config, sigma, funcVisited):
        # Steps to create the strong 'sign' algorithm 
        # 1. select a new random variable, s (seed)
        funcVisited.append(config.signFuncName)                
        signConfig = sdl.getVarInfoFuncStmts( config.signFuncName )
        Stmts = signConfig[0]
        begin = "BEGIN :: func:" + config.signFuncName
        end   = "END :: func:" + config.signFuncName            

        # 2. obtain program slice of \sigma_2 variables? and include
        lines = list(Stmts.keys())
        lines.sort()
        newLines = [begin]
        sigma2 = list(sigma['sigma2'])
        sigmaStr = ""
        for i in sigma['sigma2']:
            sigmaStr += i + ", "
        sigmaStr = sigmaStr[:-2]
        self.sigma2str = sigmaStr

        sigma2Fixed = False
        for index, i in enumerate(lines):
            assert type(Stmts[i]) == sdl.VarInfo, "transformFunction: blockStmts must be VarInfo Objects."
            if sigma2Fixed:
                # 4. add the rest of code and substitute references from m to m'
                if self.messageVar in Stmts[i].getVarDeps():
                    sdl.ASTVisitor( SubstituteVar(self.messageVar, self.newMsgVal) ).preorder( Stmts[i].getAssignNode() ) # modify in place
            
            if Stmts[i].getIsExpandNode():
                if str(Stmts[i].getAssignVar()) == config.keygenPubVar:
                    Stmts[i].getAssignNode().getRight().listNodes.insert(0, self.chK)
                    print("new list: ", Stmts[i].getAssignNode().getRight())
                    newLines.append( str(Stmts[i].getAssignNode()) ) 
                else:
                    newLines.append( str(Stmts[i].getAssignNode()) )
            elif Stmts[i].getIsForLoopBegin():
                if Stmts[i].getIsForType(): newLines.append("\n" + START_TOKEN + " " + BLOCK_SEP + ' for')
                elif Stmts[i].getIsForAllType(): newLines.append("\n" + START_TOKEN + " " + BLOCK_SEP + ' forall')
                newLines.append(str(Stmts[i].getAssignNode()))
            elif Stmts[i].getIsIfElseBegin():
                newLines.append("\n" + START_TOKEN + " " + BLOCK_SEP + ' if')
                newLines.append( str(Stmts[i].getAssignNode()) )
            else:
                assignVar = str(Stmts[i].getAssignVar())
                if assignVar in sigma2:                   
                    newLines.append( str(Stmts[i].getAssignNode()) )
                    # 3. add statement for computing m' using original m and \sigma_2
                    sigma2.remove(assignVar)
                    if len(sigma2) == 0:
                        newLines.append( self.seed + " := random(ZR)" )
                        newLines.append( self.hashVal + " := H(concat{%s, %s, %s}, ZR)" % (self.chK, self.messageVar, self.sigma2str) ) # s1 := H(concat{k, m, r}, ZR) 
                        newLines.append( self.newMsgVal + " := %s(%s, %s, %s)"  % (self.chamH, self.chpk, self.hashVal, self.seed) ) # mpr := chamH(chpk, s1, s)
                    sigma2Fixed = True
                elif assignVar == config.signatureVar:
                    # 5. add seed to output as part of signature
                    if Stmts[i].getIsList():
                        if Stmts[i].getAssignNode().getRight() != None: Stmts[i].getAssignNode().getRight().listNodes.append( self.seed )
                        newLines.append( str(Stmts[i].getAssignNode()) )
                    else:
                        print("TODO: ", assignVar, " has unexpected structure.")
                elif assignVar == inputKeyword:
                    if Stmts[i].getAssignNode().getRight() != None: Stmts[i].getAssignNode().getRight().listNodes.insert(0, self.chpk)
                    newLines.append( str(Stmts[i].getAssignNode()) )
                else:
                    newLines.append( str(Stmts[i].getAssignNode()) )

        newLines.append( end )        
        return newLines
    
    def modifyVerify(self, config, sigma, funcVisited):
        # Steps to create the strong 'verify' algorithm 
        # 1. add the statements for 
        funcVisited.append(config.verifyFuncName)
        verifyConfig = sdl.getVarInfoFuncStmts( config.verifyFuncName )
        Stmts = verifyConfig[0]
        begin = "BEGIN :: func:" + config.verifyFuncName
        end   = "END :: func:" + config.verifyFuncName          

        # 2. obtain program slice of \sigma_2 variables? and include
        lines = list(Stmts.keys())
        lines.sort()
        newLines = [begin]
        messageSlice = []
        expandCount = 0
        for index, i in enumerate(lines):
            assert type(Stmts[i]) == sdl.VarInfo, "Stmts not VarInfo Objects for some reason."
            if Stmts[i].getIsExpandNode(): expandCount += 1
            if Stmts[i].getAssignVar() == self.messageVar: messageSlice.append(self.messageVar)
        
        sigma2Fixed = False
        lastExpand = False
        for index, i in enumerate(lines):
            assert type(Stmts[i]) == sdl.VarInfo, "Stmts not VarInfo Objects for some reason."
            if lastExpand and len(messageSlice) == 0:
                newLines.append( self.hashVal + " := H(concat{%s, %s, %s}, ZR)" % (self.chK, self.messageVar, self.sigma2str) ) # s1 := H(concat{k, m, r}, ZR) 
                newLines.append( self.newMsgVal + " := %s(%s, %s, %s)"  % (self.chamH, self.chpk, self.hashVal, self.seed) ) # mpr := chamH(chpk, s1, s)
                lastExpand = False
                sigma2Fixed = True

            if sigma2Fixed:
                # 4. add the rest of code and substitute references from m to m'
                if self.messageVar in Stmts[i].getVarDeps():
                    sdl.ASTVisitor( SubstituteVar(self.messageVar, self.newMsgVal) ).preorder( Stmts[i].getAssignNode() ) # modify in place

            if Stmts[i].getIsExpandNode():
                expandCount -= 1
                if expandCount == 0: lastExpand = True
                if str(Stmts[i].getAssignVar()) == config.keygenPubVar:
                    Stmts[i].getAssignNode().getRight().listNodes.insert(0, self.chK)
                    print("new list: ", Stmts[i].getAssignNode().getRight())
                elif str(Stmts[i].getAssignVar()) == config.signatureVar:
                    Stmts[i].getAssignNode().getRight().listNodes.append( self.seed )                                        
                newLines.append( str(Stmts[i].getAssignNode()) )
            elif Stmts[i].getIsForLoopBegin():
                if Stmts[i].getIsForType(): newLines.append("\n" + START_TOKEN + " " + BLOCK_SEP + ' for')
                elif Stmts[i].getIsForAllType(): newLines.append("\n" + START_TOKEN + " " + BLOCK_SEP + ' forall')
                newLines.append(str(Stmts[i].getAssignNode()))
            elif Stmts[i].getIsIfElseBegin():
                newLines.append("\n" + START_TOKEN + " " + BLOCK_SEP + ' if')
                newLines.append( str(Stmts[i].getAssignNode()) )
            else:
                assignVar = str(Stmts[i].getAssignVar())
                if assignVar == config.signatureVar:
                    # 5. add seed to output as part of signature
                    if Stmts[i].getIsExpandNode():
                        if Stmts[i].getAssignNode().getRight() != None: Stmts[i].getAssignNode().getRight().listNodes.append( self.seed )
                        newLines.append( str(Stmts[i].getAssignNode()) )
                    else:
                        print("TODO: ", assignVar, " has unexpected structure.")
                elif assignVar == inputKeyword:
                    if Stmts[i].getAssignNode().getRight() != None: Stmts[i].getAssignNode().getRight().listNodes.insert(0, self.chpk)
                    # check if signature variables are contained inside the list
                    sigLen = len(set( Stmts[i].getAssignNode().getRight().listNodes ).intersection( sigma['sigma1'] )) + len(set( Stmts[i].getAssignNode().getRight().listNodes ).intersection( sigma['sigma2'] ))
                    if sigLen > 0: Stmts[i].getAssignNode().getRight().listNodes.append( self.seed )
                    newLines.append( str(Stmts[i].getAssignNode()) )
                elif assignVar == self.messageVar:
                    messageSlice.remove(assignVar)
                    newLines.append( str(Stmts[i].getAssignNode()) )                    
                else:
                    newLines.append( str(Stmts[i].getAssignNode()) )

        newLines.append( end )        
        return newLines
