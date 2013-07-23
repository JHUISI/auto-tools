"""
Bellare-Shoup Transformation - if a signature is NOT partitionable, then we can apply the less efficient BS transform to 
convert the signature to a strongly-unforgeable signature.
"""
import src.sdlpath, importlib, sys
import sdlparser.SDLParser as sdl
from sdlparser.SDLang import *
from src.sdltechniques import *

keygenFuncName = "keygen"
signFuncName   = "sign"
verifyFuncName = "verify"

def applyBSTransform(sdl_file, config):
    """ read sdl file to determine interfaces and variable types, etc"""
    global assignInfo
    sdl.parseFile(sdl_file, False, ignoreCloudSourcing=True)
    assignInfo = sdl.getAssignInfo()
    allTypes   = sdl.getVarTypes()
    varTypes   = allTypes.get(sdl.TYPES_HEADER)
    # 1. extract each function
    inputSchemeApi = {keygenFuncName:None, signFuncName:None, verifyFuncName:None}
    funcVars = set()
    for i in config.functionOrder:
        print("processing func: ", i)
        inputSchemeApi[i], _funcVars = getInterface(assignInfo, i)
        funcVars = funcVars.union(_funcVars)
        
    funcVars = list(funcVars)
    print("funcVars: ", funcVars)    
    schemeTypes = getInterfaceTypes(allTypes, funcVars)
    
    name = sdl.assignInfo[sdl.NONE_FUNC_NAME][sdl.SDL_NAME].getAssignNode().getRight().getAttribute()
    setting = sdl.assignInfo[sdl.NONE_FUNC_NAME][sdl.ALGEBRAIC_SETTING].getAssignNode().getRight().getAttribute()

    schemeCalls = {}
    funcInput = {}
    funcOutput = {}
    for i in config.functionOrder:
        schemeCalls[i] = "%s.%s(%s)" % (name, i, getArgString(inputSchemeApi[i][inputKeyword]))
        print("funcCall: ", schemeCalls[i])
        funcInput[i] = inputSchemeApi[i][inputKeyword]
        funcOutput[i] = inputSchemeApi[i][outputKeyword]

    bsT = BSTransform(assignInfo, varTypes, schemeTypes, schemeCalls, funcInput, funcOutput)
    bsT.setSchemeName(name)
    bsT.setSetting(setting)
    bsT.constructSDL(config)
    return

def getInterface(assignInfo, funcName):
    funcVars = set()
    inputVarObj = assignInfo[funcName][inputKeyword]
    outputVarObj = assignInfo[funcName][outputKeyword]
    input = GetAttributeVars(inputVarObj.getAssignNode())
    input.remove(inputKeyword)
    output = GetAttributeVars(outputVarObj.getAssignNode())
    output.remove(outputKeyword)
    print("\t input: ", input)
    print("\t output: ", output)
    funcVars = funcVars.union(input)
    funcVars = funcVars.union(output)    
    return {inputKeyword:input, outputKeyword:output}, funcVars

def getInterfaceTypes(allTypes, funcVars):
    unifiedTypes = {}
    for i in allTypes.keys():
        unifiedTypes.update(allTypes[i])
        
    schemeTypes = {}
    for i in funcVars:
        if i not in ['None', 'False', 'True']:
            schemeTypes[i] = unifiedTypes.get(i).getType()
    
    return schemeTypes

def getArgString(args):
    argList = ""
    COMMA = ", "
    for i in args:
        argList += i + COMMA
    argList = argList[:-len(COMMA)]
    return argList
    
class BSTransform:
    def __init__(self, assignInfo, varTypes, schemeTypes, schemeCalls, funcInput, funcOutput):
        self.assignInfo  = assignInfo
        self.varTypes    = varTypes
        self.schemeCalls = schemeCalls
        self.funcInput   = funcInput
        self.funcOutput  = funcOutput
        self.__newTypeLines = []
        self.__schemeType = schemeTypes
        
    def __chooseVariables(self):
        self.ppk, self.psk = "ppk", "psk"
        self.ppkType = types.list
        self.pskType = types.list
        self.spk, self.ssk = "spk", "ssk"
        self.spkType = types.G1
        self.sskType = types.list
        self.newSig, self.origSig = "sig", "sig1"
        self.schnorr = "schnorr"
        self.schnorrSig = "sig2"
        self.newSK, self.newPK = "suSK", "suPK"
        self.newPKArgs = [self.ppk]
        self.newSKArgs = [self.psk]
    
    def setSchemeName(self, name):
        self.__schemeName = name
        return
    
    def setSetting(self, setting):
        self.__setting = setting
    
    def constructSDL(self, config):
        self.__chooseVariables()
        head = self.__constructHead()
        keygenLines = self.__constructKeygen(config)
        signLines   = self.__constructSign(config)
        verifyLines = self.__constructVerify(config)
        typeLines = self.__constructTypes()
        print_sdl(True, head, typeLines, keygenLines, signLines, verifyLines)
        outfile = self.strongName + ".sdl"
        write_sdl(outfile, [head, typeLines, keygenLines, signLines, verifyLines])
        print("output: ", outfile)
        return
    
    def __constructHead(self):
        assert self.__schemeName != None, "BSTransform: scheme name not set."
        assert self.__setting != None, "BSTransform: scheme setting not set."
        self.strongName = self.__schemeName + "SU"
        newLines0 = [ sdl.SDL_NAME + " := " + self.strongName, sdl.SETTING + " := " + self.__setting, "\n",
        "requires := list{" + self.schnorr + ", " + self.__schemeName + "}" ] 
        return newLines0
    
    def __constructTypes(self):
        typesHeadBegin = "BEGIN :: " + sdl.TYPES_HEADER
        typesHeadEnd = "END :: " + sdl.TYPES_HEADER
        newLines = [typesHeadBegin]
        typeLines = {}
        # extract line numbers
        for i, j in self.varTypes.items():
            typeLines[ j.getLineNo() ] = (i, j)
        
        # sort based on line number, then process each type
        typeKeysList = list(typeLines.keys())
        typeKeysList.sort() # sort the line numbers
        for k in typeKeysList:
            (i, j) = typeLines[k]
            newLines.append( j.getSrcLine() )
        
        newLines += self.__newTypeLines
        newLines.append( typesHeadEnd )
        return newLines
                
    def __constructKeygen(self, config):
        keyP = "keyP"
        keygenInArgs = self.funcInput[keygenFuncName]
        keygenOutArgs = [self.newSK, self.newPK]
        keyName = "varK"
        
        begin  = "BEGIN :: func:" + keygenFuncName
        input  = inputKeyword + " := list{" + getArgString(keygenInArgs) + "}"
        
        keyLine  = [ keyName + " := " + self.schemeCalls[keygenFuncName] ]
        keyTypes = []
        for j,i in enumerate(self.funcOutput[ keygenFuncName ]):
            keyLine.append( i + " := " + keyName + "#" + str(j) )
            keyTypes.append( i + " := " + str(self.__schemeType[i]) )
            if i == config.keygenSecVar: # find secret vars
                self.newSKArgs.append(i)
            else: # all else are public (works for symm and asymm schemes)
                self.newPKArgs.append(i)
        
        self.__newTypeLines += keyTypes
        self.__newTypeLines.append( keyName + " := list{" + getArgString(self.funcOutput[ keygenFuncName ]) + "}" )
        self.newSKArgs.reverse()
        self.newPKArgs.reverse()
        keyLine.append( keyP + " := " + self.schnorr + "." + keygenFuncName + "P(None)" )
        keyLine.append( self.ppk + " := " + keyP + "#0" )
        keyLine.append( self.psk + " := " + keyP + "#1" )
        self.__newTypeLines.append( self.ppk + " := " + str(self.ppkType) )
        self.__newTypeLines.append( self.psk + " := " + str(self.pskType) )
        self.__newTypeLines.append( keyP + " := list{" + self.ppk + ", " + self.psk + "}" )
        keyLine.append( self.newSK + " := list{" + getArgString(self.newSKArgs) + "}" )
        keyLine.append( self.newPK + " := list{" + getArgString(self.newPKArgs) + "}" )
        
        output = outputKeyword + " := list{" + getArgString(keygenOutArgs) + "}"
        end    = "END :: func:" + keygenFuncName
        
        newLines = [begin, input] + keyLine + [output, end]
        return newLines
    
    def __constructSign(self, config):
        keyS = "keyS"
        varM = "var" + config.messageVar.upper()
        varM1 = varM + "1"
        diffVars = set(list(self.newSKArgs + self.funcInput[signFuncName])).difference([config.messageVar] + self.newSKArgs)
        signInArgs = [self.newSK] + list(diffVars) + [config.messageVar]
        signOutArgs = [self.origSig, self.schnorrSig, self.spk]
        schnorrSignArgs = [self.psk, self.ssk, self.origSig]
        signLines = []
        
        begin  = "BEGIN :: func:" + signFuncName
        input  = inputKeyword + " := list{" + getArgString(signInArgs) + "}"
#          SK := expand{skR, psk}
        signLines.append( self.newSK + " := expand{" + getArgString(self.newSKArgs) + "}" )
        
        signLines.append( keyS + " := " + self.schnorr + "." + keygenFuncName + "S(" + getArgString([self.psk]) + ")" )
        signLines.append( self.spk + " := " + keyS + "#0" )
        signLines.append( self.ssk + " := " + keyS + "#1" )
        self.__newTypeLines.append( self.spk + " := " + str(self.spkType) )
        self.__newTypeLines.append( self.ssk + " := " + str(self.sskType) )
        self.__newTypeLines.append( keyS + " := list{" + self.spk + ", " + self.ssk + "}" )
        
        # prepare new regular signature input
        signLines.append( varM + " := concat{" + getArgString([self.spk, config.messageVar]) + "}" ) 
        MsgType = self.varTypes.get(config.messageVar).getType()
#        print("type: ", self.varTypes, config.messageVar)
        if MsgType == types.str:
            signLines.append( varM1 + " := DeriveKey(" + varM + ")" )
        elif MsgType in [types.ZR, types.G1]:
            signLines.append( varM1 + " := H(" + varM1 + ", " + str(MsgType) + ")" )
        else:
            print("BSTransform: Unexepcted type for " + config.messageVar)
            sys.exit(-1)
        self.__newTypeLines.append( varM1 + " := " + str(MsgType) )
        # call sign for the regular signature :=> sig1
        signLines.append( self.origSig + " := " + self.schemeCalls[signFuncName].replace(config.messageVar, varM1) )
        # call sign for the schnorr signature scheme :=> sig2
        signLines.append( self.schnorrSig + " := " + self.schnorr + "." + signFuncName + "(" + getArgString(schnorrSignArgs) + ")" )
        signLines.append( self.newSig + " := list{" + getArgString(signOutArgs) + "}" )
        output = outputKeyword + " := " + self.newSig 
        end    = "END :: func:" + signFuncName
        
        newLines = [begin, input] + signLines + [output, end]
        return newLines
    
    def __constructVerify(self, config):
        verifyLines = []
        verifyInArgs = [self.newPK, config.messageVar, self.newSig]
        newSigArgs = [self.origSig, self.schnorrSig, self.spk]
        schnorrVerifyArgs = [ self.ppk, self.spk, self.origSig, self.schnorrSig ] # ppk, spk, sig1, sig2

        # sanity check
        usedVars = self.funcInput[verifyFuncName] + schnorrVerifyArgs
        inArgs = newSigArgs + self.newPKArgs + [config.messageVar]
        neededSet = set(inArgs).difference(usedVars)
        if len(neededSet) > 0:
            print("BSTransform: needed for verify func: ", neededSet)
            sys.exit(-1)
        
        begin  = "BEGIN :: func:" + verifyFuncName
        input  = inputKeyword + " := list{" + getArgString(verifyInArgs) + "}"
        verifyLines.append( self.newSig + " := expand{" + getArgString(newSigArgs) + "}" )
        verifyLines.append( self.newPK + " := expand{" + getArgString(self.newPKArgs) + "}" )
        
        verifyCond1 = self.schemeCalls[verifyFuncName]
        verifyCond2 = self.schnorr + "." + verifyFuncName + "(" + getArgString(schnorrVerifyArgs) + ")"
        verifyLines.append( "BEGIN :: if" )
        verifyLines.append( "if {{" + verifyCond1 + " == True } and {" + verifyCond2 + " == True }}" )
        verifyLines.append( " output := True" )
        verifyLines.append( "else")        
        verifyLines.append( " output := False" )
        verifyLines.append( "END :: if" )
        end    = "END :: func:" + verifyFuncName            
        newLines = [begin, input] + verifyLines + [end]
        return newLines
    
def print_sdl(verbose, *blocks):
    if verbose:
        print("<===== new SDL =====>")
        for block in blocks:
            for i in block:
                print(i)
            print("\n")
        print("<===== new SDL =====>")
    return

def write_sdl(filename, blocks):
    f = open(filename, 'w')
    for block in blocks:
        for line in block:
            f.write(line + "\n")
        if len(block) > 0: f.write('\n') # in case block = [] (empty)
    f.close()
    return


if __name__ == "__main__":
    sdlFile = sys.argv[1]
    configName = sys.argv[2]
    configModule = importlib.import_module("schemes." + configName)
    
    applyBSTransform(sdlFile, configModule)
    