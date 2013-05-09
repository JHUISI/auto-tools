import sys, getopt, importlib, time
import src.sdlpath
import SDLParser as sdl
from SDLang import *
from src.partitionProperty import *

import codegen_CPP

PKSIG = "PKSIG" # signature scheme type
functionOrder = "functionOrder"
verboseFlag = "-v"

configParams = ["messageVar", "signatureVar", "keygenPubVar", "keygenSecVar", "keygenFuncName", "signFuncName", "verifyFuncName"]

def errorOut(keyword):
    sys.exit("configAutoStrong: missing '%s' variable in config." % keyword)

def configAutoStrong(sdl_file, cm, option, targetFile, sdlVerbose):
    # setup sdl parser configs
    sdl.masterPubVars = cm.masterPubVars
    sdl.masterSecVars = cm.masterSecVars
    if not hasattr(cm, "schemeType"):
        sys.exit("configAutoStrong: need to set 'schemeType' in config.")
    
    if cm.schemeType == PKSIG and getattr(cm, functionOrder, None) == None:
        funcOrder = [cm.setupFuncName, cm.keygenFuncName, cm.signFuncName, cm.verifyFuncName]
        setattr(cm, functionOrder, funcOrder)
    
    for i in configParams:
        if not hasattr(cm, i):
            errorOut(i)
    
    if hasattr(cm, "userFuncList"):
        userFuncList = cm.userFuncList
    else:
        userFuncList = []
    
    print("function order: ", cm.functionOrder)
    testForSUCMA = False
    
    option['userFuncList'] = userFuncList
    startTime = time.clock()
    strong_sdl = runAutoStrong(sdl_file, cm, option, sdlVerbose)
    endTime = time.clock()
    new_input_sdl = strong_sdl
    new_output_sdl = targetFile
    runningTime = (endTime - startTime) * 1000
    print("running time: ", runningTime)
    os.system("echo '%s' >> %s" % (runningTime, targetFile))
    
    #print("Codegen Input: ", new_input_sdl)
    #print("Codegen Output: ", new_output_sdl)
    #print("User defined funcs: ", option['userFuncList'])
    #codegen_CPP.codegen_CPP_main(new_input_sdl, new_output_sdl, option['userFuncList'])
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
        option = {skipTransform:False}
        
        try:
            value = sys.argv.index("-s")
            option[skipTransform] = True
        except:
            pass
        configModule = importlib.import_module("schemes." + config)
        configAutoStrong(sdl_file, configModule, option, targetFile, sdlVerbose)
    else:
        print("python %s [ SDL file ] [ SDL config name ] [ Output code name ]" % sys.argv[0])
        sys.exit(-1)
