import src.sdlpath, sys, os, random, string, re, importlib
import sdlparser.SDLParser as sdl
from sdlparser.SDLang import *
from src.sdltechniques import *
from z3 import *

def runAutoStrong(sdlFile, config, sdlVerbose=False):
    sdl.parseFile2(sdlFile, sdlVerbose, ignoreCloudSourcing=True)
    global assignInfo
    assignInfo = sdl.getAssignInfo()
    # get config parameters
    msg = config.messageVar
    sigVar = config.signatureVar
    
    # extract property 1 details...
    (name, varInf) = getVarNameEntryFromAssignInfo(assignInfo, sigVar)
    if name != config.signFuncName:
        sys.exit("runAutoStrong: '%s' not in the sign function." % sigVar)
    print("identified signature: ", varInf.getAssignNode())
    listVars = varInf.getListNodesList()
    print("list of possible vars: ", listVars)
    sigma = property1Extract(config.signFuncName, assignInfo, listVars, msg)
    
    property2Extract(config.verifyFuncName, assignInfo, sigma)
    
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
    
    
    # (stmt, types, depList, depListNoExp, infList, infListNoExp) = getVarInfoFuncStmts
    if hasattr(config, "setuPFuncName"):
        setupStmts  = getVarInfoFuncStmts( config.setupFuncName )
    else:
        pass
    
    # extract types for all variables
    varTypes = sdl.getVarTypes().get(TYPES_HEADER)
    for i in config.functionOrder:
        #print("Processing func: ", i)
        varTypes.update( sdl.getVarTypes().get(i) )
    
    #print("Type variables for all: ", varTypes.keys())
    #bsw = BSWTransform(varTypes)
    #bsw.construct(config, sigma)
    
    sys.exit(0)
    #newSDL = None
    #if property2Check(config.verifyFuncName, assignInfo, sigma): # TODO: needs a lot of work
    #    pass # proceed with BSW transform
    #else:
    #    pass # proceed with Bellare-X transform
    
    # writeSDL(newSDL)    
    return None

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
        if msg in varInf.getVarDeps():
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
        else:
            sigma['sigma2'].append(i)
    
    print("<=== Candidate sigma1 and sigma2 ===>")
    print("sigma1 => ", sigma['sigma1'])
    print("sigma2 => ", sigma['sigma2'])
    return sigma

class Decompose:
    def __init__(self, assignInfo, freeVars):
        self.assignInfo = assignInfo
        self.freeVars = freeVars
        self.verbose = False
        
    def visit(self, node, data):
        pass
    
    def visit_attr(self, node, data):
        varName = node.getRefAttribute()
        if varName in self.freeVars: return        
        name, varInf = getVarNameEntryFromAssignInfo(self.assignInfo, varName)
        node2 = varInf.getAssignBaseElemsOnly()
        if self.verbose:
            print("<=====>")
            print("varName: ", varName)
            print("varInf: ", varInf.getAssignBaseElemsOnly())
        if node2 != None and varName != str(node2):
            # make the substitution
            if node == data['parent'].left:
                data['parent'].left = node2
            elif node == data['parent'].right:
                data['parent'].right = node2
        if self.verbose: print("<=====>")

class Transform:
    def __init__(self, generators, varTypes):
        self.generators = generators
        self.varTypes   = varTypes

    def visit(self, node, data):
        pass
    
    def visit_exp(self, node, data):
        # this node is visited last in a post-order traversal
        if Type(node.left) == ops.ATTR and str(node.left) == "1":
            # promote the right node
            addAsChildNodeToParent(data, node.right)

    def visit_mul(self, node, data):
        """convert MUL to ADD"""
        if Type(data['parent']) != ops.EXP:
            node.type = ops.ADD

    def visit_div(self, node, data):
        """convert DIV to SUB"""
        node.type = ops.SUB
    
    def visit_attr(self, node, data):
        varName = str(node)
        if varName in self.generators:
            node.setAttribute("1") # replace generators
        #elif varName in self.varTypes.keys(): # convert group elements in G1 or G2 too g^t
        #    varT = self.varTypes.get(varName)

def property2Extract(verifyFuncName, assignInfo, sigma):
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
    generators = ['g']
    # 1. decompose, then test whether pairings exist?
    freeVars = list(sigma['sigma1'])
    for i in verifyConds:
        if HasPairings(i):
            print("Original: ", i)
            dep = Decompose(assignInfo, freeVars)
            sdl.ASTVisitor(dep).postorder(i)
            print("Decomposed: ", i)
            j = BinaryNode.copy(i)
            j = SimplifyExponents(j)
            print("Converted: ", j)
            
            tf = Transform(generators, None)
            sdl.ASTVisitor(tf).postorder(j)
            print("Final: ", j)
            ga = GetAttrs(dropPounds=True)
            sdl.ASTVisitor(ga).postorder(j)
            vars = ga.getVarList()
            testWithZ3Solver(j, vars)
    # 2. breakdown
    
    return True

def testWithZ3Solver(verifyEqs, varList):    
    I = IntSort()
    E = Function('E', I, I, I)
    x, y, z = Ints('x y z')
    
    my_solver = Then(With('simplify', arith_lhs=True), 'normalize-bounds', 'solve-eqs', 'smt').solver()
    my_solver.add( ForAll([x, y], E(x, y) == x*y) )
    my_solver.add( ForAll([x, y, z], E(x+y, z) == (x*z + y*z)) )
    my_solver.add( ForAll([x, y, z], E(x, y+z) == (y*x + z*x)) )
    
    print(my_solver)
    if my_solver.check() == unsat:
        sys.exit("ERROR: Z3 setup failed.")

    M = my_solver.model()
    print(M, "\n")
    
    varMap = {}
    print("Creating Z3 ints for... ", varList)
    for i in varList:
        varMap[ i ] = Int(i)
    print("varMap: ", varMap)
    # TODO: need recursive algorithm to model pairings
    print("Creating Z3 expression for... ", verifyEqs)
    
    return
    
    
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
    def __init__(self, theVarTypes):
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
        self.newMsgVal = config.messageVar + "pr"
        
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
                if config.messageVar in Stmts[i].getVarDeps():
                    sdl.ASTVisitor( SubstituteVar(config.messageVar, self.newMsgVal) ).preorder( Stmts[i].getAssignNode() ) # modify in place
            
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
                        newLines.append( self.hashVal + " := H(concat{%s, %s, %s}, ZR)" % (self.chK, config.messageVar, self.sigma2str) ) # s1 := H(concat{k, m, r}, ZR) 
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
            if Stmts[i].getAssignVar() == config.messageVar: messageSlice.append(config.messageVar)
        
        sigma2Fixed = False
        lastExpand = False
        for index, i in enumerate(lines):
            assert type(Stmts[i]) == sdl.VarInfo, "Stmts not VarInfo Objects for some reason."
            if lastExpand and len(messageSlice) == 0:
                newLines.append( self.hashVal + " := H(concat{%s, %s, %s}, ZR)" % (self.chK, config.messageVar, self.sigma2str) ) # s1 := H(concat{k, m, r}, ZR) 
                newLines.append( self.newMsgVal + " := %s(%s, %s, %s)"  % (self.chamH, self.chpk, self.hashVal, self.seed) ) # mpr := chamH(chpk, s1, s)
                lastExpand = False
                sigma2Fixed = True

            if sigma2Fixed:
                # 4. add the rest of code and substitute references from m to m'
                if config.messageVar in Stmts[i].getVarDeps():
                    sdl.ASTVisitor( SubstituteVar(config.messageVar, self.newMsgVal) ).preorder( Stmts[i].getAssignNode() ) # modify in place

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
                elif assignVar == config.messageVar:
                    messageSlice.remove(assignVar)
                    newLines.append( str(Stmts[i].getAssignNode()) )                    
                else:
                    newLines.append( str(Stmts[i].getAssignNode()) )

        newLines.append( end )        
        return newLines
