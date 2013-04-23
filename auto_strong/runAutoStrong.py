import sys, getopt, importlib
import src.sdlpath
import SDLParser as sdl
from SDLang import *
from src.partitionProperty import *

PKSIG = "PKSIG" # signature scheme type
functionOrder = "functionOrder"
verboseFlag = "-v"

configParams = ["messageVar", "signatureVar", "keygenPubVar", "keygenSecVar", "keygenFuncName", "signFuncName", "verifyFuncName"]

def errorOut(keyword):
    sys.exit("configAutoStrong: missing '%s' variable in config." % keyword)

def configAutoStrong(sdl_file, cm, option, sdlVerbose):
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
    
    print("function order: ", cm.functionOrder)
    testForSUCMA = False
    
    runAutoStrong(sdl_file, cm, option, sdlVerbose)
    return

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(sys.argv)
        sdl_file = sys.argv[1]
        if verboseFlag in sys.argv: sdlVerbose = True
        else: sdlVerbose = False
        config = sys.argv[2]
        config = config.split('.')[0]
        option = {skipTransform:False}
        try:
            value = sys.argv.index("-s")
            option[skipTransform] = True
        except:
            pass
        configModule = importlib.import_module("schemes." + config)
        configAutoStrong(sdl_file, configModule, option, sdlVerbose)
    else:
        print("python %s [ SDL file ] [ SDL config name ]" % sys.argv[0])
        sys.exit(-1)