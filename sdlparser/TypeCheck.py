from z3 import *
from SDLang import *
import SDLParser as sdl

#Group, (sInt, ZR, G1, G2, GT, Nil) = EnumSort('GroupType', ('sInt', 'ZR', 'G1', 'G2', 'GT', 'Nil'))
Group, (Str, sInt, ZR, G1, G2, GT, listType, listStr, listInt, listZR, listG1, listG2, listGT, metalist, metalistStr, metalistInt, metalistZR, metalistG1, metalistG2, metalistGT, Nil) = \
    EnumSort('GroupType', ('Str','sInt', 'ZR', 'G1', 'G2', 'GT', 'list', 'listStr', 'listInt', 'listZR', 'listG1', 'listG2', 'listGT', \
                           'metalist', 'metalistStr', 'metalistInt', 'metalistZR', 'metalistG1', 'metalistG2', 'metalistGT','Nil'))

mapGroup = {'Str':Str, 'sInt':sInt, 'ZR':ZR, 'G1':G1, 'G2':G2, 'GT':GT, 'list':listType, 'listStr':listStr, 'listInt':listInt, 'listZR':listZR, 'listG1':listG1, 'listG2':listG2, 'listGT':listGT, 
            'metalist':metalist, 'metalistStr':metalistStr, 'metalistInt':metalistInt, 'metalistZR':metalistZR, 'metalistG1':metalistG1, 'metalistG2':metalistG2, 'metalistGT':metalistGT, 'Nil':Nil}

exp = Function('exp', Group, Group, Group)
mul = Function('mul', Group, Group, Group)
div = Function('div', Group, Group, Group)
add = Function('add', Group, Group, Group)
sub = Function('sub', Group, Group, Group)
sym_pair = Function('sympair', Group, Group, Group)
asym_pair = Function('asympair', Group, Group, Group)

# will be created uniquely for each list type variable
# listArray = Array("varName", IntSort(), Group)

refDown = Function('refDown', Group, Group)

def buildList(var, listTypes):
    cond = []
    for i in listTypes:
        assert i in mapGroup.keys(), "specified invalid SDL type"
        cond.append( var == mapGroup[i] )
    return cond
    
#isZR = Function('isZR', Group, Group)
#isGroup = Function('isGroup', Group, Group)
class TypeCheck:
    def __init__(self, setting=None, verbose=False):
        self.setting = setting
        self.verbose = verbose
    
    def __getTypeModel(self):        
        x, y = Consts('x y', Group)
        # rules for exponentiation 
        exp_axioms = [ ForAll([x, y], Implies(And(Or(buildList(x, ['sInt', 'ZR', 'G1', 'G2', 'GT'])), Or(buildList(y, ['sInt', 'ZR']))), exp(x, y) == x)), # y == G1, y == G2, y == GT, y == listZR, y == listG1, y == listG2, y == listGT, y == Nil
                       ForAll([x, y], Implies(Or(buildList(y, ['Str', 'G1', 'G2', 'GT', 'list', 'listZR', 'listG1', 'listG2', 'listGT', \
                                                               'metalist', 'metalistZR', 'metalistG1', 'metalistG2', 'metalistGT','Nil'])), exp(x, y) == Nil)) ]
        
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
        
        axioms = [ ForAll(x, Implies(x == listG1, refDown(x) == G1)),
                   ForAll(x, Implies(x == listG2, refDown(x) == G2)),
                   ForAll(x, Implies(x == listGT, refDown(x) == GT)),
                   ForAll(x, Implies(x == listZR, refDown(x) == ZR)),
                   ForAll(x, Implies(x == listInt, refDown(x) == sInt)),           
                   ForAll(x, Implies(x == listStr, refDown(x) == Str)),
                   ForAll(x, Implies(x == metalist, refDown(x) == listType)),                   
                   ForAll(x, Implies(x == metalistStr, refDown(x) == listStr)),            
                   ForAll(x, Implies(x == metalistZR, refDown(x) == listZR)), 
                   ForAll(x, Implies(x == metalistG1, refDown(x) == listG1)), 
                   ForAll(x, Implies(x == metalistG2, refDown(x) == listG2)), 
                   ForAll(x, Implies(x == metalistGT, refDown(x) == listGT)),            
                   ForAll(x, Implies(Or(buildList(x, ['sInt', 'ZR', 'G1', 'G2', 'GT', 'list', 'Nil'])), refDown(x) == Nil)) ]
            
        s = Solver()
        s.add( exp_axioms )
        s.add( mul_axioms )
        s.add( div_axioms )
        s.add( add_axioms )
        s.add( sub_axioms )
        if self.setting == SYMMETRIC_SETTING:
            s.add( sym_axioms )        
        elif self.setting == ASYMMETRIC_SETTING:
            s.add( asym_axioms )
        s.add( axioms )
        #print(s)
        satisfy = s.check()
        print("satisfiable: ", satisfy)
        if satisfy == unsat:
            sys.exit(-1)
    
        return s
    
    def setupSolver(self):
        solver = self.__getTypeModel()
        if self.verbose: print(solver)
        M = solver.model()
        self.TypeModel = M
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
        print("Test 9: ", M.evaluate(mul(G1, refDown(listG1))))
        print("Test 10: ", M.evaluate(mul(Str, refDown(refDown(metalistStr)))))
    
    def __buildZ3Expression(self, node, varType):
        if node == None: return None
        if node.left != None: leftNode   = self.__buildZ3Expression(node.left, varType)
        if node.right != None: rightNode = self.__buildZ3Expression(node.right, varType)
        
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
        elif Type(node) == ops.LIST:
            return listType
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
            return self.contextType(node, theType) # in case it has a '#' symbol
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
            return Nil # Error
        
        else:
            print("NodeType unsupported: ", Type(node))
            return None
    
    def contextType(self, attrNode, theType):
        print("attrNode: ", attrNode)
        countHash = len(str(attrNode).split(LIST_INDEX_SYMBOL))-1
        context = theType # usually one of the above types
        for i in range(countHash):
            context = refDown(context)
        return context
    
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
    
    def inferType(self, binNode, varType): 
        #solver = self.__getTypeModel()
        #print(solver)
        #M = solver.model()
        #print(M)
        if Type(binNode) == ops.EQ:
            z3Nodes = self.__buildZ3Expression(binNode.getRight(), varType)
            print("Z3 expression: ", z3Nodes)
            new_type = self.TypeModel.evaluate(z3Nodes)
            print("Inferred Type: ", new_type)
            varName = str(binNode.left)
            if LIST_INDEX_SYMBOL in varName:
                listKey = varName.split(LIST_INDEX_SYMBOL)[0]
                if listKey in varType.keys():
                    orig_type = varType.get(listKey)
                    contextExpr = self.contextType(binNode.left, orig_type)
                    contextRes  = self.TypeModel.evaluate(contextExpr)
                    print("LHS: ", binNode.left, contextExpr, contextRes, new_type)
                    if contextRes.eq( new_type ):
                        print("Type OK!")
                    else:
                        print("ERROR: Invalid SDL statement!")
                        sys.exit(-1)
                else:
                    print("Need type annotation for list type: ", listKey)
            else:
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
