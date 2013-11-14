import os, sys, getopt, imp, time
import src.sdlpath
import SDLParser as sdl
from SDLang import *
from src.partitionProperty import *

import codegen_CPP
import codegen_PY

description = "convert an unforgeable signature to a strongly unforgeable signature in SDL."
help_info   = """
\t-s, --sdl  [ filename ]
\t\t: input SDL file description of scheme.

\t-c, --config [ SDL config file ]
\t\t: configuration parameters needed for AutoStrong.

\t-v, --verbose   [ no-argument ]
\t\t: enable verbose mode.

\t-o, --outfile  [ filename prefix ]
\t\t: generate code of new scheme in C++/Python for Charm.

\t-b, --benchmark  [ no-arguments ]
\t\t: benchmark AutoStrong execution time.

\t-t, --skip-transform [ no-arguments ]
\t\t: skip the application of the BSW or BS transform

\t--path [ path/to/dir/ ]
\t\t: destination for AutoStrong output files. Default: current dir.
"""

verbose = print_usage = print_options = benchmark = skip_transform = False
sdl_file = None
output_file = None
config_file = None
dest_path = ""

try:
    options, remainder = getopt.getopt(sys.argv[1:], 'o:s:c:bhvt', ['outfile=', 'sdl=', 'config=', 'benchmark', 'help', 'verbose', 'path=', 'skip-transform', 'print'])
except:
    sys.exit("ERROR: Specified invalid arguments.")

for opt, arg in options:
    if opt in ('-h', '--help'):
        print_usage = True
    elif opt in ('-o', '--outfile'):
        output_file = arg
    elif opt in ('-s', '--sdl'):
        sdl_file = arg
    elif opt in ('-v', '--verbose'):
        verbose = True
    elif opt in ('-c', '--config'):
        config_file = arg
    elif opt in ('-b', '--benchmark'):
        benchmark = True
    elif opt in ('-t', '--skip-transform'):
        skip_transform = True
    elif opt == '--path':
        dest_path = arg        
    elif opt == '--print':
        print_options = True

if verbose:
    print('OPTIONS   :', options)
if print_usage:
    print("AutoStrong: ", description)
    print("\nArguments:")
    print(help_info)
    sys.exit(0)
if print_options:
    print('VERBOSE    :', verbose)
    print('CONFIG     :', config_file)
    print('SDL INPUT  :', sdl_file)
    print('SDL OUTPUT :', output_file)
    print('PATH       :', dest_path)
    print('BENCHMARK  :', benchmark)

sys.exit("Need to specify SDL file.\nArguments: " + help_info) if sdl_file == None else None
sys.exit("Need to specify config file.\nArguments: " + help_info) if config_file == None else None
sys.exit("Need an output file for codegen.\nArguments: " + help_info) if output_file == None else None
if dest_path != "" and dest_path[-1] != '/': dest_path += '/'

PKSIG = "PKSIG" # signature scheme type
functionOrder = "functionOrder"
verboseFlag = "-v"

configParams = ["messageVar", "signatureVar", "keygenPubVar", "keygenSecVar", "keygenFuncName", "signFuncName", "verifyFuncName"]

def errorOut(keyword):
    sys.exit("configAutoStrong: missing '%s' variable in config." % keyword)

def configAutoStrong(dest_path, sdl_file, config_file, output_file, verbose, benchmarkOpt, skip_transform):
    # get full path (assuming not provided)
    full_config_file = os.path.abspath(config_file)
    pkg_name = os.path.basename(full_config_file)
    
    cm = imp.load_source(pkg_name, full_config_file)
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
    
    option = {}
    option[skipTransform] = skip_transform
    option['userFuncList'] = userFuncList
    startTime = time.clock()
    strong_sdl = runAutoStrong(sdl_file, cm, option, verbose)
    endTime = time.clock()
    new_input_sdl = strong_sdl
    new_output_sdl = dest_path + output_file
    if benchmarkOpt:
        runningTime = (endTime - startTime) * 1000
        print("running time: ", str(runningTime) + "ms")
        os.system("echo '%s' >> %s" % (runningTime, output_file))
    
    print("Codegen Input: ", new_input_sdl)
    print("Codegen Output: ", new_output_sdl)
    print("User defined funcs: ", option['userFuncList'])
    if not benchmarkOpt:
        codegen_CPP.codegen_CPP_main(new_input_sdl, new_output_sdl + ".cpp", option['userFuncList'])
        codegen_PY.codegen_PY_main(new_input_sdl, new_output_sdl + ".py", new_output_sdl + "User.py")
    return

# run AutoStrong with the designated options
configAutoStrong(dest_path, sdl_file, config_file, output_file, verbose, benchmark, skip_transform)
