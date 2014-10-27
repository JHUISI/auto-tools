import os, sys, getopt, imp, time
import src.sdlpath
import SDLParser as sdl
from SDLang import *
from src.convertToAsymmetric import *
from src.outsrctechniques import SubstituteVar, SubstitutePairings, SplitPairings, HasPairings, CountOfPairings, MaintainOrder, PairInstanceFinderImproved, TestForMultipleEq, GetAttributeVars, GetEquqlityNodes, CountExpOp, CountMulOp, DelAnyVarInList

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

def parseAssumptionFile(cm, assumption_file, verbose, benchmarkOpt, estimateOpt):
    # setup sdl parser configs
    sdl.masterPubVars = cm.assumpMasterPubVars
    sdl.masterSecVars = cm.assumpMasterSecVars
    if not hasattr(cm, "schemeType"):
        sys.exit("configAutoGroup: need to set 'schemeType' in config.")

    funcOrder = [cm.assumpSetupFuncName, cm.assumpFuncName]
    setattr(cm, functionOrder, funcOrder)

    print("function order: ", cm.functionOrder)

    #TODO: create something like this for assumption?
    #for i in encConfigParams:
    #    if not hasattr(cm, i):
    #        errorOut(i)
    
    if not hasattr(cm, "secparam"):
        secparam = "BN256" # default pairing curve for now
    else:
        secparam = cm.secparam
    
    #do we need this for the assumption?
    dropFirst = None
    if hasattr(cm, "dropFirst"):
        dropFirst = cm.dropFirst
    
    options = {'secparam':secparam, 'userFuncList':[], 'computeSize':estimateOpt, 'dropFirst':dropFirst, 'path':dest_path}

    sdl.parseFile(assumption_file, verbose, ignoreCloudSourcing=True)
    assignInfo_assump = sdl.getAssignInfo()
    assumptionData = {'sdl_name':sdl.assignInfo[sdl.NONE_FUNC_NAME][BV_NAME].getAssignNode().getRight().getAttribute(), 'setting':sdl.assignInfo[sdl.NONE_FUNC_NAME][ALGEBRAIC_SETTING].getAssignNode().getRight().getAttribute(), 'assignInfo':assignInfo_assump, 'typesBlock':sdl.getFuncStmts( TYPES_HEADER ), 'userCodeBlocks':list(set(list(assignInfo_assump.keys())).difference(cm.functionOrder + [TYPES_HEADER, NONE_FUNC_NAME]))}


    # this consists of the type of the input scheme (e.g., symmetric)
    setting = sdl.assignInfo[sdl.NONE_FUNC_NAME][ALGEBRAIC_SETTING].getAssignNode().getRight().getAttribute()
    # name of the scheme
    sdl_name = sdl.assignInfo[sdl.NONE_FUNC_NAME][BV_NAME].getAssignNode().getRight().getAttribute()

    typesBlock = sdl.getFuncStmts( TYPES_HEADER )
    info = {'verbose':verbose}

    # we want to ignore user defined functions from our analysis
    # (unless certain variables that we care about are manipulated there)
    userCodeBlocks = list(set(list(assignInfo_assump.keys())).difference(cm.functionOrder + [TYPES_HEADER, NONE_FUNC_NAME]))
    options['userFuncList'] += userCodeBlocks

    lines = list(typesBlock[0].keys())
    lines.sort()
    typesBlockLines = [ i.rstrip() for i in sdl.getLinesOfCodeFromLineNos(lines) ]
    begin = ["BEGIN :: " + TYPES_HEADER]
    end = ["END :: " + TYPES_HEADER]

    # start constructing the preamble for the Asymmetric SDL output
    newLines0 = [ BV_NAME + " := " + sdl_name, SETTING + " := " + sdl.ASYMMETRIC_SETTING ] 
    newLines1 = begin + typesBlockLines + end
    # this fact is already verified by the parser
    # but if scheme claims symmetric
    # and really an asymmetric scheme then parser will
    # complain.
    assert setting == sdl.SYMMETRIC_SETTING, "No need to convert to asymmetric setting."    
    # determine user preference in terms of keygen or encrypt
    short = SHORT_DEFAULT # default option
    if hasattr(cm, 'short'):
        if cm.short in SHORT_OPTIONS:
            short = cm.short
    print("reducing size of '%s'" % short) 

    varTypes = dict(sdl.getVarTypes().get(TYPES_HEADER))
    typesH = dict(varTypes)
    if not hasattr(cm, 'schemeType'):
        sys.exit("'schemeType' option missing in specified config file.")
    pairingSearch = []
    # extract the statements, types, dependency list, influence list and exponents of influence list
    # for each algorithm in the SDL scheme
    (stmtS, typesS, depListS, depListNoExpS, infListS, infListNoExpS) = sdl.getVarInfoFuncStmts( cm.assumpSetupFuncName )
    (stmtA, typesA, depListA, depListNoExpA, infListA, infListNoExpA) = sdl.getVarInfoFuncStmts( cm.assumpFuncName )
    varTypes.update(typesS)
    varTypes.update(typesA)
    print(depListS, depListNoExpS)
    print(depListA, depListNoExpA)
    # TODO: expand search to encrypt and potentially setup
    pairingSearch += [stmtS, stmtA] # aka start with decrypt.
            
    info[curveID] = options['secparam']
    info[dropFirstKeyword] = options[dropFirstKeyword]
    gen = Generators(info)
    # JAA: commented out for benchmarking    
    #print("List of generators for scheme")
    # retrieve the generators selected by the scheme
    # typically found in the setup routine in most cases.
    # extract the generators from the setup and keygen routine for later use
    if hasattr(cm, 'assumpSetupFuncName'):
        gen.extractGens(stmtS, typesS)
    if hasattr(cm, 'assumpFuncName'):
        gen.extractGens(stmtA, typesA)
    else:
        sys.exit("Assumption failed: setup not defined for this function. Where to extract generators?")
    generators = gen.getGens()
    # JAA: commented out for benchmarking    
    print("Generators extracted: ", generators)

    print("\n")

    # need a Visitor class to build these variables  
    # TODO: expand to other parts of algorithm including setup, keygen, encrypt
    # Visits each pairing computation in the SDL and
    # extracts the inputs. This is the beginning of the
    # analysis of these variables as the SDL is converted into
    # an asymmetric scheme.
    hashVarList = []
    pair_vars_G1_lhs = [] 
    pair_vars_G1_rhs = []    
    gpv = GetPairingVariables(pair_vars_G1_lhs, pair_vars_G1_rhs)
    print(pairingSearch)
    for eachStmt in pairingSearch: # loop through each pairing statement
        print(pair_vars_G1_lhs)            
        lines = eachStmt.keys() # for each line, do the following
        for i in lines:
            print(pair_vars_G1_lhs)            
            if type(eachStmt[i]) == sdl.VarInfo: # make sure we have the Var Object
                #print("Each: ", eachStmt[i].getAssignNode())
                # assert that the statement contains a pairing computation
                if HasPairings(eachStmt[i].getAssignNode()):
                    path_applied = []
                    # split pairings if necessary so that we don't influence
                    # the solve in anyway. We can later recombine these during
                    # post processing of the SDL
                    eachStmt[i].assignNode = SplitPairings(eachStmt[i].getAssignNode(), path_applied)
                    # JAA: commented out for benchmarking                    
                    #if len(path_applied) > 0: print("Split Pairings: ", eachStmt[i].getAssignNode())
                    if info['verbose']: print("Each: ", eachStmt[i].getAssignNode())
                    print(eachStmt[i].assignNode)
                    sdl.ASTVisitor( gpv ).preorder( eachStmt[i].getAssignNode() )
                elif eachStmt[i].getHashArgsInAssignNode(): 
                    # in case there's a hashed value...build up list and check later to see if it appears
                    # in pairing variable list
                    print("hash => ", str(eachStmt[i].getAssignVar()))
                    hashVarList.append(str(eachStmt[i].getAssignVar()))
                else:
                    continue # not interested
                
    # constraint list narrows the solutions that
    # we care about
    constraintList = []
    # for example, include any hashed values that show up in a pairing by default
    for i in hashVarList:
        if i in pair_vars_G1_lhs or i in pair_vars_G1_rhs:
            constraintList.append(i)
    # JAA: commented out for benchmarking            
    print("pair vars LHS:", pair_vars_G1_lhs)
    print("pair vars RHS:", pair_vars_G1_rhs) 
    print("list of gens :", generators)
    print("constraintList: ", constraintList)
    # for each pairing variable, we construct a dependency graph all the way back to
    # the generators used. The input of assignTraceback consists of the list of SDL statements,
    # generators from setup, type info, and the pairing variables.
    # We do this analysis for both sides
    info[ 'G1_lhs' ] = (pair_vars_G1_lhs, assignTraceback(assignInfo_assump, generators, varTypes, pair_vars_G1_lhs, constraintList))
    info[ 'G1_rhs' ] = (pair_vars_G1_rhs, assignTraceback(assignInfo_assump, generators, varTypes, pair_vars_G1_rhs, constraintList))

    depList = {}
    for i in [depListS, depListA]:
        for (key, val) in i.items():
            print(key, val)
            if(not(len(val) == 0) and not(key == 'input') and not(key == 'output')):
                depList[key] = val
    print(depList)

    print("\n")
    info[ 'deps' ] = (depList, assignTraceback(assignInfo_assump, generators, varTypes, depList, constraintList))
    print(info['deps'])

    print("\n")

    assumptionData['info'] = info
    assumptionData['depList'] = depList
    assumptionData['deps'] = info['deps']

    return assumptionData

def parseReductionFile(cm, reduction_file, verbose, benchmarkOpt, estimateOpt):
    # setup sdl parser configs
    sdl.masterPubVars = cm.reducMasterPubVars
    sdl.masterSecVars = cm.reducMasterSecVars
    if not hasattr(cm, "schemeType"):
        sys.exit("configAutoGroup: need to set 'schemeType' in config.")

    funcOrder = [cm.reducSetupFuncName, cm.reducQueryFuncName, cm.reducChallengeFuncName]
    setattr(cm, functionOrder, funcOrder)

    print("function order: ", cm.functionOrder)

    #TODO: create something like this for assumption?
    #for i in encConfigParams:
    #    if not hasattr(cm, i):
    #        errorOut(i)
    
    if not hasattr(cm, "secparam"):
        secparam = "BN256" # default pairing curve for now
    else:
        secparam = cm.secparam
    
    #do we need this for the assumption?
    dropFirst = None
    if hasattr(cm, "dropFirst"):
        dropFirst = cm.dropFirst
    
    options = {'secparam':secparam, 'userFuncList':[], 'computeSize':estimateOpt, 'dropFirst':dropFirst, 'path':dest_path}

    sdl.parseFile(reduction_file, verbose, ignoreCloudSourcing=True)
    assignInfo_reduction = sdl.getAssignInfo()
    reductionData = {'sdl_name':sdl.assignInfo[sdl.NONE_FUNC_NAME][BV_NAME].getAssignNode().getRight().getAttribute(), 'setting':sdl.assignInfo[sdl.NONE_FUNC_NAME][ALGEBRAIC_SETTING].getAssignNode().getRight().getAttribute(), 'assignInfo':assignInfo_reduction, 'typesBlock':sdl.getFuncStmts( TYPES_HEADER ), 'userCodeBlocks':list(set(list(assignInfo_reduction.keys())).difference(cm.functionOrder + [TYPES_HEADER, NONE_FUNC_NAME]))}


    # this consists of the type of the input scheme (e.g., symmetric)
    setting = sdl.assignInfo[sdl.NONE_FUNC_NAME][ALGEBRAIC_SETTING].getAssignNode().getRight().getAttribute()
    # name of the scheme
    sdl_name = sdl.assignInfo[sdl.NONE_FUNC_NAME][BV_NAME].getAssignNode().getRight().getAttribute()

    typesBlock = sdl.getFuncStmts( TYPES_HEADER )
    info = {'verbose':verbose}

    # we want to ignore user defined functions from our analysis
    # (unless certain variables that we care about are manipulated there)
    userCodeBlocks = list(set(list(assignInfo_reduction.keys())).difference(cm.functionOrder + [TYPES_HEADER, NONE_FUNC_NAME]))
    options['userFuncList'] += userCodeBlocks

    lines = list(typesBlock[0].keys())
    lines.sort()
    typesBlockLines = [ i.rstrip() for i in sdl.getLinesOfCodeFromLineNos(lines) ]
    begin = ["BEGIN :: " + TYPES_HEADER]
    end = ["END :: " + TYPES_HEADER]

    # start constructing the preamble for the Asymmetric SDL output
    newLines0 = [ BV_NAME + " := " + sdl_name, SETTING + " := " + sdl.ASYMMETRIC_SETTING ] 
    newLines1 = begin + typesBlockLines + end
    # this fact is already verified by the parser
    # but if scheme claims symmetric
    # and really an asymmetric scheme then parser will
    # complain.
    assert setting == sdl.SYMMETRIC_SETTING, "No need to convert to asymmetric setting."    
    # determine user preference in terms of keygen or encrypt
    short = SHORT_DEFAULT # default option
    if hasattr(cm, 'short'):
        if cm.short in SHORT_OPTIONS:
            short = cm.short
    print("reducing size of '%s'" % short) 

    varTypes = dict(sdl.getVarTypes().get(TYPES_HEADER))
    typesH = dict(varTypes)
    if not hasattr(cm, 'schemeType'):
        sys.exit("'schemeType' option missing in specified config file.")
    pairingSearch = []
    # extract the statements, types, dependency list, influence list and exponents of influence list
    # for each algorithm in the SDL scheme
    (stmtS, typesS, depListS, depListNoExpS, infListS, infListNoExpS) = sdl.getVarInfoFuncStmts( cm.reducSetupFuncName )
    (stmtQ, typesQ, depListQ, depListNoExpQ, infListQ, infListNoExpQ) = sdl.getVarInfoFuncStmts( cm.reducQueryFuncName )
    (stmtC, typesC, depListC, depListNoExpC, infListC, infListNoExpC) = sdl.getVarInfoFuncStmts( cm.reducChallengeFuncName )
    varTypes.update(typesS)
    varTypes.update(typesQ)
    varTypes.update(typesC)
    print(stmtS)
    print(stmtQ)
    print(depListS)
    print(depListNoExpS)
    # TODO: expand search to encrypt and potentially setup
    pairingSearch += [stmtS, stmtQ, stmtC] # aka start with decrypt.
            
    info[curveID] = options['secparam']
    info[dropFirstKeyword] = options[dropFirstKeyword]
    gen = Generators(info)
    # JAA: commented out for benchmarking    
    #print("List of generators for scheme")
    # retrieve the generators selected by the scheme
    # typically found in the setup routine in most cases.
    # extract the generators from the setup and keygen routine for later use
    if hasattr(cm, 'reducSetupFuncName'):
        gen.extractGens(stmtS, typesS)
    if hasattr(cm, 'reducQueryFuncName'):
        gen.extractGens(stmtQ, typesQ)
    if hasattr(cm, 'reducChallengeFuncName'):
        gen.extractGens(stmtC, typesC)
    else:
        sys.exit("Assumption failed: setup not defined for this function. Where to extract generators?")
    generators = gen.getGens()
    # JAA: commented out for benchmarking    
    print("Generators extracted: ", generators)

    # need a Visitor class to build these variables  
    # TODO: expand to other parts of algorithm including setup, keygen, encrypt
    # Visits each pairing computation in the SDL and
    # extracts the inputs. This is the beginning of the
    # analysis of these variables as the SDL is converted into
    # an asymmetric scheme.
    hashVarList = []
    pair_vars_G1_lhs = [] 
    pair_vars_G1_rhs = []    
    gpv = GetPairingVariables(pair_vars_G1_lhs, pair_vars_G1_rhs)
    print(pairingSearch)
    for eachStmt in pairingSearch: # loop through each pairing statement
        print(pair_vars_G1_lhs)            
        lines = eachStmt.keys() # for each line, do the following
        for i in lines:
            print(pair_vars_G1_lhs)            
            if type(eachStmt[i]) == sdl.VarInfo: # make sure we have the Var Object
                #print("Each: ", eachStmt[i].getAssignNode())
                # assert that the statement contains a pairing computation
                if HasPairings(eachStmt[i].getAssignNode()):
                    path_applied = []
                    # split pairings if necessary so that we don't influence
                    # the solve in anyway. We can later recombine these during
                    # post processing of the SDL
                    eachStmt[i].assignNode = SplitPairings(eachStmt[i].getAssignNode(), path_applied)
                    # JAA: commented out for benchmarking                    
                    #if len(path_applied) > 0: print("Split Pairings: ", eachStmt[i].getAssignNode())
                    if info['verbose']: print("Each: ", eachStmt[i].getAssignNode())
                    print(eachStmt[i].assignNode)
                    sdl.ASTVisitor( gpv ).preorder( eachStmt[i].getAssignNode() )
                elif eachStmt[i].getHashArgsInAssignNode(): 
                    # in case there's a hashed value...build up list and check later to see if it appears
                    # in pairing variable list
                    print("hash => ", str(eachStmt[i].getAssignVar()))
                    hashVarList.append(str(eachStmt[i].getAssignVar()))
                else:
                    continue # not interested
                
    # constraint list narrows the solutions that
    # we care about
    constraintList = []
    # for example, include any hashed values that show up in a pairing by default
    for i in hashVarList:
        if i in pair_vars_G1_lhs or i in pair_vars_G1_rhs:
            constraintList.append(i)
    # JAA: commented out for benchmarking            
    print("pair vars LHS:", pair_vars_G1_lhs)
    print("pair vars RHS:", pair_vars_G1_rhs) 
    print("list of gens :", generators)
    print("constraintList: ", constraintList)
    # for each pairing variable, we construct a dependency graph all the way back to
    # the generators used. The input of assignTraceback consists of the list of SDL statements,
    # generators from setup, type info, and the pairing variables.
    # We do this analysis for both sides
    info[ 'G1_lhs' ] = (pair_vars_G1_lhs, assignTraceback(assignInfo_reduction, generators, varTypes, pair_vars_G1_lhs, constraintList))
    info[ 'G1_rhs' ] = (pair_vars_G1_rhs, assignTraceback(assignInfo_reduction, generators, varTypes, pair_vars_G1_rhs, constraintList))

    depList = {}
    for i in [depListS, depListQ, depListC]:
        for (key, val) in i.items():
            print(key, val)
            if(not(len(val) == 0) and not(key == 'input') and not(key == 'output')):
                depList[key] = val
    print(depList)

    print("\n")
    info[ 'deps' ] = (depList, assignTraceback(assignInfo_reduction, generators, varTypes, depList, constraintList))
    print(info['deps'][1])

    print("\n")

    reductionData['info'] = info
    reductionData['depList'] = depList
    reductionData['deps'] = info['deps']

    return reductionData

def configAutoGroup(dest_path, sdl_file, config_file, output_file, verbose, benchmarkOpt, estimateOpt):
    # get full path (assuming not provided)
    full_config_file = os.path.abspath(config_file)
    pkg_name = os.path.basename(full_config_file)
    
    cm = imp.load_source(pkg_name, full_config_file)

    #parse assumption arguments
    if not hasattr(cm, "assumption"):
        print("No assumption specified")
        #sys.exit("configAutoGroup: need to set 'assumption' in config.") #TODO: add back in when finished and remove else
    else:
        assumptionFile = os.path.dirname(full_config_file) + "/" + cm.assumption + ".sdl" #TODO: how to determine location of assumption SDL file??
        assumptionData = parseAssumptionFile(cm, assumptionFile, verbose, benchmarkOpt, estimateOpt)
        setattr(cm, functionOrder, None)

    #parse reduction arguments
    if not hasattr(cm, "reduction"):
        print("No reduction specified")
        #sys.exit("configAutoGroup: need to set 'reduction' in config.") #TODO: add back in when finished and remove else
    else:
        reductionFile = os.path.dirname(full_config_file) + "/" + cm.reduction + ".sdl" #TODO: how to determine location of reduction SDL file??
        reductionData = parseReductionFile(cm, reductionFile, verbose, benchmarkOpt, estimateOpt)
        setattr(cm, functionOrder, None)

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
    outfile = runAutoGroup(sdl_file, cm, options, verbose, assumptionData, reductionData)
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
