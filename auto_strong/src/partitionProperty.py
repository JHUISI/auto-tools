import src.sdlpath, sys, os, random, string, re, importlib
import sdlparser.SDLParser as sdl
from sdlparser.SDLang import *

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
    
    print("Program Slice for sigma1: ", sigma['sigma1'])
    for i in sigma['sigma1']:
        sliceListSigma1 = []
        getProgramSlice(config.signFuncName, assignInfo, i, sliceListSigma1)
        sliceListSigma1.sort()
        print("sliceList: ", sliceListSigma1)
    print("")    
    print("Program Slice for sigma2: ", sigma['sigma2'])
    for i in sigma['sigma2']:
        sliceListSigma2 = []
        getProgramSlice(config.signFuncName, assignInfo, i, sliceListSigma2)
        sliceListSigma2.sort()
        print("sliceList: ", sliceListSigma2)
    
    
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

def property2Check(targetFuncName, assignInfo, sigma):
    #TODO: use term rewriter to breakdown and extract the verification equation
    # 1) convert the pairing equation to the version expected by our Z3 solver
    # 2) determine whether the equation satisfies the following constraint:
    #    - \sigma_1 != \sigma_1pr && verify(pk, m, \sigma_1pr, \sigma_2) ==> True
    # Goal: verify that there is at most one \sigma_1 verifies with \sigma_2 under pk
    return True


class BSWTransform:
    def __init__(self):
        pass
    
    def construct(self):
        pass
    
