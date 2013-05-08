import sys, getopt, importlib, time
import src.sdlpath
import SDLParser as sdl
from SDLang import *
from src.convertToAsymmetric import *

import codegen_CPP

verboseFlag = "-v"
encConfigParams = ["keygenPubVar", "keygenSecVar", "ciphertextVar", "keygenFuncName", "encryptFuncName", "decryptFuncName"]
sigConfigParams = ["keygenPubVar", "keygenSecVar", "signatureVar", "keygenFuncName", "signFuncName", "verifyFuncName"]

def errorOut(keyword):
    sys.exit("configAutoGroup: missing '%s' variable in config." % keyword)

def configAutoGroup(sdl_file, cm, targetFile, sdlVerbose):
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
    
    if cm.schemeType == PKENC:
        for i in encConfigParams:
            if not hasattr(cm, i):
                errorOut(i)
    elif cm.schemeType == PKSIG:
        for i in sigConfigParams:
            if not hasattr(cm, i):
                errorOut(i)
    
    if not hasattr(cm, "secparam"):
        secparam = "BN256" # default pairing curve for now
    else:
        secparam = cm.secparam
        
    options = {'secparam':secparam, 'userFuncList':[], 'computeSize':False}
    startTime = time.clock()
    outfile = runAutoGroup(sdl_file, cm, options, sdlVerbose)
    endTime = time.clock()
    runningTime = (endTime - startTime) * 1000
    
    new_input_sdl  = outfile
    new_output_sdl = targetFile
    print("Codegen Input: ", new_input_sdl)
    print("Codegen Output: ", new_output_sdl)
    print("User defined funcs: ", options['userFuncList'])
    codegen_CPP.codegen_CPP_main(new_input_sdl, new_output_sdl, options['userFuncList'])
    return
    
if __name__ == "__main__":
    if len(sys.argv) > 3:
        print(sys.argv)
        sdl_file = sys.argv[1]
        if verboseFlag in sys.argv: sdlVerbose = True
        else: sdlVerbose = False
        config = sys.argv[2]
        targetFile = sys.argv[3]
        config = config.split('.')[0]

        configModule = importlib.import_module("schemes." + config)
        configAutoGroup(sdl_file, configModule, targetFile, sdlVerbose)
    else:
        print("python %s [ SDL file ] [ SDL config name ] [ Output code name ]" % sys.argv[0])
        sys.exit(-1)
