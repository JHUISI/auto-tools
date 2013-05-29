from z3 import *
from SDLang import *
import SDLParser as sdl

#Group, (sInt, ZR, G1, G2, GT, Nil) = EnumSort('GroupType', ('sInt', 'ZR', 'G1', 'G2', 'GT', 'Nil'))
Group, (Str, sInt, ZR, G1, G2, GT, Nil) = EnumSort('GroupType', ('Str', 'sInt', 'ZR', 'G1', 'G2', 'GT', 'Nil'))

#, listType, listStr, listInt, listZR, listG1, listG2, listGT, metalist, metalistStr, metalistInt, metalistZR, metalistG1, metalistG2, metalistGT, Nil) = \
#    EnumSort('GroupType', ('Str','sInt', 'ZR', 'G1', 'G2', 'GT', 'list', 'listStr', 'listInt', 'listZR', 'listG1', 'listG2', 'listGT', \
#                           'metalist', 'metalistStr', 'metalistInt', 'metalistZR', 'metalistG1', 'metalistG2', 'metalistGT','Nil'))

#'list':listType, 'listStr':listStr, 'listInt':listInt, 'listZR':listZR, 'listG1':listG1, 'listG2':listG2, 'listGT':listGT, 
#            'metalist':metalist, 'metalistStr':metalistStr, 'metalistInt':metalistInt, 'metalistZR':metalistZR, 'metalistG1':metalistG1, 'metalistG2':metalistG2, 'metalistGT':metalistGT}

exp = Function('exp', Group, Group, Group)
mul = Function('mul', Group, Group, Group)
div = Function('div', Group, Group, Group)
add = Function('add', Group, Group, Group)
sub = Function('sub', Group, Group, Group)
sym_pair = Function('sympair', Group, Group, Group)
asym_pair = Function('asympair', Group, Group, Group)

# define basic data structure for SDL
listStr = K(IntSort(), Str)
listInt = K(IntSort(), sInt)
listZR = K(IntSort(), ZR)
listG1 = K(IntSort(), G1)
listG2 = K(IntSort(), G2)
listGT = K(IntSort(), GT)

metalistStr = K(IntSort(), listStr)
metalistInt = K(IntSort(), listInt)
metalistZR = K(IntSort(), listZR)
metalistG1 = K(IntSort(), listG1)
metalistG2 = K(IntSort(), listG2)
metalistGT = K(IntSort(), listGT)


mapGroup = {'Str':Str, 'sInt':sInt, 'ZR':ZR, 'G1':G1, 'G2':G2, 'GT':GT,'Nil':Nil,\
            'listStr':listStr, 'listInt':listInt, 'listZR':listZR, 'listG1':listG1, 'listG2':listG2, 'listGT':listGT,\
            'metalistStr':metalistStr, 'metalistInt':metalistInt, 'metalistZR':metalistZR, 'metalistG1':metalistG1, 'metalistG2':metalistG2, 'metalistGT':metalistGT}

#intToGroup = {0:'Str', 1:'sInt', 2:'ZR', 3:'G1', 4:'G2', 5:'GT',\
#            6:'listStr', 7:'listInt', 8:'listZR', 9:'listG1', 10:'listG2', 11:'listGT',\
#            12:'metalist', 13:'metalistStr', 14:'metalistInt', 15:'metalistZR', 16:'metalistG1', 17:'metalistG2', 18:'metalistGT', 19:'Nil'}

groupToInt = ['Str', 'sInt', 'ZR', 'G1', 'G2', 'GT', 'listStr', 'listInt', 'listZR', 'listG1', 'listG2', 'listGT', 'Nil']

# will be created uniquely for each list type variable
# listArray = Array("varName", IntSort(), Group)

def buildList(var, listTypes):
    cond = []
    for i in listTypes:
        assert i in mapGroup.keys(), "specified invalid SDL type"
        cond.append( var == mapGroup[i] )
    return cond

#def buildRefRule(refName, index, typeVar):
#    keyType = str(typeVar)
#    if keyType in groupToInt:
#        typeInt = groupToInt.index(keyType)
#    else:
#        print("missing keyType: ", keyType)
#        sys.exit(-1)
#    return refName[index] == typeInt
    
#isZR = Function('isZR', Group, Group)
#isGroup = Function('isGroup', Group, Group)
class TypeCheck:
    def __init__(self, setting=None, verbose=False):
        self.setting = setting
        self.verbose = verbose
        self.__varCount  = 0
        self.listModel   = {}
        self.listVarType = {}
    
    def __getTypeModel(self):        
        x, y = Consts('x y', Group)
        # rules for exponentiation 
        exp_axioms = [ ForAll([x, y], Implies(And(Or(buildList(x, ['sInt', 'ZR', 'G1', 'G2', 'GT'])), Or(buildList(y, ['sInt', 'ZR']))), exp(x, y) == x)),
                       ForAll([x, y], Implies(Or(buildList(y, ['Str', 'G1', 'G2', 'GT', 'Nil'])), exp(x, y) == Nil)) ]
        
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
                       ForAll([x, y], Implies(And(x != G1, y != G1), sym_pair(x, y) == Nil)) ] 
        
#        axioms = [ ForAll(x, Implies(x == listG1, refDown(x) == G1)),
#                   ForAll(x, Implies(x == listG2, refDown(x) == G2)),
#                   ForAll(x, Implies(x == listGT, refDown(x) == GT)),
#                   ForAll(x, Implies(x == listZR, refDown(x) == ZR)),
#                   ForAll(x, Implies(x == listInt, refDown(x) == sInt)),           
#                   ForAll(x, Implies(x == listStr, refDown(x) == Str)),
#                   ForAll(x, Implies(x == metalist, refDown(x) == listType)),                   
#                   ForAll(x, Implies(x == metalistStr, refDown(x) == listStr)),            
#                   ForAll(x, Implies(x == metalistZR, refDown(x) == listZR)), 
#                   ForAll(x, Implies(x == metalistG1, refDown(x) == listG1)), 
#                   ForAll(x, Implies(x == metalistG2, refDown(x) == listG2)), 
#                   ForAll(x, Implies(x == metalistGT, refDown(x) == listGT)),            
#                   ForAll(x, Implies(Or(buildList(x, ['sInt', 'ZR', 'G1', 'G2', 'GT', 'list', 'Nil'])), refDown(x) == Nil)) ]
            
        self.solver = Solver()
        self.solver.add( exp_axioms )
        self.solver.add( mul_axioms )
        self.solver.add( div_axioms )
        self.solver.add( add_axioms )
        self.solver.add( sub_axioms )
        if self.setting == SYMMETRIC_SETTING:
            self.solver.add( sym_axioms )        
        elif self.setting == ASYMMETRIC_SETTING:
            self.solver.add( asym_axioms )
        #s.add( axioms )
        #print(s)
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
        print("\nTest 1: ", M.evaluate(exp(ZR, ZR)))
        print("Test 2: ", M.evaluate(exp(G1, ZR)))
        print("Test 3: ", M.evaluate(exp(G2, ZR)))
        print("Test 4: ", M.evaluate(exp(GT, ZR)))
        print("Test 5: ", M.evaluate(exp(GT, GT)))
        print("Test 6: ", M.evaluate(exp(ZR, sInt)))
        
        #result = M.evaluate(exp(x, G1))
        print("Test 6: ", M.evaluate(mul(ZR, ZR)))
        print("Test 7: ", M.evaluate(mul(G1, G1)))
        print("Test 8: ", M.evaluate(mul(G1, ZR)))
        #print("Test 9: ", M.evaluate(mul(G1, refDown(listG1))))
        #print("Test 10: ", M.evaluate(mul(Str, refDown(refDown(metalistStr)))))
    
    def __getUniqueRef(self):
        self.__varCount += 1
        return "list" + str(self.__varCount) 
    
    def __buildRefRule(self, refName, index, typeVar):
        keyType = str(typeVar)
        if keyType in groupToInt:
            typeInt = groupToInt.index(keyType)
        else:
            print("missing keyType: ", keyType)
            sys.exit(-1)
        return refName[index] == typeInt

    
    def __buildZ3Expression(self, node, lhs, varType):
        if node == None: return None
        if node.left != None: leftNode   = self.__buildZ3Expression(node.left, lhs, varType)
        if node.right != None: rightNode = self.__buildZ3Expression(node.right, lhs, varType)
        
        # visit the root
        if (node.type == ops.TYPE):
            the_type = str(node.attr)
            if the_type not in mapGroup.keys():
                print("Invalid type."); sys.exit(-1)
            return mapGroup.get(the_type)
        elif Type(node) == ops.RANDOM:
            retRandomType = str(node.getLeft().attr)
            return mapGroup.get(retRandomType)
        elif Type(node) == ops.HASH:
            retHashType = str(node.getRight().attr)
            return mapGroup.get(retHashType)
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
                assert len(_list[1:]) == 1, "var#x#y not supported on lhs assignment"
                self.listModel[ reflhsStr ] = new_solver.model()
                refHandle2 = K(IntSort(), refHandle)
                self.listVarType[ reflhsStr ] = refHandle2
                groupToInt.append( str(refHandle2) )
                mapGroup[ str(refHandle2) ] = refHandle2 # type definition
                return refHandle2

            return refHandle
        elif Type(node) == ops.NON_EQ_TST:
            return (leftNode != rightNode)
        elif Type(node) == ops.EQ_TST:
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
            return self.contextType(node, varType) # in case it has a '#' symbol
        elif Type(node) == ops.CONCAT:
            return listType
        elif Type(node) == ops.STRCONCAT:
            return Str            
        elif Type(node) == ops.FUNC:
            currentFuncName = getFullVarName(node, False)
            if (currentFuncName in sdl.builtInTypes):
                return sdl.builtInTypes[currentFuncName]
            elif (currentFuncName == INIT_FUNC_NAME):
                initType = node.listNodes[0]
                print("initType : ", initType)
                if (initType.isdigit() == True):
                    return sInt
                elif initType in mapGroup.keys():
                    return mapGroup.get(initType)
                else:
                    return Nil
            elif (currentFuncName == KEYS_FUNC_NAME):
                return listType
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
        name = attrName.split(LIST_INDEX_SYMBOL)[0]
        Model = None
        if name in self.listModel.keys():
            # check this first b/c the variable also occur in the varType dictionary
            refName = self.listVarType[ name ]
            Model = self.listModel[ name ]
        elif name in varType.keys():
            refName = varType[ name ]
        else:
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
            return Nil # for now
        else:
            return None
        
    def computeAttrType(self, varName, varType):
        if varName == "-1": return sInt
        if "-" in varName: varName.remove("-")
        
        if not varName.isdigit():
            if varName in varType.keys():
                return varType.get(varName)
            else:
                 print("Need type annotation: ", varName, " := NO_TYPE")
                 sys.exit(-1)
        else:
            return sInt
    
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
    
    def inferType(self, binNode, varType): 
        if Type(binNode) == ops.EQ:
            z3Nodes = self.__buildZ3Expression(binNode.getRight(), binNode.getLeft(), varType)
            print("Z3 expression: ", z3Nodes)
            lhsStr = str(binNode.getLeft())
            if lhsStr in self.listModel.keys():
#                new_type = self.convertType(self.listModel[lhsStr].evaluate(z3Nodes))
                if LIST_INDEX_SYMBOL in lhsStr: lhsStr = lhsStr.split(LIST_INDEX_SYMBOL)[0] # JAA: may need to do other things here
                new_type = self.listVarType[ lhsStr ]
            else:
                new_type = self.TypeModel.evaluate(z3Nodes)

            print("Inferred Type: ", new_type)
            varName = str(binNode.left)            
            #if varName == "pk": x = Int('x'); print("Test: ", str(new_type), self.TypeModel.evaluate(new_type[0]), self.TypeModel.evaluate(new_type[1]))
#            if LIST_INDEX_SYMBOL in varName:
#                pass
#                listKey = varName.split(LIST_INDEX_SYMBOL)[0]
#                if listKey in varType.keys():
#                    orig_type = varType.get(listKey)
#                    contextExpr = self.contextType(binNode.left, orig_type)
#                    contextRes  = self.TypeModel.evaluate(contextExpr)
#                    print("LHS: ", binNode.left, contextExpr, contextRes, new_type)
#                    if contextRes.eq( new_type ):
#                        print("Type OK!")
#                    else:
#                        print("ERROR: Invalid SDL statement!")
#                        sys.exit(-1)
#                else:
#                    print("Need type annotation for list type: ", listKey)
#            else:
                # check context of LHS assignment: 
            varType[varName] = new_type


# need to somehow handle list types => Str, Int, ZR, G1, G2, GT types

#eq1 = M.evaluate(exp(G1, mul(GT, GT)))
#print("Test 8: ", eq1)
#
#print("Test 9: ", M.evaluate(asym_pair(G1, G2)))
#
#print("Test 10: ", )

if __name__ == "__main__":
    tc = TypeCheck()
    tc.setupSolver()
    parser = sdl.SDLParser()
    varType = {} #{'tf0':listG1, 'tf1':listG1}
    args = sys.argv[1:]
    for i in args:
        binNode = parser.parse(i)
        tc.inferType(binNode, varType)
    
    print("VarTypes: ", varType)
