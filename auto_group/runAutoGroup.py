import sys, getopt, importlib
import src.sdlpath
import SDLParser as sdl
from SDLang import *
from src.convertToAsymmetric import *

verboseFlag = "-v"
encConfigParams = ["keygenPubVar", "keygenSecVar", "ciphertextVar", "keygenFuncName", "encryptFuncName", "decryptFuncName"]

def errorOut(keyword):
    sys.exit("configAutoGroup: missing '%s' variable in config." % keyword)

def configAutoGroup(sdl_file, cm, sdlVerbose):
    # setup sdl parser configs
    sdl.masterPubVars = cm.masterPubVars
    sdl.masterSecVars = cm.masterSecVars
    if not hasattr(cm, "schemeType"):
        sys.exit("configAutoGroup: need to set 'schemeType' in config.")
    
    if cm.schemeType == PKENC and getattr(cm, functionOrder, None) == None:
        funcOrder = [cm.setupFuncName, cm.keygenFuncName, cm.encryptFuncName, cm.decryptFuncName]
        setattr(cm, functionOrder, funcOrder)
    elif cm.schemeType == PKSIG and getattr(cm, functionOrder, None) == None:
        funcOrder = [cm.setupFuncName, cm.keygenFuncName, cm.signFuncName, cm.verifyFuncName]
        setattr(cm, functionOrder, funcOrder)

    print("function order: ", cm.functionOrder)
        
    for i in encConfigParams:
        if not hasattr(cm, i):
            errorOut(i)
    
    if not hasattr(cm, "secparam"):
        secparam = "MNT160" # default pairing curve for now
    else:
        secparam = cm.secparam
    runAutoGroup(sdl_file, cm, secparam, sdlVerbose)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(sys.argv)
        sdl_file = sys.argv[1]
        if verboseFlag in sys.argv: sdlVerbose = True
        else: sdlVerbose = False
        config = sys.argv[2]
        config = config.split('.')[0]

        configModule = importlib.import_module("schemes." + config)
        configAutoGroup(sdl_file, configModule, sdlVerbose)
    else:
        print("python %s [ SDL file ] [ SDL config name ]" % sys.argv[0])
        sys.exit(-1)        
