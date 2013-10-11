# This class generates the latex macros for the batch verification proofs of security
import sdlpath, re, string
from SDLang import * 

hashtag = '#'
underscore = '_'
header = """\n
\\catcode`\^ = 13 \def^#1{\sp{#1}{}}
\\newcommand{\\newln}{\\\&\quad\quad{}}
\\newcommand{\schemename}{{\sf %s}}
\\newcommand{\schemeref}{%s_proof}
\\newcommand{\schemecite}{\cite{REF}}
\\newcommand{\\randomsecretkeys}{ %s }
\\newcommand{\secretkey}{ %s }
\\newcommand{\listofbfs}{ %s }
\\newcommand{\listofmskvalues}{ %s }
\\newcommand{\listofrandomvalues}{ %s }
\\newcommand{\keydefinitions}{ %s }
\\newcommand{\originalkey}{ %s }
\\newcommand{\\transformkey}{ %s }
\\newcommand{\pseudotransformkey}{ %s }
\\newcommand{\expandedtransformkey}{ %s }
"""

headerCT = "\n\\newcommand{\ciphertext}{ %s }\n"

header_transform = """\n
\\newcommand{\gutsoftransform}{
\\transform(\CT, \TK) \\rightarrow \CT'
"""

header_decrypt = """\n
\\newcommand{\gutsofdecrypt}{
"""

header_decout = """\n
\\newcommand{\gutsofdecout}{
\decout(\CT', \SK) \\rightarrow M
"""

proof_footer = "\n}\n"

basic_step = """\medskip \\noindent
{\\bf Step %d:} %s:
\\begin{equation}
%s
\end{equation}
""" # (step #, message of what we are doing, resulting equation)

basic_step2 = """\medskip \\noindent
{\\bf Step %s:} %s:
\\begin{equation}
%s
\end{equation}
""" # (step #, message of what we are doing, resulting equation)

#small_exp_label = "\label{eqn:smallexponents}\n"
#final_batch_eq  = "\label{eqn:finalequation}\n"

transformOutputList = "transformOutputList"
main_proof_header_standalone = """\n"""
NoneKeyword = "None"
comma = ","

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

class LatexCodeGenerator:
    def __init__(self, latex_info):
        self.latex  = latex_info # used for substituting attributes
        self.latex[ transformOutputList ] = "\CT'"
        self.latex[ "Blinded" ] = "'"
        self.latexVars  = {'alpha':'\\alpha', 'beta':'\beta', 'gamma':'\gamma', 'delta':'\delta', 'epsilon':'\epsilon',
             'zeta':'\zeta', 'eta':'\eta', 'Gamma':'\Gamma', 'Delta':'\Delta', 'theta':'\theta', 
             'kappa':'\kappa', 'lambda':'\lambda', 'mu':'\mu', 'nu':'\\nu', 'xi':'\\xi', 'sigma':'\\sigma',
             'tau':'\\tau', 'phi':'\phi', 'chi':'\\chi', 'psi':'\psi', 'omega':'\omega'}
        self.sdlTypes   = {'ZR':'\Zp^*', 'G1':'\G_1', 'G2':'\G_2', 'GT':'\G_T', 'Str':'\{0, 1\}^*', 'Int':'\Z'}
        self.hash_index = 0
    
    def getLatexVersion(self, name):
        if self.latex != None and self.latex.get(name) != None:
            return self.latex[ name ]
        elif name.find(hashtag) != -1: # matches words separated by hashtags. x#1 => 'x_1'
            newName = name.replace(hashtag, underscore) 
            for i,j in self.latex.items():
                if i in newName:
                    newName = newName.replace(i, j)
                    break
            return newName
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
                for i,j in self.latex.items():
                    if i in name: return self.getLatexVersion( name.replace(i, j) )
                
#            return self.latexVars.get(name)
        return name    
    
    def getType(self, type_node):
        t = str(type_node)
        if t in self.sdlTypes.keys():
            return self.sdlTypes[t]
        return 'None'
             
    
    def defineHashIndex(self, index):
        self.hash_index = index
        return
    
    def clearHashIndex(self):
        self.hash_index = 0
        return
        
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
                return ( left + ' \cdot ' + right)
            elif(node.type == ops.ADD):
                return ("("+ left + ' + ' + right + ")")
            elif(node.type == ops.SUB):
                return ("("+ left + ' - ' + right + ")")
            elif(node.type == ops.EQ):
                if parent != None and parent.type == ops.PROD:
                    return (left + ' = ' + str(right).replace("0", "1"))
                elif node.right != None and node.right.type == ops.RANDOM:
                    return (left + " " + str(right))
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
                 return ( "(" + printCommaList(getList(node.listNodes)) + ")")
            elif(node.type == ops.IF):
                 return ( "\mbox{if }{" + left + "}")
            elif(node.type == ops.ELSE):
                 return " or else "
            elif(node.type == ops.RANDOM):
                 return "\\rightarrow " + self.getType(node.left)
        return None

# OLD GENERATOR
#class LatexCodeGenerator:
#    def __init__(self):
#        self.latexVars  = {'alpha':'\\alpha', 'beta':'\beta', 'gamma':'\gamma', 'delta':'\delta', 'epsilon':'\epsilon',
#             'zeta':'\zeta', 'eta':'\eta', 'Gamma':'\Gamma', 'Delta':'\Delta', 'theta':'\theta', 
#             'kappa':'\kappa', 'lambda':'\lambda', 'mu':'\mu', 'nu':'\\nu', 'xi':'\\xi', 'sigma':'\\sigma',
#             'tau':'\\tau', 'phi':'\phi', 'chi':'\\chi', 'psi':'\psi', 'omega':'\omega'}
#        
#    def getLatexVersion(self, name):
#        if name.find(hashtag) != -1: # matches words separated by hashtags. x#1 => 'x_1'
#            return name.replace(hashtag, underscore)
#        elif name.find("G1") != -1:
#            return name.replace("G1", "_1")
#        elif name.find("G2") != -1:
#            return name.replace("G2", "_2")
#        else:
#            # matches word + numbers => 'x1' => 'x_1'
#            res = re.findall(r"[a-zA-Z]+|\d+", name)
#            if len(res) == 2:
#                return name.replace(res[0] + res[1], res[0] + "_" + res[1])
#            else:
#                for i,j in self.latexVars.items():
#                    if i in name: return name.replace(i, j)
##            return self.latexVars.get(name)
#        return name    
#    
#    def print_statement(self, node, parent=None):
#        if node == None:
#            return None
#        elif(node.type == ops.ATTR):
#            msg = node.attr
#            msg = self.getLatexVersion(str(msg))
#            if node.delta_index != None and 'delta' in node.attr:
##                print("Found IT!!!")
#                msg = msg + '_{' + node.delta_index[0] + '}'
#            if node.attr_index != None:
#                keys = ""
#                if msg.find('_') != -1:
#                    s = msg.split('_', 1)
#                    #print("s : ", s)
#                    for i in node.attr_index:
#                        keys += i + ","
#                    keys = keys[:len(keys)-1]
#                    msg = s[0] + '_{' + keys + "," + s[1] + '}'
#                    #print("msg :=", msgs)
#                else:
#                    for i in node.attr_index:
#                        keys += i + ","
#                    keys = keys[:len(keys)-1]
#                    if len(node.attr_index) > 1:
#                        msg += '_{' + keys + '}'
#                    else:
#                        msg += '_' + keys
#                    msg = "{" + msg + "}"
##                    print("result: ", msg)
#            if node.negated: msg = '-' + msg
##            print("msg2 : ", msg)
#            return msg
#        elif(node.type == ops.TYPE):
#            return str(node.attr)
#        else:
#            left = self.print_statement(node.left, node)
#            right = self.print_statement(node.right, node)
#
#            if debug >= levels.some:
#               print("Operation: ", node.type)
#               print("Left operand: ", left)
#               print("Right operand: ", right)            
#            if(node.type == ops.EXP):
#                if Type(node.left) == ops.EXP:
#                    l = self.print_statement(node.left.left)
#                    r = self.print_statement(node.left.right)
#                    return ( l + "^{" + r + ' \cdot ' + right + "}")
#                elif Type(node.left) in [ops.ATTR, ops.PAIR]:
#                    if str(right) == "1": return left 
#                    return ( left + '^{' + right + "}")
#                return ("(" + left + ')^{' + right + "}")
#            elif(node.type == ops.MUL):
#                return ( left + ' \cdot ' + right)
#            elif(node.type == ops.ADD):
#                return ("("+ left + ' + ' + right + ")")
#            elif(node.type == ops.SUB):
#                return ("("+ left + ' - ' + right + ")")
#            elif(node.type == ops.EQ):
#                if parent != None and parent.type == ops.PROD:
#                    return (left + ' = ' + str(right).replace("0", "1"))
#                else:
#                    return (left + ' = ' + str(right))
#            elif(node.type == ops.EQ_TST):
#                return (left + ' \stackrel{?}{=} ' + right)
#            elif(node.type == ops.PAIR):
#                return ('e(' + left + ',' + right + ')')
#            elif(node.type == ops.HASH):
#                return ('H(' + left + ')')
#            elif(node.type == ops.SUM):
#                return ('\sum_{' + left + '}^{' + right + '}')
#            elif(node.type == ops.PROD):
#                return ('\prod_{' + left + '}^' + right)
#            elif(node.type == ops.ON):
#                return ("{" + left + " " + right + "}")
#            elif(node.type == ops.OF):
#                return ("{" + left + " " + right + "}")
#            elif(node.type == ops.CONCAT):
#                 return (left + ' | ' + right)
#            elif(node.type == ops.FOR):
#                return ('\\text{for }' + left + '\\text{ to }  ' + right)
#            elif(node.type == ops.DO):
#                 return ( left + ' \\text{ it holds: }  ' + right)
#            elif(node.type == ops.AND):
#                 return ( left + " \mbox{ and } " + right )
#            elif(node.type == ops.OR):
#                 return ( left + " \mbox{ or } " + right )
#             
#        return None

class GenerateProof:
    def __init__(self):
        self.__lcg_decrypt_data = {} 
        self.__lcg_decrypt_count = 0
        self.__lcg_transform_data = {} 
        self.__lcg_transform_count = 0
        self.lcg = None
        self.stepPrefix = ''
        self.__lcg_start_pair = {}
        self.__lcg_start_pair_cnt = 0
        self.__lcg_combine_pair = {}
        self.__lcg_combine_pair_cnt = 0
        self.__lcg_buckets_pair = {}
        self.__lcg_buckets_pair_cnt = 0
        self.__lcg_unblinded_pair = {}
        self.__lcg_unblinded_pair_cnt = 0
        self.__lcg_decout_data = {}
        self.__lcg_decout_count = 0
        self.bucket_counter = 1 # use in bucket section
        self.finalPartCT = []
        self.expandPartCT = []
        self.parser = None
        self.verbose = False
    
    def setParser(self, objRef):
        self.parser = objRef
        return
    
    def setPrefix(self, prefixStr):
        assert type(prefixStr) == str, "expecting string for the step prefix."
        self.stepPrefix = prefixStr
        return
        
    def initLCG(self, latex_block, rndList, skList, bfList, mskList, randList, keyDefsList): # , originalKeyNodes, transformKeyNodes, pseudoKey):
        if self.lcg == None:
            self.lcg = LatexCodeGenerator(latex_block)
            self.rndList = rndList
            self.skList = skList
            self.bfList = bfList
            self.mskList = mskList
            self.randList = randList
            self.keyDefsList = keyDefsList
            self.ctList = None
            self.latex_file = None
            self.originalKeyList = []
            self.transformKeyList = []
            self.pseudoTK = []
            self.expandedTK = []
            return True
        else:
            # init'ed already
            return False
    
    def setOriginalKey(self, originalKeyNodes):
        assert self.lcg != None, "LatexCodeGen not initialized yet."
        self.originalKeyList = originalKeyNodes
        return
    
    def setTransformKey(self, transformKeyNodes):
        assert self.lcg != None, "LatexCodeGen not initialized yet."
        self.transformKeyList = transformKeyNodes
        return
    
    def setPseudoTK(self, pseudoTK):
        assert self.lcg != None, "LatexCodeGen not initialized yet."
        self.pseudoTK = pseudoTK
        return
    
    def setExpandedTK(self, expandedTK):
        assert self.lcg != None, "LatexCodeGen not initialized yet."
        self.expandedTK = expandedTK
        return
    
    def setSDLName(self, name):
        self.latex_file = name
        return
    
    def setCTVars(self, ctList):
        self.ctList = ctList
        return
    
    def setDecryptStep(self, node):
        assert self.lcg != None, "LatexCodeGen not initialized."
        msg = ""
        if node.type == ops.EQ:
            # check rhs
            if node.right.type == ops.FUNC: return
            msg = "Compute $" + self.lcg.print_statement(node.left) + "$"
        self.__lcg_decrypt_data[ self.__lcg_decrypt_count ] = {'msg': msg, 'eq': self.lcg.print_statement( node ) }
        self.__lcg_decrypt_count += 1
        return
    
    def setTransformStep(self, node, techs):
        assert self.lcg != None, "LatexCodeGen not initialized."
        msg = ""
        if node.type == ops.EQ:
            # check rhs
            if node.right.type == ops.FUNC: return
            msg = "" # + self.lcg.print_statement(node.left) 
            for i,j in techs.items():
                if i == 'applyTechnique11':
                    msg += "Unroll the product (if applicable), "
                if i == 'SimplifySDLNode' and j != None:
                    msg += "Simplified the equation (if applicable), "
            msg += "then compute $" + self.lcg.print_statement(node.left) + "$"
        self.__lcg_transform_data[ self.__lcg_transform_count ] = {'msg': msg, 'eq': self.lcg.print_statement( node ) }
        self.__lcg_transform_count += 1
        return

    def setDecoutStep(self, node): # TODO: improve to handle other node types
        assert self.lcg != None, "LatexCodeGen not initialized."
        msg = ""
        if node.type == ops.EQ:
            # check rhs
            if node.right.type == ops.FUNC: return
            msg = "Compute $" + self.lcg.print_statement(node.left) + "$"
        self.__lcg_decout_data[ self.__lcg_decout_count ] = {'msg': msg, 'eq': self.lcg.print_statement( node ) }
        self.__lcg_decout_count += 1
        return
    
    def setDecoutStepFromStr(self, node_str):
        assert self.parser != None
        node = self.parser.parse(node_str)
        return self.setDecoutStep(node)
    
    def setFinalPartialCT(self, node_str):
        assert self.parser != None
        eq_op = ":="
        test = node_str.split(eq_op)
        node = self.parser.parse(node_str)
        if  transformOutputList in test[0]: # tf must be on LHS
            self.finalPartCT.append( self.lcg.print_statement(node) )
        elif transformOutputList in test[1]:            
            self.expandPartCT.append( self.lcg.print_statement(node) )
        else:
            print("UNHANDLED CASE: ", node_str)
        return
    
    def setPrePartialCT(self, node_str):
        assert self.parser != None
        eq_op = ":="
        test = node_str.split(eq_op)
        if  transformOutputList in test[1]: # tf must be on RHS
            node = self.parser.parse(node_str)
            self.expandPartCT.append( self.lcg.print_statement(node) )
        else:
            print("UNHANDLED CASE: ", node_str)
        return
    
    def setStartPairs(self, lineNo, sdlList):
        assert self.lcg != None, "LatexCodeGen not initialized."
        if self.verbose:
            print("setStartPairs DEBUG: ", lineNo)
            print("setStartPairs DEBUG: ", sdlList)
        msg = "Some Message..."
        CM = ", "
        eqStr = ""        
        for node in sdlList:
            eqStr += self.lcg.print_statement( node ) + ", "
        eqStr = eqStr[:-len(CM)]
        self.__lcg_start_pair[ self.__lcg_start_pair_cnt ] = {'msg': msg, 'eq':eqStr }
        self.__lcg_start_pair_cnt += 1
        return
    
    def setCombinePairs(self, lineNo, sdlList):
        assert self.lcg != None, "LatexCodeGen not initialized."
        if self.verbose:        
            print("setCombinePairs DEBUG: ", lineNo)
            print("setCombinePairs DEBUG: ", sdlList)
        msg = "Some Message..."        
        CM = ", "
        eqStr = ""
        for node in sdlList:
            eqStr += self.lcg.print_statement( node ) + ", "
        eqStr = eqStr[:-len(CM)]
        self.__lcg_combine_pair[ self.__lcg_combine_pair_cnt ] = {'msg': msg, 'eq':eqStr }
        self.__lcg_combine_pair_cnt += 1
        return
    
    def setBuckets(self, lineNo, metaSdlList, metaSdlFactors, outputList):
        assert self.lcg != None, "LatexCodeGen not initialized."
        if self.verbose:        
            print("setBuckets DEBUG: ", lineNo)
            print("setBuckets DEBUG: ", metaSdlList)        
            print("setBuckets DEBUG: ", metaSdlFactors)
            print("setBuckets DEBUG: ", outputList)
        msg = "Organize pairings based on common blinding factors for "
        CM = " \cdot "
        AND = " and "
        listOfStr = []
        for i in range(len(metaSdlFactors)):
            eqStr = "{\CT'}_{" + str(self.bucket_counter) + "} = "
            self.bucket_counter += 1
            msg +=  "$" + self.lcg.getLatexVersion(str(metaSdlFactors[i][0])) + "$" + AND
            node2 = self.parser.parse( outputList[i] )
            listOfStr.append( self.lcg.print_statement(node2) )            
#            for node in metaSdlList[i]:
#                eqStr += self.lcg.print_statement( node ) + " \cdot "
#            eqStr = eqStr[:-len(CM)]
        msg = msg[:-len(AND)]
        self.__lcg_buckets_pair[ self.__lcg_buckets_pair_cnt ] = {'msg': msg, 'eq':listOfStr }
        self.__lcg_buckets_pair_cnt += 1
        return
    
    # starting point
    def proofHeader(self, title, list_rnds, list_sks, list_bfs, list_msk, list_rand, key_defs, original_key, transform_key, pseudo_key, expanded_tk_key):
        list_sks_str = ""; list_bfs_str = ""; list_msk_str = ""; list_rand_str = ""; key_defs_str = ""; 
        original_key_str = ""; transform_key_str = ""; pseudo_key_str = ""
        # random secret variable list
        list_rndsk_str = self.__toList(list_rnds)
        # list of msk values
        list_sks_str = self.__toList(list_sks)
        # list of msk values
        list_bfs_str = self.__toList(list_bfs)
        # list of key definitions
        key_defs_str = self.__toList(key_defs)
        # list of msk values
        list_msk_str = self.__toLaTeX(list_msk)
        # list of random values
        list_rand_str = self.__toLaTeX(list_rand)
        # original key definitions
        original_key_str = self.__toPrintStatement(original_key)
        # transform key definition
        transform_key_str = self.__toPrintStatement(transform_key)
        # pseudo key
        pseudo_key_str = self.__toPrintStatement(pseudo_key)
        # expanded tk str
        expanded_tk_key_str = self.__toPrintStatement(expanded_tk_key)
        
        result = header % (title, title, list_rndsk_str, list_sks_str, list_bfs_str, list_msk_str, list_rand_str, key_defs_str, original_key_str, transform_key_str, pseudo_key_str, expanded_tk_key_str)
        return result

    def __toLaTeX(self, _list):
        _list_str = ""
        for i in _list:
            _list_str += self.lcg.getLatexVersion(i) + ","
        _list_str = _list_str[:len(_list_str)-1]
        return _list_str
    
    def __toList(self, _list):
        _list_str = ""
        for i in _list:
            _list_str += i + ","
        _list_str = _list_str[:len(_list_str)-1]
        return _list_str
    
    def __toPrintStatement(self, _list):
        _list_str = ""
        for i in _list:
            _list_str += self.lcg.print_statement(i) + ","
        _list_str = _list_str[:len(_list_str)-1]
        return _list_str
    
    def proofBody(self, step, data):
#        pre_eq = data.get('preq')
#        step_prefix = data.get('stepPrefix')
        result_eq = data['eq']
        result = basic_step % (step, data['msg'], result_eq)
        #print('[STEP', step, ']: ', result)
        return result
    
    def proofBody2(self, step, data):
        result_eq = data['eq']
        result_eq_str = ""
        if(type(result_eq) == list):
            for i in result_eq:
                result_eq_str += i + comma
            result_eq_str = result_eq_str[:-len(comma)]
        else:
            result_eq_str = str(result_eq)
        result = basic_step2 % (str(step), data['msg'], result_eq_str)
        #print('[STEP', step, ']: ', result)
        return result

    def writeConfig(self, latex_file):
        title = string.capwords(latex_file)
        outputStr = self.proofHeader(title, self.rndList, self.skList, self.bfList, self.mskList, self.randList, self.keyDefsList, self.originalKeyList, self.transformKeyList, self.pseudoTK, self.expandedTK)
        # add list of ciphertext names
        outputStr += headerCT % self.__toLaTeX(self.ctList)
        # build the decrypt portion of proof
#        outputStr += header_decrypt
#        for i in range(self.__lcg_decrypt_count):
#            outputStr += self.proofBody(i+1, self.__lcg_decrypt_data[i])
#        outputStr += proof_footer
       # build the transform portion of proof 
        outputStr += header_transform
        for i in range(self.__lcg_transform_count):
            outputStr += self.proofBody2(str(i+1) + "a", self.__lcg_transform_data[i])
            outputStr += self.proofBody2(str(i+1) + "b", self.__lcg_buckets_pair[i])
            final_i = i
        data = {'msg': 'Return remaining elements of partially decrypted ciphertext', 'eq':self.finalPartCT}
        outputStr += self.proofBody2(final_i+1, data)
        outputStr += proof_footer
        
        outputStr += header_decout
        data = {'msg': 'Extract the following from partially decrypted ciphertext', 'eq':self.expandPartCT}
        outputStr += self.proofBody2(1, data)
        for i in range(self.__lcg_decout_count):
            outputStr += self.proofBody(i+2, self.__lcg_decout_data[i]) 
        outputStr += proof_footer
        
        return outputStr
    
    def writeProof(self, file=None):
        if file == None:
            latex_file = self.latex_file
        else:
            latex_file = file
        f = open('proof_gen' + latex_file + '.tex', 'w')
        output = self.writeConfig(latex_file)
        f.write(output)
        f.close()
        return True
