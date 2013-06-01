from z3 import *
from SDLang import *
import SDLParser2 as sdl

Group, (Str, sInt, ZR, G1, G2, GT, pol, Nil) = EnumSort('GroupType', ('Str', 'sInt', 'ZR', 'G1', 'G2', 'GT', 'pol', 'Nil'))

exp = Function('exp', Group, Group, Group)
mul = Function('mul', Group, Group, Group)
div = Function('div', Group, Group, Group)
add = Function('add', Group, Group, Group)
sub = Function('sub', Group, Group, Group)
sym_pair = Function('sympair', Group, Group, Group)
asym_pair = Function('asympair', Group, Group, Group)

# define basic data structure for SDL
listPrefix = "list"
metalistPrefix = "metalist"
listStr = K(IntSort(), Str)
listInt = K(IntSort(), sInt)
# JAA: do we need another version in which keys can be "Str" types?
listZR = K(IntSort(), ZR)
listG1 = K(IntSort(), G1)
listG2 = K(IntSort(), G2)
listGT = K(IntSort(), GT)
symmapZR = K(IntSort(), ZR)

metalistStr = K(IntSort(), listStr)
metalistInt = K(IntSort(), listInt)
metalistZR = K(IntSort(), listZR)
metalistG1 = K(IntSort(), listG1)
metalistG2 = K(IntSort(), listG2)
metalistGT = K(IntSort(), listGT)

stdTypes = {'sInt':'Int', 'Str':'Str'}

mapGroup = {'Str':Str, 'sInt':sInt, 'ZR':ZR, 'G1':G1, 'G2':G2, 'GT':GT,'Nil':Nil,\
            'listStr':listStr, 'listInt':listInt, 'listZR':listZR, 'listG1':listG1, 'listG2':listG2, 'listGT':listGT,\
            'metalistStr':metalistStr, 'metalistInt':metalistInt, 'metalistZR':metalistZR, 'metalistG1':metalistG1, 'metalistG2':metalistG2, 'metalistGT':metalistGT, \
            'symmapZR':symmapZR, 'pol':pol, 'Int':sInt } # last two are for consistency with SDL types (should make them match though)

groupToInt = ['Str', 'sInt', 'ZR', 'G1', 'G2', 'GT', 'listStr', 'listInt', 'listZR', 'listG1', 'listG2', 'listGT', 'Nil']

# will be created uniquely for each list type variable
# listArray = Array("varName", IntSort(), Group)

def buildList(var, listTypes):
    cond = []
    for i in listTypes:
        assert i in mapGroup.keys(), "specified invalid SDL type"
        cond.append( var == mapGroup[i] )
    return cond

class TypeCheck:
    def __init__(self, varType, setting=None, verbose=False):
        self.varType    = dict(varType) # make copy
        self.sdlVarType = {}
        self.setting = setting
        self.verbose = verbose
        self.__varCount  = 0
        self.listModel   = {}
        self.listVarType = {}
    
    def setSetting(self, setting):
        if setting == SYMMETRIC_SETTING:
            self.setting = SYMMETRIC_SETTING
        elif setting == ASYMMETRIC_SETTING:
            self.setting = ASYMMETRIC_SETTING
        return
    
    def getSDLVarType(self):
        return self.sdlVarType
    
    def getVarType(self):
        return self.varType
        
    def __getTypeModel(self):        
        x, y = Consts('x y', Group)
        # rules for exponentiation 
        exp_axioms = [ ForAll([x, y], Implies(And(Or(buildList(x, ['sInt', 'ZR', 'G1', 'G2', 'GT'])), Or(buildList(y, ['sInt', 'ZR']))), exp(x, y) == x)),
                       ForAll([x, y], Implies(Or(buildList(y, ['Str', 'G1', 'G2', 'GT', 'pol', 'Nil'])), exp(x, y) == Nil)) ]
        
        # rules for mul, div, add, sub
        mul_axioms = [ ForAll([x, y], Implies(And(x == y, Or(buildList(x, ['sInt', 'ZR', 'G1', 'G2', 'GT']))), mul(x, y) == x)), 
                       ForAll([x, y], Implies(x != y, mul(x, y) == Nil)) ]
        
        div_axioms = [ ForAll([x, y], Implies(And(x == y, Or(buildList(x, ['sInt', 'ZR', 'G1', 'G2', 'GT']))), div(x, y) == x)), 
                       ForAll([x, y], Implies(x != y, div(x, y) == Nil)) ]
        
        add_axioms = [ ForAll([x, y], Implies(And(x == y, Or(buildList(x, ['sInt', 'ZR', 'G1', 'G2', 'GT']))), add(x, y) == x)), 
                       ForAll([x, y], Implies(x != y, add(x, y) == Nil)) ]
        
        sub_axioms = [ ForAll([x, y], Implies(And(x == y, Or(buildList(x, ['sInt', 'ZR', 'G1', 'G2', 'GT']))), sub(x, y) == x)), 
                       ForAll([x, y], Implies(x != y, sub(x, y) == Nil)) ]
        
        asym_axioms = [ ForAll([x, y], Implies(And(x == G1, y == G2), asym_pair(x, y) == GT)),
                        ForAll([x, y], Implies(Or(And(x == G1, y != G2), And(x != G1, y == G2)), 
                                               asym_pair(x, y) == Nil)) ]
        sym_axioms = [ ForAll([x, y], Implies(And(x == G1, y == G1), sym_pair(x, y) == GT)),
                       ForAll([x, y], Implies(Or(And(x != G1, y == G1), And(x == G1, y != G1)), sym_pair(x, y) == Nil)) ] 
                    
        self.solver = Solver()
        self.solver.add( exp_axioms )
        self.solver.add( mul_axioms )
        self.solver.add( div_axioms )
        self.solver.add( add_axioms )
        self.solver.add( sub_axioms )
        self.solver.add( sym_axioms )        
        self.solver.add( asym_axioms )

        satisfy = self.solver.check()
        print("satisfiable: ", satisfy)
        if satisfy == unsat:
            return False
    
        return True
    
    def __updateModel(self, forceCheck=True):
        assert self.solver != None, "Solver is None!"
        if forceCheck:
            print("Checking....")
            if self.solver.check() == unsat:
                print("ERROR: unsatisfiable model")
                sys.exit(-1)
            print("Done!")
        self.TypeModel = self.solver.model()
    
    def checkModel(self, binNode, forceCheck=False):
        self.__updateModel(forceCheck)
        return self.TypeModel.evaluate(binNode)
    
    def setupSolver(self):
        if self.__getTypeModel():
            # already checked at this point
            self.__updateModel(forceCheck=False)
        else:
            print("Unsatisfiable axioms for SDL language.")
            sys.exit(-1)
        if self.verbose: print(self.solver)
        M = self.TypeModel
        if self.verbose: print(M)
        print()
        print("Test 1: ", M.evaluate(exp(ZR, ZR)))
        print("Test 2: ", M.evaluate(exp(G1, ZR)))
        print("Test 3: ", M.evaluate(exp(G2, ZR)))
        print("Test 4: ", M.evaluate(exp(GT, ZR)))
        print("Test 5: ", M.evaluate(exp(GT, GT)))
        print("Test 6: ", M.evaluate(exp(ZR, sInt)))
        
        #result = M.evaluate(exp(x, G1))
        print("Test 6: ", M.evaluate(mul(ZR, ZR)))
        print("Test 7: ", M.evaluate(mul(G1, G1)))
        print("Test 8: ", M.evaluate(mul(G1, ZR)))
        print("Test 8: ", M.evaluate(mul(sInt, ZR)))
        
        return
    
    def __convertTypeToZ3(self, sdlType):
        """expects sdlType in the form of a string"""
        for k,v in stdTypes.items():
            if sdlType == v:
                return k
        return sdlType
    
    def __getUniqueRef(self):
        self.__varCount += 1
        return listPrefix + str(self.__varCount) 
    
    def __buildRefRule(self, refName, index, typeVar):
        keyType = str(typeVar)
        if keyType in groupToInt:
            typeInt = groupToInt.index(keyType)
        else:
            # attempt #2 : perhaps, one of the list or metalist types
            keyType2 = str(self.__computeDataType(typeVar))
            if keyType2 in groupToInt:
                typeInt = groupToInt.index(keyType2)
            else:
                print("missing keyType: ", keyType)
                sys.exit(-1)
        return refName[index] == typeInt
    
    def __buildZ3Expression(self, node, lhs, varType):
        if node == None: return None
        if node.left != None: leftNode   = self.__buildZ3Expression(node.left, lhs, varType)
        if node.right != None: rightNode = self.__buildZ3Expression(node.right, lhs, varType)
        
        # visit the root
        if (Type(node) == ops.TYPE):
            the_type = self.__convertTypeToZ3(str(node.attr))
            if the_type not in mapGroup.keys():
                print("Invalid type: ", the_type, str(node.attr)); return Nil
            return mapGroup.get(the_type)
        elif Type(node) == ops.RANDOM:
            retRandomType = str(node.getLeft().attr)
            return mapGroup.get(retRandomType)
        elif Type(node) == ops.HASH:
            retHashType = str(node.getRight().attr)
            return mapGroup.get(retHashType)
        elif Type(node) == ops.ON:
            return rightNode
        elif Type(node) == ops.EXPAND:
            return Nil        
        elif Type(node) == ops.LIST: # JAA: Document these type semantics
            # create rules for this particular list instance in SDL
            listRules = []
            refName = self.__getUniqueRef()
            refHandle = Array(refName, IntSort(), IntSort())
            for i,j in enumerate(node.listNodes):
                # get the type of i
                if j in varType.keys():
                    listRules.append( self.__buildRefRule(refHandle, i, varType.get(j)) ) # ref[i] == typeOF j
                else:
                    print("Missing type annotation for: ", j)
                    sys.exit(-1)
            lenList = len(node.listNodes)
            k = Int('k')
            listRules.append( ForAll(k, Implies(Or(k > lenList, k == lenList), refHandle[k] == groupToInt.index('Nil'))) )
            new_solver = Solver()
            new_solver.add( listRules )
            assert new_solver.check() == sat, "ERROR" 
            lhsStr = str(lhs)
            # map creation of list type object with lhs variable 
            if LIST_INDEX_SYMBOL not in lhsStr:
                self.listModel[ lhsStr ] = new_solver.model()
                self.listVarType[ lhsStr ] = refHandle
                groupToInt.append( str(refHandle) )
                mapGroup[ str(refHandle) ] = refHandle # type definition
                #print(refHandle, " => Solver: ", new_solver)
            else:
                # JAA: untested for now
                _list = lhsStr.split(LIST_INDEX_SYMBOL)
                reflhsStr = _list[0] # get the ref name
                assert len(_list[1:]) == 1, "var#x#y not supported on lhs with a LIST on rhs assignment. Please correct."
                self.listModel[ reflhsStr ] = new_solver.model()
                refHandle2 = K(IntSort(), refHandle)
                self.listVarType[ reflhsStr ] = refHandle2
                groupToInt.append( str(refHandle2) )
                mapGroup[ str(refHandle2) ] = refHandle2 # type definition
                return refHandle2

            return refHandle
        # idea is to verify that both sides have thesame type, so we use the equal operator in Z3
        elif Type(node) in [ops.EQ, ops.EQ_TST, ops.NON_EQ_TST]: 
            return (leftNode == rightNode)
        elif Type(node) == ops.OR:
            return Or(leftNode, rightNode)
        elif Type(node) == ops.AND:
            return And(leftNode, rightNode)
        elif Type(node) == ops.PAIR:
            if self.setting == SYMMETRIC_SETTING:
                return sym_pair(leftNode, rightNode)
            elif self.setting == ASYMMETRIC_SETTING:
                return asym_pair(leftNode, rightNode)
            else:
                print("TypeCheck: Setting was not specified and using PAIRING.")
                sys.exit(-1)
        elif Type(node) == ops.ADD:
            return add(leftNode, rightNode)
        elif Type(node) == ops.SUB:
            return sub(leftNode, rightNode)
        elif Type(node) == ops.MUL:
            return mul(leftNode, rightNode)
        elif Type(node) == ops.DIV:
            return div(leftNode, rightNode)
        elif Type(node) == ops.EXP:
            return exp(leftNode, rightNode)
        elif Type(node) == ops.ATTR:
            varName = str(node).split(LIST_INDEX_SYMBOL)[0]
            theType = self.computeAttrType(varName, varType)
            if varName.isdigit():
                return theType
            else:
                return self.contextType(node, varType) # in case it has a '#' symbol
        elif Type(node) == ops.CONCAT:
            return listStr
        elif Type(node) == ops.STRCONCAT:
            return Str            
        elif Type(node) == ops.FUNC:
            currentFuncName = getFullVarName(node, False)
            if (currentFuncName in sdl.builtInTypes):
                print("mapGroup type for: ", currentFuncName, " := ", str(sdl.builtInTypes[currentFuncName]))
                return mapGroup.get( str(sdl.builtInTypes[currentFuncName]) )
            elif (currentFuncName == INIT_FUNC_NAME):
                initType = str(node.listNodes[0])
                print("initType : ", initType)
                if (initType.isdigit() == True):
                    return ZR # by default, must cast down for Int operations
                elif initType in mapGroup.keys():
                    return mapGroup.get(initType)
                else:
                    return Nil
            elif (currentFuncName == KEYS_FUNC_NAME):
                return mapGroup.get("listInt") # default
            elif (currentFuncName == LEN_FUNC_NAME):
                return sInt
            print("ERROR: require type annotation for func: ", currentFuncName); sys.exit(-1)
            return Nil # Error
        else:
            print("NodeType unsupported: ", Type(node))
            return None
    
    def contextType(self, attrNode, varType):
        print("attrNode: ", attrNode)
        attrName = str(attrNode)
        if attrName == "-1": return sInt
        if "-" in attrName: attrName = attrName.replace("-", "")
        
        name = attrName.split(LIST_INDEX_SYMBOL)[0]
        Model = None
        # 1. check if specific model exists for given attrNode
        if name in self.listModel.keys():
            # check this first b/c the variable also occur in the varType dictionary
            refName = self.listVarType[ name ]
            Model = self.listModel[ name ] # use list specific model
        # 2. if option 1 fails, then check if varType entry exists for attrNode
        elif name in varType.keys():
            # retrieve type handle and use the default model to evaluate it
            refName = varType[ name ]
            Model = self.TypeModel
        else:
            # otherwise, this is an error!
            print("Could not find ref for: ", name); sys.exit(-1)
            
        countHash = len(attrName.split(LIST_INDEX_SYMBOL))-1
        if countHash == 0: # basic case
            return refName
        elif countHash == 1:
            arg = attrName.split(LIST_INDEX_SYMBOL)[-1]
            assert Model != None, "Cannot find model for var: %s" % name
            if arg.isdigit():
                return self.convertType( Model.evaluate(refName[ int(arg) ]) ) # concrete reference
            else:
                return self.convertType( Model.evaluate( refName[ Int(arg) ]) ) # abstract reference
        elif countHash == 2:
            arg1, arg2 = attrName.split(LIST_INDEX_SYMBOL)[-2:]
            assert Model != None, "Cannot find model for var: %s" % name
            isArg1Digit = arg1.isdigit()
            isArg2Digit = arg2.isdigit()
            if isArg1Digit and isArg2Digit:
                return self.convertType( Model.evaluate(refName[ int(arg1) ][ int(arg2) ]) ) # concrete reference
            elif not isArg1Digit and isArg2Digit:
                return self.convertType( Model.evaluate( refName[ Int(arg1) ][ int(arg2) ]) ) # abstract reference
            elif isArg1Digit and not isArg2Digit:
                return self.convertType( Model.evaluate( refName[ int(arg1) ][ Int(arg2) ]) ) # last reference is abstract
            elif not isArg1Digit and not isArg2Digit:
                return self.convertType( Model.evaluate( refName[ Int(arg1) ][ Int(arg2) ]) ) # both references are abstract

        return None
        
    def computeAttrType(self, varName, varType):
        if varName == "-1": return ZR
        if "-" in varName: varName = varName.replace("-", "")
        
        if not varName.isdigit():
            if varName in varType.keys():
                return varType.get(varName)
            else:
                 print("Need type annotation: ", varName, " := NO_TYPE")
                 sys.exit(-1)
        else:
            return ZR # by default, must specifically add Int() call to convert type
    
    def convertType(self, evalType):
        evalTypeStr = str(evalType)
        print("evalTypeStr: ", evalTypeStr)
        if evalTypeStr.isdigit():
            key = groupToInt[int(evalTypeStr)]
            if key in mapGroup.keys():
                return mapGroup[ key ]
            else:
                print("convertType: missing key := ", key)
                sys.exit(-1)
        return evalType
    
    def __computeDataType(self, z3_type):
        """ highly tied to structure of string representation in Z3 Types. Maps Z3 types to SDL types."""
        sdlType = types.NO_TYPE
        sortString = str(z3_type.sort())
        the_type = str(z3_type)
        listLevel = sortString.count('Array(')        
        if listLevel == 0:
            if the_type not in stdTypes.keys():
                return types[the_type]
            else:
                return types[ stdTypes[the_type] ]
        elif listLevel == 1:
            #print("LIST: ", listLevel, the_type)
            if listPrefix in the_type:
                 return types.list
            else:
                the_type = str(z3_type.children()[0])
                return types[listPrefix + the_type]
        elif listLevel == 2:
            #print("METALIST: ", listLevel)
            if listPrefix in the_type:
                 return types.metalist
            else:
                the_type = str(z3_type.children()[0])
                return types[metalistPrefix + the_type]
        return sdlType

    def __buildSDLType(self, node):
        """interprets type annotations in TYPES header of SDL and maps to Z3 data types counterpart"""
        if node == None: return None
        if node.left != None: leftNode   = self.__buildZ3Expression(node.left, lhs, varType)
        if node.right != None: rightNode = self.__buildZ3Expression(node.right, lhs, varType)
        
        if Type(node) == ops.TYPE:
            the_type = str(node.attr)
            the_type2 = self.__convertTypeToZ3( the_type )
            if the_type2 == listPrefix: return # handled properly later 
            return mapGroup.get( the_type2 )
        elif Type(node) == ops.LIST:
            print("LIST TYPE: ", node, ) # TODO: handle metalists
            the_type = self.__convertTypeToZ3(node.listNodes[0])
            return mapGroup.get( listPrefix + str(the_type) )
        elif Type(node) == ops.ATTR: 
            print("Undefined type: ", node)
        return
    
    def processTypeAnnotations(self, binNode):
        if Type(binNode) == ops.EQ:
            lhsStr = str(binNode.getLeft())
            the_type = self.__buildSDLType(binNode.getRight())
            if the_type != None:                
                print("ANNOTATED TYPE: ", lhsStr, " => ", the_type)
                self.varType[ lhsStr ] = the_type
        return
    
    def evaluateType(self, binNode):
        if Type(binNode) != ops.EQ:
            z3Nodes = self.__buildZ3Expression(binNode.getLeft(), None, self.varType)
            print("DEBUG: Z3 expression = ", z3Nodes)
            new_type = self.TypeModel.evaluate(z3Nodes)
            if str(new_type) == 'True': return True
            elif str(new_type) == 'False': return False
        elif Type(binNode) == ops.EQ:
            z3Nodes = self.__buildZ3Expression(binNode, None, self.varType)
            print("DEBUG: Z3 expression = ", z3Nodes)
            new_type = self.TypeModel.evaluate(z3Nodes)
            print("TESTING ==> Final output: ", new_type); sys.exit(-1)
        return
        
    def inferType(self, binNode): 
        #print("DEBUG: Node Type = ", Type(binNode))
        if Type(binNode) == ops.EQ:
            lhsStr = str(binNode.getLeft())
            if lhsStr in [inputKeyword, outputKeyword]: return
            #print("DEBUG: original node = ", binNode)
            z3Nodes = self.__buildZ3Expression(binNode.getRight(), binNode.getLeft(), self.varType)
            print("DEBUG: Z3 expression = ", z3Nodes)
            if lhsStr in self.listModel.keys():
#                new_type = self.convertType(self.listModel[lhsStr].evaluate(z3Nodes))
                if LIST_INDEX_SYMBOL in lhsStr: lhsStr = lhsStr.split(LIST_INDEX_SYMBOL)[0] # JAA: may need to do other things here
                new_type = self.listVarType[ lhsStr ]
            else:
                new_type = self.TypeModel.evaluate(z3Nodes)

            print("DEBUG: Inferred Type = ", new_type)
            varName = str(binNode.left)
            sortString = str(new_type.sort())
            listLevel = sortString.count('Array')
            isAList = True if listLevel == 1 else False
            isMetaList = True if listLevel == 2 else False
            # JAA: dealing with LHS :=> var#x := g
            # 1. look up var#x
            # 2. then remove, then add a rule for index 'x' iff int => re-run Model?
            # 3. does this work?
            
            #if varName == "pk": x = Int('x'); print("Test: ", str(new_type), self.TypeModel.evaluate(new_type[0]), self.TypeModel.evaluate(new_type[1]))
            if LIST_INDEX_SYMBOL in varName:
                # evaluate the equation          
                listKey = varName.split(LIST_INDEX_SYMBOL)[0]                
                if listKey in self.varType.keys():
                    LHSType = self.contextType(binNode.left, self.varType)
                    if LHSType.eq( new_type ):
                        print("Type OK!")
                    else:
                        print("ERROR: Type mismatch in SDL statement!")
                        sys.exit(-1)
                elif isAList or isMetaList:
                    self.varType[ listKey ] = new_type
                    self.sdlVarType[ listKey ] = self.__computeDataType(new_type) # to map back to original SDL types                    
                else:
                    print("Missing type annotation for: ", listKey)
                    print("Inferred Type 2: ", new_type.sort())
                    sys.exit(-1)
            else:
                self.varType[varName] = new_type
                self.sdlVarType[varName] = self.__computeDataType(new_type) # to map back to original SDL types
                # check context of LHS assignment: 


if __name__ == "__main__":
    varType = {} #{'tf0':listG1, 'tf1':listG1}
    tc = TypeCheck(varType)
    tc.setupSolver()
    parser = sdl.SDLParser()
    args = sys.argv[1:]
    for i in args:
        binNode = parser.parse(i)
        tc.inferType(binNode)
    
    print("VarTypes:\t", tc.getVarType())
    print()
    print("SDL VarTypes:\t", tc.getSDLVarType())
