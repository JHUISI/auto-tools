import src.sdlpath, sys, os, copy, string, re, importlib
import sdlparser.SDLParser as sdl
from sdlparser.SDLang import *
from src.outsrctechniques import SubstituteVar, SubstitutePairings, SplitPairings, HasPairings, CountOfPairings, MaintainOrder, PairInstanceFinderImproved, TestForMultipleEq, GetAttributeVars, GetEquqlityNodes, CountExpOp, CountMulOp, DelAnyVarInList
from src.solver import *

assignInfo = None
SHORT_SECKEYS = "secret_keys" # for
SHORT_PUBKEYS = "public_keys"
SHORT_CIPHERTEXT = "ciphertext" # in case, an encryption scheme
SHORT_SIGNATURE  = "signature" # in case, a sig algorithm
SHORT_FORALL = "both"
SHORT_DEFAULT = "all"
SHORT_OPTIONS = [SHORT_SECKEYS, SHORT_PUBKEYS, SHORT_CIPHERTEXT, SHORT_SIGNATURE, SHORT_FORALL]
minOp = "operation"
PKENC = "PKENC" # encryption
PKSIG = "PKSIG" # signatures
functionOrder = "functionOrder"
curveID = "curve"

G1Prefix = "G1"
G2Prefix = "G2"
Gtypes = [G1Prefix, G2Prefix]
length = 5 # length of temporary file
oldListTypeRefs = {}
newListTypeRefs = {}
loc = "src"

class GetPairingVariables:
    def __init__(self, list1, list2):
        assert type(list1) == type(list2) and type(list1) == list, "GetPairingVariables: invalid input type"
        self.listLHS = list1
        self.listRHS = list2
    
    def retrieveNode(self, node):
        if Type(node) == ops.EXP:
            return node.left
        #elif Type(node) == ops.MUL:
        #    pass
        return
        
    def visit(self, node, data):
        pass
    
    def visit_pair(self, node, data):
        if str(node.left.getRefAttribute()) == str(node.right.getRefAttribute()):
            return # skip
        
        if Type(node.left) == ops.ATTR and Type(node.right) == ops.ATTR:
            self.listLHS.append(str(node.left.getRefAttribute()))
            self.listRHS.append(str(node.right.getRefAttribute()))
        elif Type(node.left) == ops.ATTR and Type(node.right) != ops.ATTR:
            self.listLHS.append(str(node.left.getRefAttribute()))
            self.listRHS.append(str(self.retrieveNode(node.right)))
        elif Type(node.left) != ops.ATTR and Type(node.right) == ops.ATTR:
            self.listLHS.append(str(self.retrieveNode(node.left)))
            self.listRHS.append(str(node.right.getRefAttribute()))
        elif Type(node.left) != ops.ATTR and Type(node.right) != ops.ATTR:
            self.listLHS.append(str(self.retrieveNode(node.left)))
            self.listRHS.append(str(self.retrieveNode(node.right)))
        else:
            pass            

class transformXOR:
    def __init__(self, fixedValues):
        self.groundTruth = fixedValues
        self.varMap = {}
        self.varsList = [] # records variable instances?
        self.xorList = [] # records tuple
        self.alphabet = list(string.ascii_lowercase)
        self.count = 0

    def __getNextVar(self):
        suffixCount = int(self.count / len(self.alphabet))
        if suffixCount > 0: suffix = str(suffixCount)
        else: suffix = '0'
        
        count = self.count % len(self.alphabet)
        a = self.alphabet[ count ] + suffix
        self.count += 1
        return a
    
    def visit(self, node, data):
        return
    
    def visit_xor(self, node, data):
        var1 = str(node.left)
        var2 = str(node.right)
        if var1 not in self.varMap.keys():
            alpha_x = self.__getNextVar()
        else:
            alpha_x = self.varMap[ var1 ]
            
        if var2 not in self.varMap.keys():
            alpha_y = self.__getNextVar()
        else:
            alpha_y = self.varMap[ var2 ]
        
        self.varMap[ var1 ] = alpha_x
        self.varMap[ var2 ] = alpha_y
        
        self.xorList.append( (alpha_x, alpha_y) )
        return
        
    def getVarMap(self):
        return self.varMap
    
    def getVariables(self):
        keys = list(set(self.varMap.values()))
        keys.sort()
        return keys
    
    def getClauses(self):
        return self.xorList        


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
def transformFunction(entireSDL, funcName, blockStmts, info, noChangeList, startLines={}):
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
            if blockStmts[i].getIsForType(): newLines.append(parser.parse("BEGIN :: for\n")) # "\n" + START_TOKEN + " " + BLOCK_SEP + ' for')
            elif blockStmts[i].getIsForAllType(): newLines.append(parser.parse("BEGIN :: forall\n"))  # "\n" + START_TOKEN + " " + BLOCK_SEP + ' forall')
            newLines.append(blockStmts[i].getAssignNode())
        elif blockStmts[i].getIsForLoopEnd():
            newLines.append(blockStmts[i].getAssignNode())
        
        elif blockStmts[i].getIsIfElseBegin():
            newLines.append(parser.parse("BEGIN :: if\n")) # "\n" + START_TOKEN + " " + BLOCK_SEP + ' if')
            assign = blockStmts[i].getAssignNode()
            if info['verbose']: print(i, ":", assign, end="")           
            handleVarInfo(newLines, assign, blockStmts[i], info, noChangeList)
        
        elif blockStmts[i].getIsIfElseEnd():
            newLines.append(blockStmts[i].getAssignNode()) 
        
        elif blockStmts[i].getIsElseBegin():
            newLines.append(blockStmts[i].getAssignNode())
        
        else:
            assign = blockStmts[i].getAssignNode()
            if info['verbose']: print(i, ":", assign, end="")
            handleVarInfo(newLines, assign, blockStmts[i], info, noChangeList, startLines)

        if info['verbose']: print("")
    newLines.append(end)
    return newLines

"""theType either types.G1 or types.G2"""
def updateForIfConditional(node, assignVar, varInfo, info, theType, noChangeList):
    new_node2 = BinaryNode.copy(node)
        
    if assignVar not in noChangeList: new_assignVar = assignVar + G1Prefix
    else: new_assignVar = str(assignVar)

    sdl.ASTVisitor( SubstituteVar(assignVar, new_assignVar) ).preorder( new_node2 )
    info['generatorMapG1'][assignVar] = new_assignVar
    
    # in case of init() calls...
    sdl.ASTVisitor( SubstituteVar('', str(theType), initChange=True) ).preorder( new_node2 )
    return new_node2

def handleVarInfo(newLines, assign, blockStmt, info, noChangeList, startLines={}):
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
                if info['verbose']: print(" :-> not a generator, so add to newLines.", end=" ")
                #newLine = str(assign) # unmodified
                newLines.append(assign) # unmodified
                return True
            else:
                if info['verbose']: print(" :-> what type ?= ", info['varTypes'].get(assignVar).getType(), end=" ")
                if info['varTypes'].get(assignVar).getType() == types.G1:
                    pass # figure out what to do here
        if assignVar == outputKeyword:
            vardeps = blockStmt.getVarDepsNoExponents()
            if len(set(blockStmt.getVarDepsNoExponents()).intersection(info['generators'])) > 0:
                if Type(assign.right) == ops.LIST:
                    newLine = updateForLists(blockStmt, assignVar, info)                    
                    newLines.append( newLine )
                    return True
                elif Type(assign.right) == ops.ATTR:
                    assign.right = BinaryNode(ops.LIST)
                    assign.right.listNodes = list(vardeps)
                    newLine = updateForLists(blockStmt, assignVar, info)
                    newLines.append( newLine )
                    return True
                
        if assignVarOccursInBoth(assignVar, info):
            if info['verbose']: print(" :-> split computation in G1 & G2:", blockStmt.getVarDepsNoExponents(), end=" ")
            newLine = updateAllForBoth(assign, assignVar, blockStmt, info, True, noChangeList)
        elif assignVarOccursInG1(assignVar, info):
            if info['verbose']: print(" :-> just in G1:", blockStmt.getVarDepsNoExponents(), end=" ")
            noChangeList.append(str(assignVar))
            newLine = updateAllForG1(assign, assignVar, blockStmt, info, False, noChangeList)
        elif assignVarOccursInG2(assignVar, info):
            if info['verbose']: print(" :-> just in G2:", blockStmt.getVarDepsNoExponents(), end=" ")
            noChangeList.append(str(assignVar))
            newLine = updateAllForG2(assign, assignVar, blockStmt, info, False, noChangeList)
        elif blockStmt.getHasPairings(): # in GT so don't need to touch assignVar
            if info['verbose']: print(" :-> update pairing.", end=" ")
            noChangeList.append(str(assignVar))
            newLine = updateForPairing(blockStmt, info, noChangeList)
        elif blockStmt.getIsList() or blockStmt.getIsExpandNode():
            if info['verbose']: print(" :-> updating list...", end=" ")
            newLine = updateForLists(blockStmt, assignVar, info)
        elif len(set(blockStmt.getVarDepsNoExponents()).intersection(info['generators'])) > 0:
            if info['verbose']: print(" :-> update assign iff lhs not a pairing input AND not changed by traceback.", end=" ")
            if assignVar not in info['pairing'][G1Prefix] and assignVar not in info['pairing'][G2Prefix]:
                noChangeList.append(str(assignVar))
                info['G1'] = info['G1'].union( assignVar )
                newLine = updateAllForG1(assign, assignVar, blockStmt, info, False, noChangeList)
                if info['verbose']: print(":-> var deps = ", blockStmt.getVarDepsNoExponents())
        else:
            newLine = assign
        # add to newLines
        if type(newLine) == list:
            newLines.extend(newLine)
        elif newLine != None:
            #if newLine not in newLines:
            newLines.append(newLine)
        return True
    elif Type(assign) == ops.IF:
#        print("JAA type: ", Type(assign), blockStmt.getVarDepsNoExponents())
        # TODO: there might be some missing cases in updateForIfConditional. Revise as appropriate.
        assignVars = blockStmt.getVarDepsNoExponents()
        assign2 = assign
        if not HasPairings(assign):
            for assignVar in assignVars:
                if assignVarOccursInG1(assignVar, info):
                    if info['verbose']: print(" :-> just in G1:", assignVar, end="")
                    assign2 = updateForIfConditional(assign2, assignVar, blockStmt, info, types.G1, noChangeList)
                elif assignVarOccursInG2(assignVar, info):
                    if info['verbose']: print(" :-> just in G2:", assignVar, end="")
                    assign2 = updateForIfConditional(assign2, assignVar, blockStmt, info, types.G2, noChangeList)
            #print("TODO: Not a good sign. how do we handle this case for ", assignVar, "in", assign)
        else: # pairing case
            assign2 = updateForPairing(blockStmt, info, noChangeList)
            
        if str(assign2) == str(assign):
            newLines.append(assign)
        else:
            newLines.append(assign2)
    else:
        print("Unrecognized type: ", Type(assign))
    return False

def instantiateZ3Solver(shortOpt, timeOpt, variables, clauses, hardConstraints, constraints, bothConstraints, countOpt, minOptions):
    
    options = {variableKeyword:variables, clauseKeyword:clauses, constraintKeyword:constraints}
    options[verboseKeyword] = True
         
    # uncomment for SAT version of AutoGroup
    #(result1, satisfiable) = solveUsingSAT(options)    
    #print("Satisfiable: ", satisfiable)
    #print("Result: ", result1)
    options[curveKeyword] = False # TODO: check option from user (not ready for prime-time)
    
#    options[searchKeyword] = True 
    options[countKeyword] = countOpt # set iff min ops like exp or mul are selected
    options[minKeyword] = minOptions # (minOps, specificOp)
    options[hardConstKeyword] = hardConstraints
    options[bothKeyword] = bothConstraints
    
    (result, satisfiable) = solveUsingSMT(options, shortOpt, timeOpt)
    return (satisfiable, result)


#def instantiateSolver(variables, clauses, constraints, mofnConstraints, bothConstraints):
#    print("variables = ", variables) # txor.getVariables())
#    outputVariables = variableKeyword + " = " + str(variables) + "\n"
#    print("clauses = ", clauses)
#    outputClauses   = clauseKeyword + " = " + str(clauses) + "\n"
#    print("constraints = ", constraints)
#    outputConstraints = constraintKeyword + " = " + str(constraints) + "\n"
#    outputMofN = ""
#    if mofnConstraints != None:
#        print("mofn = ", mofnConstraints)
#        outputMofN += mofnKeyword + " = " + str(mofnConstraints) + "\n"
#    
#    # options of the user wants to minimize both
#    keys = list(bothConstraints.keys())
#    outputForBoth = ""
#    if len(keys) > 0:
#        outputForBoth = "searchBoth = True\n"
#        for k in keys:
#            outputForBoth += str(k) + " = " + str(bothConstraints[k]) + "\n"
#        print(outputForBoth)
#    # get random file
#    name = ""
#    for i in range(length):
#        name += random.choice(string.ascii_lowercase + string.digits)
#    newName = loc + "." + name
#    name += ".py"
#    fileTarget = loc + "/" + name
#    f = open(fileTarget, 'w')
#    f.write(outputVariables)
#    f.write(outputClauses)
#    if outputForBoth != "": f.write(outputForBoth)
#    if outputMofN != "":    f.write(outputMofN)
#    f.write(outputConstraints)
#    f.close()
#    
#    os.system("/opt/local/bin/python2.7 %s/z3solver.py %s/%s" % (loc, loc, name))
#    results = importlib.import_module(newName) #__import__(newName)
#    if(not results.satisfiable):
#        os.system("rm -f " + fileTarget + "*")
#        print("SAT solver could not find a suitable solution. Change configuration and try again!")
#        return results.satisfiable, None
#    
#    print(results.resultDictionary)
#    os.system("rm -f " + fileTarget + "*")
#    return results.satisfiable, results.resultDictionary

def getAssignmentForName(var, varTypes, estimate=False):
    global assignInfo
    dataTypes = {}
    (funcName, varInfo) = getVarNameEntryFromAssignInfo(assignInfo, var)
    if funcName != None:
        funcStmts = sdl.getVarInfoFuncStmts( funcName )
        Stmts = funcStmts[0]
        StmtTypes = funcStmts[1]
    resultVars = []
    if varInfo.getIsList():
        assignNode = varInfo.getAssignNode()
        varList = assignNode.getRight().listNodes
        #print("assignNode: ", assignNode)
        #print("full varList: ", varList)
        resultVars = []
        for i in varList:
            varType = varTypes.get(i)
            theType = varType.getType()
            if theType == types.G1:
                # JAA: commented out for benchmarking                
                #if not estimate: print(i, ":", theType)
                resultVars.append(i)

            if theType in [types.ZR, types.G1, types.G2, types.GT]: dataTypes[ i ] = str(theType)
            
            if theType in [types.list, types.listG1]:
                #print("Find all refs: ", i) # JAA: commented out for benchmarking
                for j,k in Stmts.items():
                    if Type(k.getAssignNode()) == ops.EQ:
                        kvar = k.getAssignVar()
                        if i in kvar and StmtTypes.get(kvar).getType() == types.G1:
                            if kvar not in resultVars: resultVars.append(str(kvar))
                            if kvar not in dataTypes: dataTypes[ i ] = str(StmtTypes.get(kvar).getType())

    # JAA: commented out for benchmarking                            
    #if not estimate: print("varList: ", resultVars)
    if estimate: return dataTypes 
    return resultVars

def getOpCost(op_key, xorVarMap, varNames):
    global assignInfo
    varCounts = {}
    if op_key == expOp:
        for i in varNames:
            (funcName, varInfo) = getVarNameEntryFromAssignInfo(assignInfo, i)
            ceo = CountExpOp()
            sdl.ASTVisitor(ceo).preorder(varInfo.getAssignNode())
            v = xorVarMap.get(i)
            varCounts[ v ] = ceo.getCount()
        # JAA: commented out for benchmarking    
        #print("Final varCount for expOp: ", varCounts)

    return varCounts
    
def getConstraintList(info, constraintList, configVarName, xorVarMap, varTypes, generators, returnList=False):
    VarNames = getAssignmentForName(configVarName, varTypes)
    VarNames = list(set(VarNames).difference(generators))
    VarNames.sort()
    if info['verbose']: print("pruned varList: ", VarNames)
    if info != None:
        info['notInAPairing'] = list(set(VarNames).difference(xorVarMap.keys()))
        info['notInAPairing'].sort()
        if info[minOp] != None:
            # extract counts for whatever operation
            info[minKeyword] = getOpCost(info[minOp], xorVarMap, VarNames)
    # JAA: commented out for benchmarking
    #if len(info['notInAPairing']) > 0: print("Not in a pairing: ", info['notInAPairing'])
    VarNameList = []
    for i in VarNames:
        if xorVarMap.get(i) != None: VarNameList.append( xorVarMap.get(i) )
    if len(constraintList) > 0:
        for i in constraintList: # in case there are hash values
            if xorVarMap.get(i) != None and xorVarMap.get(i) not in VarNameList: 
                VarNameList.append( xorVarMap.get(i) )
    if returnList:
        return VarNameList # list
    return str(VarNameList) # string
 

def searchForSolution(info, shortOpt, hardConstraintList, txor, varTypes, conf, generators):
    resultDict = None
    satisfiable = False
    adjustConstraints = False
    mofnConstraints = None # only used if necessary
    fileSuffix = ""
    bothConstraints = {isSet:False }
    constraints = []
    # determine if user specified granular options such as 
    info[minOp] = None
    minOps = sizeOp # default operation
    info[minKeyword] = {}
    # check if user set the min operation field in config file?
    # this indicates interest in measuring 
    if hasattr(conf, minOp):
        info[minOp] = conf.operation
        minOps = info[minOp]           
    
    while not satisfiable:
        #print("\n<===== Generate Constraints =====>")    
        xorVarMap = txor.getVarMap()
        if shortOpt == SHORT_SECKEYS:
            # create constraints around keys
            fileSuffix = 'ky'
            assert type(conf.keygenSecVar) == str, "keygenSecVar in config file expected as a string"
            if not adjustConstraints:
                constraints = getConstraintList(info, hardConstraintList, conf.keygenSecVar, xorVarMap, varTypes, generators)
            else:
                flexConstraints = getConstraintList(info, [], conf.keygenSecVar, xorVarMap, varTypes, generators, returnList=True)
                newConstraintList = [xorVarMap.get(i) for i in hardConstraintList]
                flexConstraints = list(set(flexConstraints).difference(newConstraintList))
                if info['verbose']: 
                    print("DEBUG: n-of-n constraints: ", newConstraintList)
                    print("DEBUG: m-of-n constraints: ", flexConstraints)
                constraints = newConstraintList
                mofnConstraints = flexConstraints                        
        elif shortOpt == SHORT_PUBKEYS:
            # create constraints around keys
            fileSuffix = 'ky'
            assert type(conf.keygenPubVar) == str, "keygenPubVar in config file expected as a string"
            if not adjustConstraints:
                constraints = getConstraintList(info, hardConstraintList, conf.keygenPubVar, xorVarMap, varTypes, generators)
            else:
                flexConstraints = getConstraintList(info, [], conf.keygenPubVar, xorVarMap, varTypes, generators, returnList=True)
                newConstraintList = [xorVarMap.get(i) for i in hardConstraintList]
                flexConstraints = list(set(flexConstraints).difference(newConstraintList))
                if info['verbose']:
                    print("DEBUG: n-of-n constraints: ", newConstraintList)
                    print("DEBUG: m-of-n constraints: ", flexConstraints)
                constraints = newConstraintList
                mofnConstraints = flexConstraints            
        elif shortOpt == SHORT_CIPHERTEXT:
            fileSuffix = 'ct'
            assert type(conf.ciphertextVar) == str, "ciphertextVar in config file expected as a string"
            if not adjustConstraints:
                constraints = getConstraintList(info, hardConstraintList, conf.ciphertextVar, xorVarMap, varTypes, generators)
            else:
                flexConstraints = getConstraintList(info, [], conf.ciphertextVar, xorVarMap, varTypes, generators, returnList=True)
                newConstraintList = [xorVarMap.get(i) for i in hardConstraintList]
                flexConstraints = list(set(flexConstraints).difference(newConstraintList))
                if info['verbose']:
                    print("DEBUG: n-of-n constraints: ", newConstraintList)
                    print("DEBUG: m-of-n constraints: ", flexConstraints)
                constraints = newConstraintList
                mofnConstraints = flexConstraints
        elif shortOpt == SHORT_SIGNATURE:
            fileSuffix = 'sig'
            assert type(conf.signatureVar) == str, "signatureVar in config file expected as a string"
            if not adjustConstraints:
                constraints = getConstraintList(info, hardConstraintList, conf.signatureVar, xorVarMap, varTypes, generators)
            else:
                flexConstraints = getConstraintList(info, [], conf.signatureVar, xorVarMap, varTypes, generators, returnList=True)
                newConstraintList = [xorVarMap.get(i) for i in hardConstraintList]
                flexConstraints = list(set(flexConstraints).difference(newConstraintList))
                if info['verbose']:
                    print("DEBUG: n-of-n constraints: ", newConstraintList)
                    print("DEBUG: m-of-n constraints: ", flexConstraints)
                constraints = newConstraintList
                mofnConstraints = flexConstraints
        elif shortOpt == SHORT_FORALL and conf.schemeType == PKENC:
            fileSuffix = 'both' #default
            _hardConstraintList = [xorVarMap.get(i) for i in hardConstraintList]
            if info['verbose']: print("default constraints: ", _hardConstraintList)
            constraints_ky = getConstraintList(info, [], conf.keygenSecVar, xorVarMap, varTypes, generators, returnList=True)
            constraints_ky = list(set(constraints_ky).difference(_hardConstraintList))
            if info['verbose']: print("Constraints for ky: ", constraints_ky)
            constraints_ct = getConstraintList(info, [], conf.ciphertextVar, xorVarMap, varTypes, generators, returnList=True)
            constraints_ct = list(set(constraints_ct).difference(_hardConstraintList))
            if info['verbose']: print("Constraints for ct: ", constraints_ct)
            constraints = list(_hardConstraintList) + [conf.keygenSecVar, conf.ciphertextVar]
            bothConstraints[ isSet ] = True
            bothConstraints[ conf.keygenSecVar ] = constraints_ky
            bothConstraints[ conf.ciphertextVar ] = constraints_ct
        elif shortOpt == SHORT_FORALL and conf.schemeType == PKSIG:
            fileSuffix = 'both' #default
            _hardConstraintList = [xorVarMap.get(i) for i in hardConstraintList]
            if info['verbose']: print("default constraints: ", _hardConstraintList)
            constraints_ky = getConstraintList(info, [], conf.keygenPubVar, xorVarMap, varTypes, generators, returnList=True)
            constraints_ky = list(set(constraints_ky).difference(_hardConstraintList))
            if info['verbose']: print("Constraints for ky: ", constraints_ky)
            constraints_sig = getConstraintList(info, [], conf.signatureVar, xorVarMap, varTypes, generators, returnList=True)
            constraints_sig = list(set(constraints_sig).difference(_hardConstraintList))
            if info['verbose']: print("Constraints for sig: ", constraints_sig)
            constraints = list(_hardConstraintList) + [conf.keygenPubVar, conf.signatureVar]
            bothConstraints[ isSet ] = True            
            bothConstraints[ conf.keygenPubVar ] = constraints_ky
            bothConstraints[ conf.signatureVar ] = constraints_sig
        else:
            # JAA: commented out for benchmarking
            #print("'short' option not specified.\n")
            shortOpt = ""
        
        # time options
        timeOpt = ""
        if info[minOp] != None:
            fileSuffix += info[minOp]                
            if conf.schemeType == PKENC:
                configVarName = conf.keygenSecVar
                VarNames1 = getAssignmentForName(configVarName, varTypes)
                VarNames1 = list(set(VarNames1).difference(generators))
                VarNames1.sort()
                configVarName = conf.ciphertextVar
                VarNames2 = getAssignmentForName(configVarName, varTypes)
                VarNames2 = list(set(VarNames2).difference(generators))
                VarNames2.sort()
                
                VarNames = VarNames1 + VarNames2
                info[minKeyword] = getOpCost(info[minOp], xorVarMap, VarNames)
                timeOpt = info[minOp]
            elif conf.schemeType == PKSIG:
                configVarName = conf.keygenPubVar
                VarNames1 = getAssignmentForName(configVarName, varTypes)
                VarNames1 = list(set(VarNames1).difference(generators))
                VarNames1.sort()
                configVarName = conf.signatureVar
                VarNames2 = getAssignmentForName(configVarName, varTypes)
                VarNames2 = list(set(VarNames2).difference(generators))
                VarNames2.sort()
                
                VarNames = VarNames1 + VarNames2
                info[minKeyword] = getOpCost(info[minOp], xorVarMap, VarNames)
                timeOpt = info[minOp]
                
        #else:
        #    print("Unexpected configuration. Run python runAutoGroup.py --help-config")
        #    sys.exit(-1)
                
        #print("<===== Generate Constraints =====>\n")
        
        #print("<===== Generate SAT solver input =====>")
        
        # TODO: process constraints and add to output
        #print("<===== Instantiate Z3 solver =====>")
        #print("map: ", xorVarMap)
        #print("original hard constraint: ", hardConstraintList)
        hardConstraints = [xorVarMap.get(i) for i in hardConstraintList]
        minOptions = info[curveID] # user should provide this information
        countOpt = info[minKeyword] # the cost of group operations
        (satisfiable, resultDict) = instantiateZ3Solver(shortOpt, timeOpt, txor.getVariables(), txor.getClauses(), hardConstraints, constraints, bothConstraints, countOpt, minOptions)
        if satisfiable == False:
            #print("Adjusing constraints...")
            adjustConstraints = True
        #print("<===== Instantiate Z3 solver =====>")

    return fileSuffix, resultDict

def convertType(v, i):
    if i == types.int:
        return "int"
    elif i == types.listInt:
        return "list{int}"
    elif i == types.str:
        return "str"
    elif i == types.listStr:
        return "list{str}"
    elif i == types.GT:
        return "GT"
    elif i == types.listGT:
        return "list{GT}"
    elif i == types.pol:
        return "pol"
    elif i == types.list:
        return "list"
    elif i == types.ZR:
        return "ZR"
    elif i == types.listZR:
        return "list{ZR}"
    print("DEBUG: convertType error: ", v, " = ", i)
    return False

def newTypeFrom(t, suffix):
    if suffix == G1Prefix:
        if t == types.G1:
            return "G1"
        elif t == types.listG1:
            return "list{G1}"
    elif suffix == G2Prefix:
        if t == types.G1:
            return "G2"
        elif t == types.listG1:
            return "list{G2}"
    return str(t) # not sure here
    
def transformTypes(typesH, info):
    typesHeadBegin = "BEGIN :: " + sdl.TYPES_HEADER
    typesHeadEnd = "END :: " + sdl.TYPES_HEADER
    newLines = [typesHeadBegin]
    typeLines = {}
    # extract line numbers
    for i, j in typesH.items():
        typeLines[ j.getLineNo() ] = (i, j)
    
    # sort based on line number, then process each type
    typeKeysList = list(typeLines.keys())
    typeKeysList.sort() # sort the line numbers
    for k in typeKeysList:
        (i, j) = typeLines[k]
        t = j.getType()
        if t in [types.G1, types.listG1]: #, types.int, types.listInt, types.str, types.listStr, types.GT]:
            if assignVarOccursInBoth(i, info):
                #print(i, " :-> split computation in G1 & G2")
                newLines.append( i + G1Prefix + " := " + newTypeFrom(t, G1Prefix) )
                newLines.append( i + G2Prefix + " := " + newTypeFrom(t, G2Prefix) )
            elif assignVarOccursInG1(i, info):
                #print(i, " :-> just in G1.")
                newLines.append( i + " := " + newTypeFrom(t, G1Prefix) )
            elif assignVarOccursInG2(i, info):
                #print(i, " :-> just in G2.")
                newLines.append( i + " := " + newTypeFrom(t, G2Prefix) )
            elif i in info['generators']:
                if i in info['generatorMapG1']:
                    newLines.append(info['generatorMapG1'][i] + " := " + newTypeFrom(t, G1Prefix) )
                if i in info['generatorMapG2']:
                    newLines.append(info['generatorMapG2'][i] + " := " + newTypeFrom(t, G2Prefix) )
        else:
            resType = convertType(i, t)
            if resType != False:
                newLines.append( i + " := " + resType )
            else:
                # keep the original SDL type line
                newLines.append( j.getSrcLine() )
    
    newLines.append(typesHeadEnd)
    return newLines


def runAutoGroup(sdlFile, config, options, sdlVerbose=False):
    sdl.parseFile(sdlFile, sdlVerbose, ignoreCloudSourcing=True)
    global assignInfo
    assignInfo = sdl.getAssignInfo()
    setting = sdl.assignInfo[sdl.NONE_FUNC_NAME][ALGEBRAIC_SETTING].getAssignNode().getRight().getAttribute()
    sdl_name = sdl.assignInfo[sdl.NONE_FUNC_NAME][BV_NAME].getAssignNode().getRight().getAttribute()
    typesBlock = sdl.getFuncStmts( TYPES_HEADER )
    
    userCodeBlocks = list(set(list(assignInfo.keys())).difference(config.functionOrder + [TYPES_HEADER, NONE_FUNC_NAME]))
    options['userFuncList'] += userCodeBlocks
    print("name is", sdl_name)
    print("setting is", setting)
    
    lines = list(typesBlock[0].keys())
    lines.sort()
    typesBlockLines = [ i.rstrip() for i in sdl.getLinesOfCodeFromLineNos(lines) ]
    begin = ["BEGIN :: " + TYPES_HEADER]
    end = ["END :: " + TYPES_HEADER]

    newLines0 = [ BV_NAME + " := " + sdl_name, SETTING + " := " + sdl.ASYMMETRIC_SETTING ] 
    newLines1 = begin + typesBlockLines + end
    
    assert setting == sdl.SYMMETRIC_SETTING, "No need to convert to asymmetric setting."    
    # determine user preference in terms of keygen or encrypt
    short = SHORT_DEFAULT # default option
    if hasattr(config, 'short'):
        if config.short in SHORT_OPTIONS:
            short = config.short
    print("reducing size of '%s'" % short) 

    varTypes = dict(sdl.getVarTypes().get(TYPES_HEADER))
    typesH = dict(varTypes)
    if not hasattr(config, 'schemeType'):
        sys.exit("'schemeType' option missing in specified config file.")
    pairingSearch = []
    if config.schemeType == PKENC:
        (stmtS, typesS, depListS, depListNoExpS, infListS, infListNoExpS) = sdl.getVarInfoFuncStmts( config.setupFuncName )
        (stmtK, typesK, depListK, depListNoExpK, infListK, infListNoExpK) = sdl.getVarInfoFuncStmts( config.keygenFuncName )
        (stmtE, typesE, depListE, depListNoExpE, infListE, infListNoExpE) = sdl.getVarInfoFuncStmts( config.encryptFuncName )    
        (stmtD, typesD, depListD, depListNoExpD, infListD, infListNoExpD) = sdl.getVarInfoFuncStmts( config.decryptFuncName )
        varTypes.update(typesS)
        varTypes.update(typesK)
        varTypes.update(typesE)
        varTypes.update(typesD)
        # TODO: expand search to encrypt and potentially setup
        pairingSearch += [stmtS, stmtE, stmtD] # aka start with decrypt.
    elif config.schemeType == PKSIG:
        if hasattr(config, 'setupFuncName'): 
            (stmtS, typesS, depListS, depListNoExpS, infListS, infListNoExpS) = sdl.getVarInfoFuncStmts( config.setupFuncName )
            varTypes.update(typesS)
            pairingSearch += [stmtS]
        (stmtK, typesK, depListK, depListNoExpK, infListK, infListNoExpK) = sdl.getVarInfoFuncStmts( config.keygenFuncName )
        (stmtSi, typesSi, depListSi, depListNoExpSi, infListSi, infListNoExpSi) = sdl.getVarInfoFuncStmts( config.signFuncName )    
        (stmtV, typesV, depListV, depListNoExpV, infListV, infListNoExpV) = sdl.getVarInfoFuncStmts( config.verifyFuncName )
        varTypes.update(typesK)
        varTypes.update(typesSi)
        varTypes.update(typesV)
        pairingSearch += [stmtV] # aka start with verify
    else:
        sys.exit("'schemeType' options are 'PKENC' or 'PKSIG'")
            
    info = {'verbose':False}
    info[curveID] = options['secparam']
    gen = Generators(info)
    # JAA: commented out for benchmarking    
    #print("List of generators for scheme")
    if hasattr(config, "extraSetupFuncName"):
        (stmtSe, typesSe, depListSe, depListNoExpSe, infListSe, infListNoExpSe) = sdl.getVarInfoFuncStmts( config.extraSetupFuncName )
        gen.extractGens(stmtSe, typesSe)
        #extractGeneratorList(stmtSe, typesSe, generators)
        varTypes.update(typesSe)
    
    if hasattr(config, 'setupFuncName'):
        gen.extractGens(stmtS, typesS)
    if hasattr(config, 'keygenFuncName'):
        gen.extractGens(stmtK, typesK)
    else:
        sys.exit("Assumption failed: setup not defined for this function. Where to extract generators?")
    generators = gen.getGens()
    # JAA: commented out for benchmarking    
    #print("Generators extracted: ", generators)

    # need a Visitor class to build these variables  
    # TODO: expand to other parts of algorithm including setup, keygen, encrypt 
    hashVarList = []
    pair_vars_G1_lhs = [] 
    pair_vars_G1_rhs = []    
    gpv = GetPairingVariables(pair_vars_G1_lhs, pair_vars_G1_rhs) 
    for eachStmt in pairingSearch:
        lines = eachStmt.keys()
        for i in lines:
            if type(eachStmt[i]) == sdl.VarInfo:
                
                #print("Each: ", eachStmt[i].getAssignNode())
                if HasPairings( eachStmt[i].getAssignNode() ):
                    path_applied = []
                    eachStmt[i].assignNode = SplitPairings(eachStmt[i].getAssignNode(), path_applied)
                    # JAA: commented out for benchmarking                    
                    #if len(path_applied) > 0: print("Split Pairings: ", eachStmt[i].getAssignNode())
                    #print("Each: ", eachStmt[i].getAssignNode())
                    sdl.ASTVisitor( gpv ).preorder( eachStmt[i].getAssignNode() )
                elif eachStmt[i].getHashArgsInAssignNode(): 
                    # in case, there's a hashed values...build up list and check later to see if it appears
                    # in pairing variable list
                    hashVarList.append(str(eachStmt[i].getAssignVar()))
                else:
                    continue # not interested
                
    constraintList = []
    # determine if any hashed values in decrypt show up in a pairing
    for i in hashVarList:
        if i in pair_vars_G1_lhs or i in pair_vars_G1_rhs:
            constraintList.append(i)
    # JAA: commented out for benchmarking            
    #print("pair vars LHS:", pair_vars_G1_lhs)
    #print("pair vars RHS:", pair_vars_G1_rhs) 
    #print("list of gens :", generators)
    #print("constraintList: ", constraintList)
    info[ 'G1_lhs' ] = (pair_vars_G1_lhs, assignTraceback(generators, varTypes, pair_vars_G1_lhs, constraintList))
    info[ 'G1_rhs' ] = (pair_vars_G1_rhs, assignTraceback(generators, varTypes, pair_vars_G1_rhs, constraintList))
   
    # JAA: commented out for benchmarking     
    #print("info => G1 lhs : ", info['G1_lhs'])
    #print("info => G1 rhs : ", info['G1_rhs'])   
    #print("<===== Determine Asymmetric Generators =====>")
    #(generatorLines, generatorMapG1, generatorMapG2) = Step1_DeriveSetupGenerators(generators, info)
    (generatorMapG1, generatorMapG2) = gen.setupNewGens()
    generatorLines = gen.getGenLines()
    # JAA: commented out for benchmarking    
    #print("Generators in G1: ", generatorMapG1)
    #print("Generators in G2: ", generatorMapG2)
    #print("<===== Determine Asymmetric Generators =====>\n")
    
    #print("<===== Generate XOR clauses =====>")  
    # let the user's preference for fixing the keys or ciphertext guide this portion of the algorithm.
    # info[ 'G1' ] : represents (varKeyList, depVarMap). 
    assert len(pair_vars_G1_lhs) == len(pair_vars_G1_rhs), "Uneven number of pairings. Please inspect your bv file."
    varsLen = len(pair_vars_G1_lhs)
    xorList = []
    for i in range(varsLen):
        xor = BinaryNode(ops.XOR)
        xor.left = BinaryNode(pair_vars_G1_lhs[i])
        xor.right = BinaryNode(pair_vars_G1_rhs[i])
        xorList.append(xor)
    
    ANDs = [ BinaryNode(ops.AND) for i in range(len(xorList)-1) ]
    for i in range(len(ANDs)):
        ANDs[i].left = BinaryNode.copy(xorList[i])
        if i < len(ANDs)-1: ANDs[i].right = ANDs[i+1]
        else: ANDs[i].right = BinaryNode.copy(xorList[i+1])
    # JAA: commented out for benchmarking        
    #print("XOR clause: ", ANDs[0])
    txor = transformXOR(None) # accepts dictionary of fixed values
    sdl.ASTVisitor(txor).preorder(ANDs[0])
    #print("<===== Generate XOR clauses =====>")
        
    constraints = "[]"
    fileSuffix, resultDict = searchForSolution(info, short, constraintList, txor, varTypes, config, generators)
    
    xorVarMap = txor.getVarMap()
#    if short != SHORT_FORALL:
#        res, resMap = NaiveEvaluation(resultDict, short)
#        print("Group Mapping: ", res)
#        # determine whether to make True = G1 and False = G2. 
#        # It depends on which counts more since they're interchangeable...
#        groupInfo = DeriveGeneralSolution(res, resMap, xorVarMap, info)
#    else:

    groupInfo = DeriveSpecificSolution(resultDict, xorVarMap, info)
    symDataTypePK  = {}
    asymDataTypePK = {}
    if config.schemeType == PKENC and options['computeSize']:   
        symDataTypeSK = getAssignmentForName(config.keygenSecVar, varTypes, True)
        symDataTypeCT = getAssignmentForName(config.ciphertextVar, varTypes, True)
        asymDataTypeSK = {}
        asymDataTypeCT = {}
        newSol = groupInfo['newSol']
        for i in symDataTypeSK:
            if i in newSol.keys():
               asymDataTypeSK[i] = newSol[i]
            else:
               asymDataTypeSK[i] = symDataTypeSK[i]
               
        for i in symDataTypeCT:
            if i in newSol.keys():
               asymDataTypeCT[i] = newSol[i]
            else:
               asymDataTypeCT[i] = symDataTypeCT[i]
        print("<====================>")
        print("SK => ", list(symDataTypeSK.keys()))
        print("estimated  sym:  ", estimateSize(symDataTypeSK, symmetric_curves['SS1536']))        
        print("estimated asym: ", estimateSize(asymDataTypeSK, asymmetric_curves['BN256']))
        print("CT => ", list(symDataTypeCT.keys()))               
        print("estimated  sym: ", estimateSize(symDataTypeCT, symmetric_curves['SS1536']))            
        print("estimated asym: ", estimateSize(asymDataTypeCT, asymmetric_curves['BN256']))
        print("<====================>")
    elif config.schemeType == PKSIG and options['computeSize']:
        symDataTypePK = getAssignmentForName(config.keygenPubVar, varTypes, True)
        symDataTypeSIG = getAssignmentForName(config.signatureVar, varTypes, True)
        #asymDataTypePK = {}
        asymDataTypeSIG = {}
        newSol = groupInfo['newSol']
        for i in symDataTypePK:
            if i in newSol.keys():
               asymDataTypePK[i] = newSol[i]
            else:
               asymDataTypePK[i] = symDataTypePK[i] # keep old type
               
        for i in symDataTypeSIG:
            if i in newSol.keys():
               asymDataTypeSIG[i] = newSol[i]
            else:
               asymDataTypeSIG[i] = symDataTypeSIG[i]
        print("<====================>")
#        print("PK => ", list(symDataTypePK.keys()))
#        print("estimated  sym:  ", estimateSize(symDataTypePK, symmetric_curves['SS1536']))        
#        print("estimated asym: ", estimateSize(asymDataTypePK, asymmetric_curves['BN256']))
        print("SIG => ", list(symDataTypeSIG.keys()))               
        print("estimated  sym: ", estimateSize(symDataTypeSIG, symmetric_curves['SS1536']))            
        print("estimated asym: ", estimateSize(asymDataTypeSIG, asymmetric_curves['BN256']))
        print("<====================>")

    if info.get('notInAPairing') != None and len(info['notInAPairing']) > 0:
        groupInfo['G1'] = groupInfo['G1'].union( info['notInAPairing'] )
        #print("Update: new G1 deps=>", groupInfo['G1'])    

    groupInfo['generators'] = generators 
    groupInfo['generatorMapG1'] = generatorMapG1
    groupInfo['generatorMapG2'] = generatorMapG2
    groupInfo['baseGeneratorG1'] = info['baseGeneratorG1'] # usually 'g'
    groupInfo['baseGeneratorG2'] = info['baseGeneratorG2']
    groupInfo['newTypes'] = {}
    groupInfo['varTypes'] = {}
    groupInfo['varTypes'].update(varTypes)
    groupInfo['usedVars'] = set()
    groupInfo['verbose'] = info['verbose']
    transFunc = {}
    transFuncGen = {}

    if hasattr(config, "extraSetupFuncName"):
        transFuncGen[ config.extraSetupFuncName ] = stmtSe
    if hasattr(config, 'setupFuncName'):    
        transFuncGen[ config.setupFuncName ] = stmtS
    elif hasattr(config, 'keygenFuncName'):
        transFuncGen[ config.keygenFuncName ] = stmtK

    if config.schemeType == PKENC:
        transFunc[ config.keygenFuncName ]  = stmtK
        transFunc[ config.encryptFuncName ] = stmtE
        transFunc[ config.decryptFuncName ] = stmtD
    elif config.schemeType == PKSIG:
        if hasattr(config, 'setupFuncName') or hasattr(config, "extraSetupFuncName"):
            transFunc[ config.keygenFuncName ] = stmtK
        transFunc[ config.signFuncName ] = stmtSi
        transFunc[ config.verifyFuncName ] = stmtV
    
    if options['computeSize']:
        options['symPK']  = symDataTypePK
        options['asymPK'] = asymDataTypePK
    newSDL = AsymSDL(options, assignInfo, groupInfo, typesH, generatorLines, transFunc, transFuncGen)
    # fix this!!!!
    newLinesT, newLinesSe, newLinesS, newLinesK, newLines2, newLines3, userFuncLines = newSDL.constructSDL(config)

    # debug 
    print_sdl(info['verbose'], newLinesS, newLinesK, newLines2, newLines3)
    outputFile = sdl_name + "_asym_" + fileSuffix + sdlSuffix
    writeConfig(outputFile, newLines0, newLinesT, newLinesSe, newLinesS, newLinesK, newLines2, newLines3, userFuncLines)
    return outputFile
        

class AsymSDL:
    def __init__(self, options, assignInfo, groupInfo, typesH, generatorLines, transFunc, transFuncGen):
        self.assignInfo     = assignInfo
        self.groupInfo      = copy.deepcopy(groupInfo)
        self.groupInfo['myAsymSDL'] = self # this is for recording used vars in each function
        self.generatorMap   = list(self.groupInfo['generatorMapG1'].values()) + list(self.groupInfo['generatorMapG2'].values()) 
        self.typesH         = copy.deepcopy(typesH)
        self.generatorLines = copy.deepcopy(generatorLines)
        self.transFunc      = transFunc
        self.transFuncGen   = transFuncGen
        self.userFuncList   = options['userFuncList']
        if options['computeSize']:
            self.__computeSize = True
            if options.get('asymPK') != None: self.__aPKdict = options['asymPK']            
            else: self.__aPKdict = None
            if options.get('symPK') != None: self.__sPKdict = options['symPK']
            else: self.__sPKdict = None
        else:
            self.__computeSize = False
            self.__aPKdict = None
            self.__sPKdict = None            
        self.verbose        = groupInfo['verbose']
        self.__currentFunc    = None
        self.__funcUsedVar    = {}

    def __getFuncLines(self, funcName):
        funcConfig = sdl.getVarInfoFuncStmts( funcName )
        Stmts = funcConfig[0]
        begin = "BEGIN :: func:" + funcName
        end   = "END :: func:" + funcName
        
        lines = list(Stmts.keys())
        lines.sort()
        newLines = [begin]
        for index, i in enumerate(lines):
            assert type(Stmts[i]) == sdl.VarInfo, "transformFunction: blockStmts must be VarInfo Objects."
            if Stmts[i].getIsExpandNode() or Stmts[i].getIsList():
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
        return newLines


    def recordUsedVar(self, varList):
        assert type(varList) in [set, list], "AsymSDL.recordUsedVar: expected a list or set type."
        if self.__currentFunc != None:
            if self.__funcUsedVar.get( self.__currentFunc ) == None:
                self.__funcUsedVar[ self.__currentFunc ] = set() # create new set iff the first time
            self.__funcUsedVar[ self.__currentFunc ] = self.__funcUsedVar[ self.__currentFunc ].union(varList)
        return
    
    def constructSDL(self, config):
        noChangeList = []
        # process original TYPES section to see what we should add to noChangeList (str, int or GT types)    
        for i, j in self.typesH.items():
            t = j.getType()
            if t in [types.ZR, types.listZR, types.int, types.listInt, types.str, types.listStr, types.GT]: 
                noChangeList.append(i)
        # JAA: commented out for benchmarking    
        #print("Initial noChangeList: ", noChangeList)
        #(Stmts, Types, depList, depListNoExp, infList, infListNoExp)
        userFuncLines = []
        if len(self.userFuncList) > 0:
            for userFuncs in self.userFuncList:
                # JAA: commented out for benchmarking                
                #print("processing user defined func: ", userFuncs)
                userFuncLines.append( self.__getFuncLines(userFuncs) )
#                userFuncData = sdl.getVarInfoFuncStmts( userFuncs )
#                userTypes = userFuncData[1]
#                for j in userTypes.keys():
#                    print("user func vars: ", j)
#                    noChangeList.append(j)
        
 
        newLinesSe = []
        newLinesS = []
        newLinesK = []
        entireSDL = sdl.getLinesOfCode()
        transFuncRes = {}
        Input = {}
        for funcName in config.functionOrder:
            if funcName in self.transFuncGen.keys():
                #print("<===== processing %s =====>" % funcName)
                self.__currentFunc = funcName
                transFuncRes[ funcName ] = transformFunction(entireSDL, funcName, self.transFuncGen[ funcName ], self.groupInfo, noChangeList, self.generatorLines)
                #print("<===== processing %s =====>" % funcName)
                
        # obtain results
        newLinesT = transformTypes(self.typesH, self.groupInfo)
        if hasattr(config, "extraSetupFuncName"):
            newLinesSe = transFuncRes.get( config.extraSetupFuncName )
        if hasattr(config, 'setupFuncName'):   
            newLinesS  = transFuncRes.get( config.setupFuncName )
        elif hasattr(config, 'keygenFuncName'):
            newLinesK  = transFuncRes.get( config.keygenFuncName )
        
        # transform body of SDL scheme
        if config.schemeType == PKENC:
            for funcName in config.functionOrder:
                if funcName in self.transFunc.keys():
                    #print("<===== processing %s =====>" % funcName)
                    self.__currentFunc = funcName
                    transFuncRes[ funcName ] = transformFunction(entireSDL, funcName, self.transFunc[ funcName ], self.groupInfo, noChangeList)
                    #print("<===== processing %s =====>" % funcName)
            newLinesK = transFuncRes.get( config.keygenFuncName )
            newLines2 = transFuncRes.get( config.encryptFuncName )
            newLines3 = transFuncRes.get( config.decryptFuncName )
                
        elif config.schemeType == PKSIG:
            for funcName in config.functionOrder:
                if funcName in self.transFunc.keys():
                    #print("<===== processing %s =====>" % funcName)
                    self.__currentFunc = funcName                    
                    transFuncRes[ funcName ] = transformFunction(entireSDL, funcName, self.transFunc[ funcName ], self.groupInfo, noChangeList) 
                    #print("<===== processing %s =====>" % funcName)
                
            newLinesK = transFuncRes.get( config.keygenFuncName )
            newLines2 = transFuncRes.get( config.signFuncName )
            newLines3 = transFuncRes.get( config.verifyFuncName )
        
        # prune generators not used in the scheme 
        usedGenerators = []
        for i in self.groupInfo['usedVars']:
            if i in self.generatorMap:
                # actual generator
                usedGenerators.append(i)
        #print("usedVars :=> ", usedGenerators)
        #print("generators :=> ", self.generatorMap)
        deleteMe = list(set(self.generatorMap).difference(usedGenerators))
                
        if len(deleteMe) > 0:
            #print("Pruning Generators:\t", deleteMe)
            newLinesSe = self.__prune(newLinesSe, deleteMe)
            newLinesS  = self.__prune(newLinesS, deleteMe)
            newLinesK  = self.__prune(newLinesK, deleteMe)
            newLines2  = self.__prune(newLines2, deleteMe)
            newLines3  = self.__prune(newLines3, deleteMe)
        
        if config.schemeType == PKSIG:
            # 1. find out where pk was originally defined
            (defInFuncName, varInf) = getVarNameEntryFromAssignInfo(self.assignInfo, config.keygenPubVar)
            # 2. get new pk list if defined in scheme
            origPKList = self.__getOriginalPK(config.keygenPubVar, newLinesSe + newLinesS + newLinesK)
            # 3. split pk into two new public keys (sPK, and vPK)
            if len(origPKList) > 0:
                (sPub, vPub, newSignPK, newVerifyPK, newSignPKexp, newVerifyPKexp) = self.optimizePK(config, origPKList)
                
                # apply PKSIG optimizations to pk
                newVarNames = [sPub, vPub]
                newVarNodes = [newSignPK, newVerifyPK]
                #print("Public Key defined in ", defInFuncName)
                if defInFuncName == "setup":
                    newLinesS = self.__updatePKList(config.keygenPubVar, newVarNodes, newVarNames, newLinesS)
                elif defInFuncName == "keygen":
                    newLinesK = self.__updatePKList(config.keygenPubVar, newVarNodes, newVarNames, newLinesK)
                
                # sPub => keygen AND sign
                # vPub => verify 
                if defInFuncName != "keygen":
                    newLinesK = self.__updatePKExpand(config.keygenPubVar, newSignPKexp, sPub, newLinesK)                
                newLines2 = self.__updatePKExpand(config.keygenPubVar, newSignPKexp, sPub, newLines2)
                newLines3 = self.__updatePKExpand(config.keygenPubVar, newVerifyPKexp, vPub, newLines3)
            
        return newLinesT, newLinesSe, newLinesS, newLinesK, newLines2, newLines3, userFuncLines

    def __updatePKList(self, targetVar, newVarNodes, newVarNames, newLinesK):
        nodeLines2 = []
        replacedNewPK = False 
        for node in newLinesK:
            if Type(node) == ops.EQ:
                if str(node.left) == targetVar: # found
                    nodeLines2.extend(newVarNodes)
                    replacedNewPK = True
                    continue
                if str(node.left) == outputKeyword and replacedNewPK:
                    sv = SubstituteVar(targetVar, newVarNames)
                    sdl.ASTVisitor(sv).preorder(node)
            nodeLines2.append( node )
        return nodeLines2

    def __updatePKExpand(self, targetVar, newVarNode, newVarName, newLines):
        nodeLines2 = []
        replacedNewPK = False 
        for node in newLines:
            if Type(node) == ops.EQ:
                if str(node.left) == targetVar: # found
                    nodeLines2.append(newVarNode)
                    continue
                if str(node.left) == inputKeyword:
                    sv = SubstituteVar(targetVar, newVarName)
                    sdl.ASTVisitor(sv).preorder(node)
            nodeLines2.append( node )
        return nodeLines2

    def optimizePK(self, config, origPK):
        #print("origPK :", origPK)
        if len(origPK) > 0:
            signUsedVars   = []
            signVars       = self.__funcUsedVar.get(config.signFuncName)
            if signVars != None:
                for i in signVars:
                    if i in origPK: signUsedVars.append(i)

            keygenVars       = self.__funcUsedVar.get(config.keygenFuncName)
            #print("keygenVars: ", keygenVars)
            if keygenVars != None:
                for i in keygenVars:
                    if i in origPK:
                        if i not in signUsedVars: signUsedVars.append(i)
            signUsedVars.sort()
            
            verifyUsedVars = []
            verifyVars     = self.__funcUsedVar.get(config.verifyFuncName)
            if verifyVars != None:
                for i in verifyVars:
                    if i in origPK: verifyUsedVars.append(i)
            verifyUsedVars.sort()
            
            asymDataTypePK = {}
            if self.__aPKdict != None:
                for i in self.__aPKdict:
                    if i in verifyUsedVars:
                        asymDataTypePK[i] = self.__aPKdict[i]
                print("verifyUsedVars: ", verifyUsedVars)
                print("sym PK => ", list(self.__sPKdict.keys()))
                print("asym PK => ", list(asymDataTypePK.keys()))
                print("estimated  sym:  ", estimateSize(self.__sPKdict, symmetric_curves['SS1536']))        
                print("estimated asym: ", estimateSize(asymDataTypePK, asymmetric_curves['BN256']))
            
            sPub = "s"+config.keygenPubVar
            vPub = "v"+config.keygenPubVar
            newSignPK      = self.__createListNode(sPub, signUsedVars)
            newSignPKexp   = self.__createExpandNode(sPub, signUsedVars)
            newVerifyPK    = self.__createListNode(vPub, verifyUsedVars)
            newVerifyPKexp = self.__createExpandNode(vPub, verifyUsedVars)

            
        return (sPub, vPub, newSignPK, newVerifyPK, newSignPKexp, newVerifyPKexp)
            
    def __prune(self, nodeLines, deleteMeList):
        nodeLines2 = []
        for node in nodeLines:
            if Type(node) == ops.EQ:
                if str(node.left) in deleteMeList:
                    if self.verbose: print("Delete line: ", node.left)
                    continue
                else: # check right side
                    contain = DelAnyVarInList(deleteMeList) 
                    sdl.ASTVisitor(contain).preorder( node.right )
                    if len(contain.foundVar) > 0 and self.verbose: print("Deleted ", contain.foundVar)
            if self.verbose: print("line: ", node)
            nodeLines2.append( node )
        return nodeLines2
    
    def __getOriginalPK(self, varPK, funcs):
        for node in funcs:
            if Type(node) == ops.EQ:
                if str(node.left) == varPK and Type(node.right) == ops.LIST:
                    return node.right.listNodes
        return []    
                
    
    def __createListNode(self, name, varList):
        _list = BinaryNode(ops.LIST)
        _list.listNodes = list(varList)
        return BinaryNode(ops.EQ, BinaryNode(name), _list)
    
    def __createExpandNode(self, name, varList):
        _list = BinaryNode(ops.EXPAND)
        _list.listNodes = list(varList)
        return BinaryNode(ops.EQ, BinaryNode(name), _list)
        
# temporary placement
def NaiveEvaluation(solutionList, preference):
    trueCount = 0
    falseCount = 0
    resMap = {}
    for tupl in solutionList:
        (k, v) = tupl
        if v == True: trueCount += 1
        elif v == False: falseCount += 1
        else: sys.exit("z3 results have been tampered with.")
        resMap[ k ] = v
    
    if preference in [SHORT_SECKEYS, SHORT_PUBKEYS, SHORT_CIPHERTEXT, SHORT_SIGNATURE]:
        return {True:'G1', False:'G2'}, resMap
    
    if trueCount >= falseCount: 
        G1 = True; G2 = False
    elif falseCount > trueCount:
        G1 = False; G2 = True

    return { G1:'G1', G2:'G2' }, resMap

def DeriveGeneralSolution(groupMap, resultMap, xorMap, info):
    #print("<===== Deriving Solution from Results =====>")
    G1_deps = set()
    G2_deps = set()
    pairingInfo = {}
    pairingInfo[G1Prefix] = []
    pairingInfo[G2Prefix] = []
    for i in info['G1_lhs'][0] + info['G1_rhs'][0]:
        # get the z3 var for it
        z3Var = xorMap.get(i) # gives us an alphabet
        # look up value in resultMap
        varValue = resultMap.get(z3Var)
        # get group
        group = groupMap.get(varValue)
        if i in info['G1_lhs'][0]: deps = info['G1_lhs'][1].get(i)
        else: deps = info['G1_rhs'][1].get(i)
        deps = list(deps); deps.append(i) # var name to the list
        #print(i, ":=>", group, ": deps =>", deps)
        if group == 'G1': G1_deps = G1_deps.union(deps); pairingInfo[G1Prefix].append(i)
        elif group == 'G2': G2_deps = G2_deps.union(deps); pairingInfo[G2Prefix].append(i)
    #print("<===== Deriving Solution from Results =====>")    
    both = G1_deps.intersection(G2_deps)
    G1 = G1_deps.difference(both)
    G2 = G2_deps.difference(both)
    #print("Both G1 & G2: ", both)
    #print("Just G1: ", G1)
    #print("Just G2: ", G2)
    return { 'G1':G1, 'G2':G2, 'both':both, 'pairing':pairingInfo }

def DeriveSpecificSolution(resultDict, xorMap, info):  #groupMap, resultMap, xorMap, info):
    #print("<===== Deriving Specific Solution from Results =====>")
    G1_deps = set()
    G2_deps = set()
    resultMap = {}
    newSol = {}
    for tupl in resultDict:
        (k, v) = tupl
        resultMap[ k ] = v
    pairingInfo = {}
    pairingInfo[G1Prefix] = []
    pairingInfo[G2Prefix] = []
    for i in info['G1_lhs'][0] + info['G1_rhs'][0]:
        # get the z3 var for it
        z3Var = xorMap.get(i) # gives us an alphabet
        # look up value in resultMap
        varValue = resultMap.get(z3Var)
        # get group
        if varValue == True: group = 'G1'
        else: group = 'G2'
        
        if i in info['G1_lhs'][0]: deps = info['G1_lhs'][1].get(i)
        else: deps = info['G1_rhs'][1].get(i)
        deps = list(deps); deps.append(i) # var name to the list
        #print(i, ":=>", group, ": deps =>", deps)
        newSol[ i ] = group
        if group == 'G1': G1_deps = G1_deps.union(deps); pairingInfo[G1Prefix].append(i)
        elif group == 'G2': G2_deps = G2_deps.union(deps); pairingInfo[G2Prefix].append(i)
    #print("<===== Deriving Specific Solution from Results =====>")    
    both = G1_deps.intersection(G2_deps)
    G1 = G1_deps.difference(both)
    G2 = G2_deps.difference(both)
    #print("Both G1 & G2: ", both)
    #print("Just G1: ", G1)
    #print("Just G2: ", G2)
    return { 'G1':G1, 'G2':G2, 'both':both, 'pairing':pairingInfo, 'newSol':newSol }


def findVarInfo(var, varTypes):
    if var.find(LIST_INDEX_SYMBOL) != -1:
        v = var.split(LIST_INDEX_SYMBOL) 
        vName = v[0] 
#        vRef  = v[-1] # get last argument
#        levelsOfIndirection = len(v[1:])
#        print("vName :", vName)
#        print("type info :", varTypes.get(vName).getType())
#        print("vRef :", vRef)
#        print("levels :", levelsOfIndirection)
        return varTypes.get(vName)
        
def assignTraceback(generators, varTypes, listVars, constraintList):
    varProp = []
    data = {}
    # get variable names from all pairing
    for i in listVars:
        #print("var name := ", i)
        var = i
        buildMap(generators, varTypes, varProp, var, constraintList)
        data[i] = set(varProp)
        varProp = []
    
    #for i in listVars:
    #    print("key: ", i, ":=>", data[i])
#    print("varProp for ", listVars[0], ": ", varProp)
    return data

        
def buildMap(generators, varTypes, varList, var, constraintList):
    global assignInfo
    removeList = []
    if (not set(var).issubset(generators)):
        # JAA: commented out for benchmark
        #print("var keys: ", var)
        (name, varInf) = getVarNameEntryFromAssignInfo(assignInfo, var)
        if(name == None): 
            if varInf != None: pass #print("Var : ", varInf.getVarDepsNoExponents())
            elif var.find(LIST_INDEX_SYMBOL) != -1: varInf = findVarInfo(var, varTypes)
            return
        l = list(varInf.getVarDepsNoExponents())
#        print("var:", var, ", output: ", l)
        if var in l: l.remove(var)
        if G1Prefix in l: l.remove(G1Prefix)
            
        # prune 'l' here
        for i in l:
            #print("name: ", i) # uncomment for ckrs09 error
            typeI = sdl.getVarTypeFromVarName(i, None, True)
            #print("getVarTypeFromVarName:  ", i,":", typeI)
            if typeI == types.NO_TYPE:
                node = BinaryNode(ops.ATTR)
                node.setAttribute(i)
                #print("getVarNameFromListIndices req node: ", node)
                (funcName , newVarName) = getVarNameFromListIndices(assignInfo, varTypes, node, True)
                #print("funcName: ", funcName)
                #print("newVarName: ", newVarName)
                if newVarName != None: 
                    #print("newVarName := ", newVarName)
                    resultVarName = sdl.getVarTypeFromVarName(newVarName, None, True)
                    #print("second attempt: ", newVarName, ":", resultVarName)
                    varList.append(newVarName)              
                else:
                    pass
#                    print("JAA: ADDING to varList: ", i)
#                    varList.append(i)
            elif typeI in [types.G1]:
                varList.append(i)
            elif typeI in [types.ZR, types.list, types.pol]: #types.str,
                (name, varInf) = getVarNameEntryFromAssignInfo(assignInfo, i)
                if varInf.getIsUsedInHashCalc():
                    #print("adding", i, "to the list")
                    varList.append(str(i))
                    constraintList.append(str(var))
                continue
            else:
                pass
#                print("TODO: missing a case in buildMap: ", typeI)
                
#        varList.extend(l)
        varsToCheck = list(l)
        for i in varsToCheck:
            lenBefore = len(varList)
            buildMap(generators, varTypes, varList, i, constraintList)
            lenAfter  = len(varList)
            if lenBefore == lenAfter:
                node = BinaryNode(ops.ATTR)
                node.setAttribute(i)
                #print("Node :=>", node)
                (funcName, string) = getVarNameFromListIndices(assignInfo, varTypes, node, True)
                if string != None: varList.append(string)

#        for i in removeList:
#            print("REMOVING: ", i)
#            print("varList: ", varList)
            
    return    

class Generators:
    def __init__(self, info):
        self.generators = []
        self.genLines = {}
        self.genDict = {}
        self.info = info
        
    def extractGens(self, stmt, _types):
        lines = list(stmt.keys())
        lines.sort()
        for i in lines:
            if type(stmt[i]) == sdl.VarInfo and stmt[i].getHasRandomness() and Type(stmt[i].getAssignNode()) == ops.EQ:
                t = stmt[i].getAssignVar()
                if _types.get(t) == None:
                    typ = stmt[i].getAssignNode().right.left.attr
    #                print("Retrieved type directly: ", typ)
                else:
                    typ = _types[t].getType()
                if typ == types.G1:
                    if (stmt[i].getOutsideForLoopObj() != None): inForLoop = True
                    else: inForLoop = False
                    #print(i, ": ", typ, " :=> ", stmt[i].getAssignNode(), ", loop :=> ", inForLoop)
                    if not inForLoop: 
                        self.generators.append(str(stmt[i].getAssignVar()))
                    else:
                        listRef = stmt[i].getAssignVar().split(LIST_INDEX_SYMBOL)[0]
                        self.generators.append(listRef)
                        self.genDict[ listRef ] = str(stmt[i].getAssignVar()) #, str(stmt[i].getAssignNode()))   # str(stmt[i].getOutsideForLoopObj())
                        #print("genDict : ", self.genDict)
#                        startLine = stmt[i].getOutsideForLoopObj().getStartLineNo()
#                        endLine = stmt[i].getOutsideForLoopObj().getEndLineNo()+1
#                        newLines = sdl.getLinesOfCodeFromLineNos(list(range(startLine, endLine)))
#                        print("ForLoop content:\n", newLines)
#                        print("Stmt Interest: ", stmt[i].getAssignNode())
        return

    def setupNewGens(self):
        """derive generators used by the scheme using the following rules:
        1. first generator is selected as the base generator, "g". We split into two. 1 in G1 and other in G2.
        2. second generator and thereafter are defined in terms of base generator, g in both groups as follows (DH):
             h = random(ZR)
             hG1 = gG1 ^ h
             hG2 = gG2 ^ h
        3. TODO: need a way to prune which setup generators are used (a kind of optimization)
        """
        #genLines = []
        genMapG1 = {}
        genMapG2 = {}
    
        if len(self.generators) == 0:
            sys.exit("The scheme selects no generators in setup? Please try again.\n")    
        base_gen = self.generators[0]
        self.base_gen = base_gen
        # split the first generator
        base_genG1 = base_gen + G1Prefix
        base_genG2 = base_gen + G2Prefix
        baseG1 = BinaryNode(base_genG1)
        baseG2 = BinaryNode(base_genG2)

        self.genLines[ base_gen ] = []
        self.genLines[ base_gen ].append(BinaryNode(ops.EQ, baseG1, createTree("random(", "G1", None))) # base_genG1 + " := random(G1)")
        self.genLines[ base_gen ].append(BinaryNode(ops.EQ, baseG2, createTree("random(", "G2", None))) # base_genG2 + " := random(G2)")
        
        genMapG1[ base_gen ] = base_genG1
        genMapG2[ base_gen ] = base_genG2
        self.info['baseGeneratorG1'] = base_genG1
        self.info['baseGeneratorG2'] = base_genG2
        
        genOfList = self.genDict.keys()
        for j in range(1, len(self.generators)):
            i = self.generators[j]
            iNode = BinaryNode(i)
            expG1 = BinaryNode(ops.EXP, BinaryNode.copy(baseG1), BinaryNode.copy(iNode))
            expG2 = BinaryNode(ops.EXP, BinaryNode.copy(baseG2), BinaryNode.copy(iNode))
            if i not in genOfList: 
                # generator itself is not a list
                self.genLines[ i ] = []
                self.genLines[ i ].append(BinaryNode(ops.EQ, iNode, createTree("random(", "ZR", None))) # i + " := random(ZR)")
                self.genLines[ i ].append(BinaryNode(ops.EQ, BinaryNode(i + G1Prefix), expG1)) # i + G1Prefix + " := " + base_genG1 + " ^ " + i)
                self.genLines[ i ].append(BinaryNode(ops.EQ, BinaryNode(i + G2Prefix), expG2)) # i + G2Prefix + " := " + base_genG2 + " ^ " + i)
                
                genMapG1[ i ] = i + G1Prefix
                genMapG2[ i ] = i + G2Prefix
            elif i in genOfList:
                #print("setupNewGens: handle list => ", i)
                oldI = self.genDict[ i ] # 0 : old i
                self.genLines[ oldI ] = []
                self.genLines[ oldI ].append(BinaryNode(ops.EQ, iNode, createTree("random(", "ZR", None))) # (i + " := random(ZR)")
                self.genLines[ oldI ].append(BinaryNode(ops.EQ, BinaryNode(oldI.replace(i, i + G1Prefix)), expG1)) # (oldI.replace(i, i + G1Prefix) + " := " + base_genG1 + " ^ " + i)
                self.genLines[ oldI ].append(BinaryNode(ops.EQ, BinaryNode(oldI.replace(i, i + G2Prefix)), expG2)) # (oldI.replace(i, i + G2Prefix) + " := " + base_genG2 + " ^ " + i)
                genMapG1[ i ] = i + G1Prefix
                genMapG2[ i ] = i + G2Prefix                
            else: #elif i in genCond:
                pass
                #print("setupNewGens: handle conditionals => ", i)
                
#        print("....Start New Generators...")
#        for line in self.genLines:
#            print(line)
#        print("....End New Generators...")
        return (genMapG1, genMapG2)

    def getGens(self):
        return self.generators    
    
    def getGenLines(self):
        return self.genLines
        
def assignVarOccursInBoth(varName, info):
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

def assignVarOccursInG1(varName, info):
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

def assignVarOccursInG2(varName, info):
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


def assignVarIsGenerator(varName, info):
    generatorList = info['generators']
    return varName in generatorList

def handleListTypeRefs(varTypes, ref, info, isForBoth, groupType):
    global oldListTypeRefs, newListTypeRefs
    changeBack = None
    refDetails = ref.split(LIST_INDEX_SYMBOL)
    length = len(refDetails)
    if length == 2: # one level of indirection var#<int>
        refName = refDetails[0]
        refStr  = refDetails[1]
        if refStr.isdigit(): refNum = int(refDetails[1])
        else: return ref.replace(refName, refName + str(groupType))
    elif length == 3: # two level of indirection...var#*#<int>
        refName = refDetails[0]
        refStr  = refDetails[-1]
        if refStr.isdigit(): refNum = int(refDetails[-1]) # refNum 
        # look for "varName#*" type def
        #print("oldListTypeRefs: ", oldListTypeRefs.keys())
        searchRE = refName + "#." # try to match
        for i in oldListTypeRefs.keys():
            result = re.search(searchRE, i)
            if result:
                changeBack = ref[:-2] # cut off last two characters '#<int>'
                refName = result.group(0) # update the refName
                break

    else:
        print("JAA: can't handle reference lists of length %s yet." % length)
        return False
    oldVar = oldListTypeRefs.get(refName)
    if(oldVar != None): oldVar = oldVar[refNum]
    else: return ref
    
    if assignVarIsGenerator(oldVar, info) or assignVarOccursInBoth(oldVar, info):
       # look for either G1 or G2
       if groupType == types.G1: newRef = newListTypeRefs.get(refName).index(oldVar + G1Prefix)
       elif groupType == types.G2: newRef = newListTypeRefs.get(refName).index(oldVar + G2Prefix)
    else:
        # means either G1 or G2, we don't have to look for "_G?" extensions
        newRef = newListTypeRefs.get(refName).index(oldVar)
    
    if changeBack != None: refName = changeBack #TODO: handle this better in the future
    newRefName = refName + "#" + str(newRef)
    return newRefName

def prune(_list):
    # remove redundancies in list
    _list2 = list(set(_list))
    _list3 = []
    for i in _list2:
        if i.find(sdl.LIST_INDEX_SYMBOL) != -1:
            # chop off the '#' in the case of list references
            _list3.append(i.split(sdl.LIST_INDEX_SYMBOL)[0])
        else:
            _list3.append(i)
    # return the pruned list
    return _list3

def assignNewVar(assignVar, suffix):
    if assignVar.find(sdl.LIST_INDEX_SYMBOL) != -1:
        assignVar0 = assignVar.split(sdl.LIST_INDEX_SYMBOL)[0]
        return assignVar.replace(assignVar0, assignVar0 + suffix)
    return assignVar + suffix

def updateAllForBoth(node, assignVar, varInfo, info, changeLeftVar=True, noChangeList=[]):
    newLine1 = updateAllForG1(node, assignVar, varInfo, info, changeLeftVar, noChangeList)
    newLine2 = updateAllForG2(node, assignVar, varInfo, info, changeLeftVar, noChangeList)
    return [newLine1, newLine2]

def updateAllForG1(node, assignVar, varInfo, info, changeLeftVar, noChangeList=[]):
    varTypes = info['varTypes']
    varDeps = varInfo.getVarDepsNoExponents()
    new_node2 = BinaryNode.copy(node)
    # 1. assignVar
    if changeLeftVar: new_assignVar = assignNewVar(assignVar, G1Prefix) # new_assignVar = assignVar + G1Prefix
    else: new_assignVar = str(assignVar)
    sdl.ASTVisitor( SubstituteVar(assignVar, new_assignVar) ).preorder( new_node2 )
    info['generatorMapG1'][assignVar] = new_assignVar
    #info['usedVars'] = info['usedVars'].union([new_assignVar])
    # see if it is initCall:
    if varInfo.getInitCall() or varInfo.getHasRandomness():
        # make change and return here
        sdl.ASTVisitor( SubstituteVar('', str(types.G1), initChange=True) ).preorder( new_node2 )
        info['newTypes'][new_assignVar] = types.G1
        return new_node2

    info['myAsymSDL'].recordUsedVar(varDeps)                
    
    prunedList = prune(noChangeList)
    newVarDeps = set(varDeps).difference(prunedList, Gtypes)
    for i in newVarDeps:
        new_i = i + G1Prefix
        updatedRefAlready = False
        if i.find(sdl.LIST_INDEX_SYMBOL) != -1: 
            newRef = handleListTypeRefs(varTypes, i, info, changeLeftVar, types.G1)
            if newRef == False: print("ERROR in handleListTypeRefs"); return
            elif newRef == i: continue # meaning no change in reference 
            else: new_i = newRef; updatedRefAlready = True
        
        if not updatedRefAlready:
            v = varTypes.get(i)
            if v != None: v = v.getType()
            else: print("FIX: no type for G1: ", i); sys.exit(0)
            # prune (as a second effort)
            if v in [types.ZR, types.listZR, types.int, types.listInt, types.str, types.listStr]: 
                continue

        sdl.ASTVisitor( SubstituteVar(i, new_i) ).preorder( new_node2 )
        info['generatorMapG1'][i] = new_i
        info['usedVars'] = info['usedVars'].union([new_i])
        info['myAsymSDL'].recordUsedVar([new_i])
        info['newTypes'][new_i] = types.G1
    #print("\n\tChanged: ", new_node2, end="")
    return new_node2

def updateAllForG2(node, assignVar, varInfo, info, changeLeftVar, noChangeList=[]):
    varTypes = info.get('varTypes')  
    varDeps = varInfo.getVarDepsNoExponents()  
    new_node2 = BinaryNode.copy(node)
    # 1. assignVar
    if changeLeftVar: new_assignVar = assignNewVar(assignVar, G2Prefix) # new_assignVar = assignVar + G2Prefix
    else: new_assignVar = str(assignVar)
    sdl.ASTVisitor( SubstituteVar(assignVar, new_assignVar) ).preorder( new_node2 )
    info['generatorMapG2'][assignVar] = new_assignVar    
    #info['usedVars'] = info['usedVars'].union([new_assignVar])    
    # see if it is initCall:
    if varInfo.getInitCall() or varInfo.getHasRandomness():
        # make change and return here
        sdl.ASTVisitor( SubstituteVar('', str(types.G2), initChange=True) ).preorder( new_node2 )
        info['newTypes'][new_assignVar] = types.G2        
        return new_node2
    
    info['myAsymSDL'].recordUsedVar(varDeps)                
        
    prunedList = prune(noChangeList)
    newVarDeps = set(varDeps).difference(prunedList, Gtypes)
    for i in newVarDeps:
        new_i = i + G2Prefix
        updatedRefAlready = False
        if i.find(sdl.LIST_INDEX_SYMBOL) != -1: # detect references such as <var>#<int> which are treated like indirect pointers
            newRef = handleListTypeRefs(varTypes, i, info, changeLeftVar, types.G2)
            if newRef == False: print("ERROR in handleListTypeRefs"); return
            elif newRef == i: continue # meaning no change in reference
            else: new_i = newRef; updatedRefAlready = True
            
        if not updatedRefAlready:   
            v = varTypes.get(i)
            if v != None: v = v.getType()
            else: print("FIX: no type for G2: ", i); sys.exit(0)            
            # prune (as a second effort)
            if v in [types.ZR, types.listZR, types.int, types.listInt, types.str, types.listStr]: 
                continue
        sdl.ASTVisitor( SubstituteVar(i, new_i) ).preorder( new_node2 )
        info['generatorMapG2'][i] = new_i
        info['usedVars'] = info['usedVars'].union([new_i])
        info['myAsymSDL'].recordUsedVar([new_i])
        info['newTypes'][new_i] = types.G2        
    #print("\n\tChanged: ", new_node2, end="")
    return new_node2

def updateForLists(varInfo, assignVar, info):
    global oldListTypeRefs, newListTypeRefs
    newList = []
    inBoth = info['both']
    orig_list = varInfo.getAssignNode().getRight().listNodes
    oldListTypeRefs[ str(assignVar) ] = list(orig_list) # record the original list

    for i in orig_list:
        if i in inBoth or assignVarIsGenerator(i, info):
            newList.extend([i + G1Prefix, i + G2Prefix])
        else:
            newList.append(i)
    new_node = BinaryNode.copy(varInfo.getAssignNode())
    new_node.right.listNodes = newList
    #print("\n\tnewList: ", new_node)
    newListTypeRefs[ str(assignVar) ] = list(newList) # record the updates
    return new_node

def updateForPairing(varInfo, info, noChangeList):
    node = BinaryNode.copy(varInfo.getAssignNode())
    tme = TestForMultipleEq()
    sdl.ASTVisitor(tme).preorder(node)
    if tme.multiple:
        gen = GetEquqlityNodes()
        sdl.ASTVisitor( gen ).preorder(node)
        listOfNodes = gen.getNodes()
        for i in listOfNodes:
            tmp = applyPairingUpdate(info, i, noChangeList) # pass reference to eq_tst nodes
        #print("\n\t Final: ", node)
        return node
    
    return applyPairingUpdate(info, node, noChangeList)

def applyPairingUpdate(info, node, noChangeList):
    sp = SubstitutePairings(info, noChangeList)
    sdl.ASTVisitor( sp ).preorder( node )
    info['usedVars'] = info['usedVars'].union(sp.getUsedGens())
    info['myAsymSDL'].recordUsedVar(GetAttributeVars(node)) # sp.getUsedVars())    
    #print("\n\t Pre techs: ", node, end="")
    sdl.ASTVisitor( MaintainOrder(info) ).preorder( node )    
    # combining pairing logic a bit.
    while True:
        tech6 = PairInstanceFinderImproved()
        sdl.ASTVisitor(tech6).preorder( node )
        if tech6.testForApplication(): 
            tech6.makeSubstitution( node )
        else:
            break

    #print("\n\t Changed: ", node)
    return node

def print_sdl(verbose, *args):
    if verbose:
        print("<===== new SDL =====>")    
        for block in args:
            for i in block:
                print(i)
            print("\n\n")
        print("<===== new SDL =====>")
    return
    

def writeConfig(filename, *args):
    f = open(filename, 'w')
    for block in args:
        for line in block:
            if type(line) == list:
                for subLine in line:
                    f.write(str(subLine) + "\n")
                if len(line) > 0: f.write('\n')
            else:
                f.write(str(line) + "\n")
        if len(block) > 0: f.write('\n') # in case block = [] (empty)
    f.close()
    return
    