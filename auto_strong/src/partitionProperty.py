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

def property2Check():
    pass


class BSWTransform:
    def __init__(self):
        pass
    
    def construct(self):
        pass
    
