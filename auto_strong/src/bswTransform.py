import src.sdlpath, importlib
import sdlparser.SDLParser as sdl
from sdlparser.SDLang import *
from src.sdltechniques import *


ch = "ch"

class BSWTransform:
    def __init__(self, assignInfo, theVarTypes, messageVar, messageVarList):
        self.assignInfo     = assignInfo
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
        return
        
    def __chooseVariables(self, config):
        suffix = "New"
        self.chamH = "chamH"
        self.chK, self.chT, self.ch0, self.ch1, self.chpk = ch+"K", ch+"t", ch+"0", ch+"1", ch+"pk"
        self.t0, self.t1 = "t0", "t1"
        self.chZr, self.chVal = ch+"Zr", ch+"Val"
        self.chPrefix = "1"
        seedVar = "s"
        self.seed = seedVar + "0"
        self.hashVal = seedVar + "1"
        self.newMsgVal = self.messageVar + "pr"
        
        # search for each one
        sdlVars = [self.chK, self.chT, self.ch0, self.ch1, self.chpk, self.t0, self.t1, self.chZr, self.chVal, self.seed, self.hashVal, self.newMsgVal]
        
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
        (name, varInf) = getVarNameEntryFromAssignInfo(self.assignInfo, config.keygenPubVar)        
        funcVisited.append(name)
        print("Found public key in: ", name)
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
                    newLines.append( self.chT + " := random(ZR)" )                    
                    newLines.append( self.ch0 + " := random(G1)" )
                    newLines.append( self.ch1 + " := %s ^ %s" % (self.ch0, self.chT))
                    newLines.append( self.chpk + " := list{" + self.ch0 + ", " + self.ch1 + "}" )
                elif str(Stmts[i].getAssignVar()) == config.keygenSecVar:
                    Stmts[i].getAssignNode().getRight().listNodes.insert(0, self.chT)                                    
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
                elif str(Stmts[i].getAssignVar()) == config.keygenSecVar:                    
                    Stmts[i].getAssignNode().getRight().listNodes.insert(0, self.chT) 

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

def print_sdl(verbose, *args):
    if verbose:
        print("<===== new SDL =====>")    
        for block in args:
            for i in block:
                print(i)
            print("\n\n")
        print("<===== new SDL =====>")
    return
