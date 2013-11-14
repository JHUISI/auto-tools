import os, sys, getopt, imp, time
import src.sdlpath
import SDLParser as sdl
from SDLang import *
from src.convertToAsymmetric import *

import codegen_CPP
import codegen_PY

description = "sym.-to-asym. conversion for cryptographic schemes in SDL."
help_info   = """
\t-s, --sdl  [ filename ]
\t\t: input SDL file description of scheme.

\t-c, --config [ SDL config file ]
\t\t: configuration parameters needed for AutoGroup.

\t-v, --verbose   [ no-argument ]
\t\t: enable verbose mode.

\t-o, --outfile  [ filename prefix ]
\t\t: generate code of new scheme in C++/Python for Charm.

\t-b, --benchmark  [ no-arguments ]
\t\t: benchmark AutoGroup execution time.

\t-e, --estimate [ no-arguments ]
\t\t: estimate bandwidth for keys and ciphertext/signatures.

\t--path [ path/to/dir/ ]
\t\t: destination for AutoGroup output files. Default: current dir.
"""

verbose = print_usage = print_options = benchmark = estimateSize = False
sdl_file = None
output_file = None
config_file = None
dest_path = ""
library = 'miracl'

try:
    options, remainder = getopt.getopt(sys.argv[1:], 'o:s:c:behv', ['outfile=', 'sdl=', 'config=', 'benchmark', 'estimate', 'help', 'verbose', 'path=', 'print'])
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
    elif opt in ('-l', '--library'):
        library = arg
    elif opt in ('-b', '--benchmark'):
        benchmark = True
    elif opt in ('-e', '--estimate'):
        estimateSize = True
    elif opt == '--path':
        dest_path = arg        
    elif opt == '--print':
        print_options = True

if verbose:
    print('OPTIONS   :', options)
if print_usage:
    print("AutoGroup: ", description)
    print("\nArguments:")
    print(help_info)
    sys.exit(0)
if print_options:
    print('VERBOSE    :', verbose)
    print('CONFIG     :', config_file)
    print('SDL INPUT  :', sdl_file)
    print('SDL OUTPUT :', output_file)
    print('PATH:      :', dest_path)
    print('BENCHMARK  :', benchmark)
    print('ESTIMATES  :', estimateSize)

sys.exit("Need to specify SDL file.\nArguments: " + help_info) if sdl_file == None else None
sys.exit("Need to specify config file.\nArguments: " + help_info) if config_file == None else None
sys.exit("Need an output file for codegen.\nArguments: " + help_info) if output_file == None else None
if dest_path != "" and dest_path[-1] != '/': dest_path += '/'

verboseFlag = "-v"
encConfigParams = ["keygenPubVar", "keygenSecVar", "ciphertextVar", "keygenFuncName", "encryptFuncName", "decryptFuncName"]
sigConfigParams = ["keygenPubVar", "keygenSecVar", "signatureVar", "keygenFuncName", "signFuncName", "verifyFuncName"]

def errorOut(keyword):
    sys.exit("configAutoGroup: missing '%s' variable in config." % keyword)

def configAutoGroup(dest_path, sdl_file, config_file, output_file, verbose, benchmarkOpt, estimateOpt):
    # get full path (assuming not provided)
    full_config_file = os.path.abspath(config_file)
    pkg_name = os.path.basename(full_config_file)
    
    cm = imp.load_source(pkg_name, full_config_file)
    
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
    
    dropFirst = None
    if hasattr(cm, "dropFirst"):
        dropFirst = cm.dropFirst
    
    options = {'secparam':secparam, 'userFuncList':[], 'computeSize':estimateOpt, 'dropFirst':dropFirst, 'path':dest_path}
    startTime = time.clock()
    outfile = runAutoGroup(sdl_file, cm, options, verbose)
    endTime = time.clock()
    if benchmarkOpt: 
        runningTime = (endTime - startTime) * 1000
        print("running time: ", str(runningTime) + "ms")
        os.system("echo '%s' >> %s" % (runningTime, output_file))
    
    new_input_sdl  = outfile
    new_output_sdl = output_file
    # JAA: commented out for benchmark purposes
    if verbose:
        print("Codegen Input: ", new_input_sdl)
        print("Codegen Output: ", new_output_sdl)
        print("User defined funcs: ", options['userFuncList'])
    if not benchmarkOpt:
        codegen_CPP.codegen_CPP_main(new_input_sdl, dest_path + new_output_sdl + ".cpp", options['userFuncList'])
        codegen_PY.codegen_PY_main(new_input_sdl, dest_path + new_output_sdl + ".py", new_output_sdl + "User.py")
    return

# run AutoGroup with the designated options
configAutoGroup(dest_path, sdl_file, config_file, output_file, verbose, benchmark, estimateSize)
