"""Standalone generator of LaTeX from SDL descriptions"""
import os, re, sys, getopt, imp, time
import sdlpath
import SDLParser2 as sdl
from SDLang import *

PKENC = "PKENC" # encryption
PKSIG = "PKSIG" # signatures
functionOrder = "functionOrder"
hashtag = "#"
comma = ","
times = " \\times "
NoneKeyword = "None"

encConfigParams = ["keygenPubVar", "keygenSecVar", "ciphertextVar", "keygenFuncName", "encryptFuncName", "decryptFuncName"]
sigConfigParams = ["keygenPubVar", "keygenSecVar", "signatureVar", "keygenFuncName", "signFuncName", "verifyFuncName"]
configDef = {'keygenPubVar': 'public key', 'keygenSecVar': 'secret key', 'ciphertextVar': 'ciphertext', 'signatureVar': 'signature' }

template_top = """
\documentclass[11pt]{article}
\\usepackage{fullpage,amsthm,amsmath}
\\usepackage{latexsym,amssymb,xspace,paralist}
\\renewenvironment{itemize}[1]{\\begin{compactitem}#1}{\end{compactitem}}
"""

template_header = "\n\\begin{document}\n"
template_end    = "\end{document}\n"


fixed_cmds = """
\\newcommand{\Zq}{\mathbb{Z}_q}
\\newcommand{\G}{\mathbb{G}}
"""

funcname_cmd = "\\newcommand{\%s}{{\sf %s}}\n"
varname_cmd  = "\\newcommand{%s}{%s}\n"

content_header = "\\begin{itemize}\n"
content_line   = "\item[-] %s\n"
content_end    = "\end{itemize}\n"

def getList(listNode):
    newList = list(listNode)
    if NoneKeyword in newList:
        newList.remove(NoneKeyword)
    return newList

def printCommaList(_list):
    listStr = ""
    for i in _list:
        listStr += i + comma
    listStr = listStr[:-len(comma)]
    return listStr

def handleKeywords(config, varList):
    output = " "
    if hasattr(config, "keygenPubVar") and config.keygenPubVar in varList:
        output += configDef["keygenPubVar"] + ", " + config.keygenPubVar + " "
    if hasattr(config, "keygenSecVar") and config.keygenSecVar in varList:
        output += configDef["keygenSecVar"] + ", " + config.keygenSecVar + " "
    if hasattr(config, "ciphertextVar") and config.ciphertextVar in varList:
        output += configDef["ciphertextVar"] + ", " + config.ciphertextVar + " "
    if hasattr(config, "signatureVar") and config.signatureVar in varList:
        output += configDef["signatureVar"] + ", " + config.signatureVar + " "
    return output

def computeHashIndex(hashSigs, inputList, targetType):
    countList = list(hashSigs.keys())
    countList.sort()
    if len(countList) > 0: count = countList[-1]
    else: count = 1
    
    key = (str(inputList), str(targetType))
    print("DEBUG: Hash type signature => ", key)
    if key in hashSigs.keys():
        return hashSigs[key]
    else:
        hashSigs[ key ] = count
        return count    

def generateLatexFuncs(tcObj, funcName, config, blockStmts, hashSigs, latexBlock=None):
    sdlVarType = tcObj.getSDLVarType()
    randomElems = {'ZR':'\Zq', 'G1':'\G_1', 'G2':'\G_2', 'GT':'\G_T', 'Str':'\{0, 1\}^*', 'Int':'\Z'}
    
    lines = list(blockStmts.keys())
    lines.sort()
    
    lcg = LatexCodeGenerator(latexBlock)
    data = {sdl.inputKeyword:None, sdl.outputKeyword:None}
    defines       = [funcname_cmd % (str(funcName), str(funcName).title())]
    random_assign = []
    compute       = []
    preamble      = []
    for index, i in enumerate(lines):
        assert type(blockStmts[i]) == sdl.VarInfo, "transformFunction: blockStmts must be VarInfo Objects."
        if blockStmts[i].getHasRandomness():
            print("Randomness: ", blockStmts[i].getAssignNode(), blockStmts[i].getAssignNode().getRight().left)
            varName = lcg.print_statement(blockStmts[i].getAssignNode().getLeft()) # blockStmts[i].getAssignVar()
            the_type = randomElems.get( str(blockStmts[i].getAssignNode().getRight().left) )
            random_assign.append( "$" + varName + " \leftarrow " + the_type + "$")
        elif blockStmts[i].getAssignVar() == sdl.inputKeyword:
            inputNode = blockStmts[i].getAssignNode().getRight()
            print("Input: ", inputNode)
            if Type(inputNode) == ops.LIST: # and NoneKeyword not in inputNode.listNodes:
                data[sdl.inputKeyword] = getList(inputNode.listNodes)
            elif Type(inputNode) == ops.ATTR:
                if str(inputNode) == NoneKeyword:
                    data[sdl.inputKeyword] = []
                else:
                    data[sd.inputKeyword] = [str(inputNode)]
        elif blockStmts[i].getAssignVar() == sdl.outputKeyword:
            outputNode = blockStmts[i].getAssignNode().getRight()
            print("Output: ", outputNode)
            if Type(outputNode) == ops.LIST:
                data[sdl.outputKeyword] = getList(outputNode.listNodes)
                output_str = "(" + printCommaList(data[sdl.outputKeyword]) + ")"
            elif Type(outputNode) == ops.ATTR:
                data[sdl.outputKeyword] = str(outputNode)
                output_str = data[sdl.outputKeyword]
            else:
                print("ERROR: Can't process output of function :", funcName)
        elif blockStmts[i].getIsExpandNode():
            varName = lcg.print_statement(blockStmts[i].getAssignNode().getLeft())
            varExpand = lcg.print_statement(blockStmts[i].getAssignNode().getRight())
            compute.append( "Parse $" + varName + "$ as $" + varExpand + "$" )
            
        elif blockStmts[i].getIsForLoopBegin(): # TODO
            #if blockStmts[i].getIsForType(): newLines.append(parser.parse("BEGIN :: for\n")) # "\n" + START_TOKEN + " " + BLOCK_SEP + ' for')
            #elif blockStmts[i].getIsForAllType(): newLines.append(parser.parse("BEGIN :: forall\n"))  # "\n" + START_TOKEN + " " + BLOCK_SEP + ' forall')
            pass
        elif blockStmts[i].getIsForLoopEnd():
            pass
        elif blockStmts[i].getIsIfElseEnd():
            pass
        elif blockStmts[i].getIsElseBegin():
            pass
        elif blockStmts[i].getHashArgsInAssignNode():
            # convert input list to types list ==> for signature
            inputList = []
            argList = ""
            for j in blockStmts[i].getHashArgsInAssignNode():
                the_type = sdlVarType.get(str(j))
                inputList.append( the_type )
                argList += randomElems.get(str(the_type)) + times
            argList = argList[:-len(times)]
            # find or create hash index
            index = computeHashIndex(hashSigs, inputList, blockStmts[i].getHashArgType() )
            # add new index to preamble
            preamble.append( '$H_'+str(index) + " : " + argList + " \\rightarrow " + randomElems.get(str(blockStmts[i].getHashArgType())) + "$" )
            lcg.defineHashIndex(index)
            compute.append( "$" + lcg.print_statement(blockStmts[i].getAssignNode()) + "$" )
            lcg.clearHashIndex()
        else:
            print("Compute: ", blockStmts[i].getAssignNode(), ":", lcg.print_statement(blockStmts[i].getAssignNode()))
            compute.append( "$" + lcg.print_statement(blockStmts[i].getAssignNode()) + "$" )
    
    print("FUNC    => ", funcName)
    print("Inputs  => ", data[sdl.inputKeyword])
    print("Random  => ", random_assign)
    print("Outputs => ", data[sdl.outputKeyword])
    output = "\\" + funcName + ". "
    if len(data[sdl.inputKeyword]) == 0:
        output += "On input a security parameter $1^\lambda$, "
    else:
        defines.append( varname_cmd % ("\\" + funcName + "Vars", printCommaList(data[sdl.inputKeyword])) )
        defs = handleKeywords(config, data[sdl.inputKeyword])
        output += "On input $\\" + funcName + "Vars$" 
        if len(defs) > 1: output += ", where " + defs + "\n"
        else: output += ".\n"
    # choose random elements
    rnd_str = "Choose "
    for i in random_assign:
        rnd_str += i + comma
    if len(random_assign) > 0:
        rnd_str = rnd_str[:-len(comma)]
        output += rnd_str + "\n"
    # add compute elements
    output += content_header
    for i in compute:
        output += content_line % i
    
    output += "\item[-] Output = $" + output_str + "$\n"
    output += content_end
    return (defines, preamble, output)

class SDL2LaTeX:
    def __init__(self, sdlName):
        self.sdlName = sdlName.upper()
        self.defines = []
        self.funcDefs = []
        self.premableDef = []
        
    def buildConfig(self, definesForFunc, preamble, outputForFunc):
        for i in definesForFunc:
            self.defines.append(i)
        for i in preamble:
            if i not in self.premableDef:
                self.premableDef.append(i)
        self.funcDefs.append( outputForFunc )
        
        
    def writeConfig(self):
        # write header
        output = template_top
        output += fixed_cmds
        for i in self.defines:
            output += i
        
        output += template_header
        output += "\section*{"+ self.sdlName + " Scheme Description}\n\n"
        if len(self.premableDef) > 0:
            preamble_str = "The scheme selects "
            for i in self.premableDef:
                preamble_str += i + comma
            preamble_str = preamble_str[:-len(comma)]
            output += preamble_str + "\n\n" 
        # write body
        for i in self.funcDefs:
            output += i + "\n"
        output += template_end
        
        
        print("<=========== OUTPUT ===========>")
        print(output)
        print("<=========== OUTPUT ===========>")
        return
        
class LatexCodeGenerator:
    def __init__(self, latex_info):
        self.latex  = latex_info # used for substituting attributes
        self.latexVars  = {'alpha':'\\alpha', 'beta':'\beta', 'gamma':'\gamma', 'delta':'\delta', 'epsilon':'\epsilon',
             'zeta':'\zeta', 'eta':'\eta', 'Gamma':'\Gamma', 'Delta':'\Delta', 'theta':'\theta', 
             'kappa':'\kappa', 'lambda':'\lambda', 'mu':'\mu', 'nu':'\\nu', 'xi':'\\xi', 'sigma':'\\sigma',
             'tau':'\\tau', 'phi':'\phi', 'chi':'\\chi', 'psi':'\psi', 'omega':'\omega'}
        self.hash_index = 0
    
    def getLatexVersion(self, name):
        if self.latex != None and self.latex.get(name) != None:
            return self.latex[ name ]        
        elif name.find(hashtag) != -1: # matches words separated by hashtags. x#1 => 'x_1'
            return name.replace(hashtag, underscore)
        elif name.find("G1") != -1:
            return "\hat{" + self.getLatexVersion( name.replace("G1", "") ) + "}"
        elif name.find("G2") != -1:
            return "\\bar{" + self.getLatexVersion( name.replace("G2", "") ) + "}"
        else:
            # matches word + numbers => 'x1' => 'x_1'
            res = re.findall(r"[a-zA-Z]+|\d+", name)
            if len(res) == 2:
                return name.replace(res[0] + res[1], res[0] + "_" + res[1])
            else:
                for i,j in self.latexVars.items():
                    if i in name: return name.replace(i, j)
#            return self.latexVars.get(name)
        return name    
    def defineHashIndex(self, index):
        self.hash_index = index
        return
    
    def clearHashIndex(self):
        self.hash_index = 0
        return
    
    def getList(self, listNode):
        newList = []
        for i in listNode:
            if i != NoneKeyword:
                newList.append( self.getLatexVersion(i) )
        return newList
        
    def print_statement(self, node, parent=None):
        if node == None:
            return None
        elif(node.type == ops.ATTR):
            msg = node.attr
            if 'delta' in str(msg):
                msg = '\delta'
            elif str(msg) =='N':
                msg = '\\numsigs'
            else:
                msg = self.getLatexVersion(str(msg))
#                if msg.find('_') != -1: msg = "{" + msg + "}" # prevent subscript
#            print("msg : ", msg)
            if node.delta_index != None and 'delta' in node.attr:
#                print("Found IT!!!")
                msg = msg + '_{' + node.delta_index[0] + '}'
            if node.attr_index != None:
                keys = ""
                if msg.find('_') != -1:
                    s = msg.split('_', 1)
                    #print("s : ", s)
                    for i in node.attr_index:
                        keys += i + ","
                    keys = keys[:len(keys)-1]
                    msg = s[0] + '_{' + keys + "," + s[1] + '}'
                    #print("msg :=", msgs)
                else:
                    for i in node.attr_index:
                        keys += i + ","
                    keys = keys[:len(keys)-1]
                    if len(node.attr_index) > 1:
                        msg += '_{' + keys + '}'
                    else:
                        msg += '_' + keys
                    msg = "{" + msg + "}"
#                    print("result: ", msg)
            if node.negated: msg = '-' + msg
#            print("msg2 : ", msg)
            return msg
        elif(node.type == ops.TYPE):
            return str(node.attr)
        else:
            left = self.print_statement(node.left, node)
            right = self.print_statement(node.right, node)

            if debug >= levels.some:
               print("Operation: ", node.type)
               print("Left operand: ", left)
               print("Right operand: ", right)            
            if(node.type == ops.EXP):
                if Type(node.left) == ops.EXP:
                    l = self.print_statement(node.left.left)
                    r = self.print_statement(node.left.right)
                    return ( l + "^{" + r + ' \cdot ' + right + "}")
                elif Type(node.left) in [ops.ATTR, ops.PAIR]:
                    if str(right) == "1": return left 
                    return ( left + '^{' + right + "}")
                return ("(" + left + ')^{' + right + "}")
            elif(node.type == ops.MUL):
                return ( left + ' \cdot ' + right )
            elif(node.type == ops.DIV):
                return ( left + ' / ' + right )
            elif(node.type == ops.ADD):
                return ("("+ left + ' + ' + right + ")")
            elif(node.type == ops.SUB):
                return ("("+ left + ' - ' + right + ")")
            elif(node.type == ops.EQ):
                if parent != None and parent.type == ops.PROD:
                    return (left + ' = ' + str(right).replace("0", "1"))
                else:
                    return (left + ' = ' + str(right))
            elif(node.type == ops.EQ_TST):
                return (left + ' \stackrel{?}{=} ' + right)
            elif(node.type == ops.PAIR):
                return ('e(' + left + ',' + right + ')')
            elif(node.type == ops.HASH):
                if self.hash_index == 0:
                    return ('H(' + left + ')')
                else:
                    return ('H_'+str(self.hash_index) + "(" + left + ")")
            elif(node.type == ops.SUM):
                return ('\sum_{' + left + '}^{' + right + '}')
            elif(node.type == ops.PROD):
                return ('\prod_{' + left + '}^' + right)
            elif(node.type == ops.ON):
                return ("{" + left + " " + right + "}")
            elif(node.type == ops.OF):
                return ("{" + left + " " + right + "}")
            elif(node.type == ops.CONCAT):
                 return (left + ' | ' + right)
            elif(node.type == ops.FOR):
                return ('\\text{for }' + left + '\\text{ to }  ' + right)
            elif(node.type == ops.DO):
                 return ( left + ' \\text{ it holds: }  ' + right)
            elif(node.type == ops.AND):
                 return ( left + " \mbox{ and } " + right )
            elif(node.type in [ops.LIST, ops.EXPAND]):
                 return ( "(" + printCommaList(self.getList(node.listNodes)) + ")")
            elif(node.type == ops.IF):
                 return ( "\mbox{if }{" + left + "}")
            elif(node.type == ops.ELSE):
                 return " or else " 
        return None


def errorOut(keyword):
    sys.exit("configAutoGroup: missing '%s' variable in config." % keyword)

def readConfig(dest_path, sdl_file, config_file, output_file, verbose):
    # get full path (assuming not provided)
    full_config_file = os.path.abspath(config_file)
    pkg_name = os.path.basename(full_config_file)
    
    config = imp.load_source(pkg_name, full_config_file)
    # setup sdl parser configs
    sdl.masterPubVars = config.masterPubVars
    sdl.masterSecVars = config.masterSecVars
    if not hasattr(config, "schemeType"):
        sys.exit("configAutoGroup: need to set 'schemeType' in config.")
    
    if config.schemeType == PKENC and getattr(config, functionOrder, None) == None:
        funcOrder = [config.setupFuncName, config.keygenFuncName, config.encryptFuncName, config.decryptFuncName]
        setattr(config, functionOrder, funcOrder)
    elif config.schemeType == PKSIG and getattr(config, functionOrder, None) == None:
        funcOrder = [config.setupFuncName, config.keygenFuncName, config.signFuncName, config.verifyFuncName]
        setattr(config, functionOrder, funcOrder)

    print("function order: ", config.functionOrder)
    
    if config.schemeType == PKENC:
        for i in encConfigParams:
            if not hasattr(config, i):
                errorOut(i)
    elif config.schemeType == PKSIG:
        for i in sigConfigParams:
            if not hasattr(config, i):
                errorOut(i)
    
    # call parseFile on SDL
    tcObj = sdl.parseFile(sdl_file, verbose, ignoreCloudSourcing=True)
    assignInfo = sdl.getAssignInfo()
#    setting = sdl.assignInfo[sdl.NONE_FUNC_NAME][ALGEBRAIC_SETTING].getAssignNode().getRight().getAttribute()
    sdl_name = sdl.assignInfo[sdl.NONE_FUNC_NAME][BV_NAME].getAssignNode().getRight().getAttribute()
    latex_info = assignInfo.get(sdl.LATEX_HEADER)
    latexBlock = {}
    if latex_info != None:
        for i,j in latex_info.items():
            latexBlock[ i ] = j.getLineStrValue()

    print("Processing... ", sdl_name)
    
    # 1. Start with Keygen/Setup ... 
    sdl2tex = SDL2LaTeX(sdl_name)
    hashSigs = {}
    if hasattr(config, "setupFuncName"):
        (stmtS, typesS, depListS, depListNoExpS, infListS, infListNoExpS) = sdl.getVarInfoFuncStmts( config.setupFuncName )
        defines, preamble, latexOutputSetup = generateLatexFuncs(tcObj, config.setupFuncName, config, stmtS, hashSigs)
        sdl2tex.buildConfig(defines, preamble, latexOutputSetup)
        funcOrder.remove(config.setupFuncName)
        
    if hasattr(config, "keygenFuncName"):
        (stmtK, typesK, depListK, depListNoExpK, infListK, infListNoExpK) = sdl.getVarInfoFuncStmts( config.keygenFuncName )
        defines, preamble, latexOutputKeygen = generateLatexFuncs(tcObj, config.keygenFuncName, config, stmtK, hashSigs)
        sdl2tex.buildConfig(defines, preamble, latexOutputKeygen)
        funcOrder.remove(config.keygenFuncName)

    # 2. call each function and produce a block of latex code
    for funcName in funcOrder:
        (stmtF, typesF, depListF, depListNoExpF, infListF, infListNoExpF) = sdl.getVarInfoFuncStmts( funcName ) 
        defines, preamble, latexOutputFunc = generateLatexFuncs(tcObj, funcName, config, stmtF, hashSigs)
        sdl2tex.buildConfig(defines, preamble, latexOutputFunc)
    
    # 3. print info to the template
    sdl2tex.writeConfig()
        

if __name__ == "__main__":
    sdl_file = sys.argv[1]
    config_file = sys.argv[2]
    output_file = "foo"
    
    readConfig("", sdl_file, config_file, output_file, False)