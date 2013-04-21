import hashlib, sys

from charm.toolbox.pairinggroup import *

from charm.toolbox.secretutil import SecretUtil
from charm.core.math import pairing
from charm.toolbox.iterate import dotprod2
from charm.core.math.pairing import hashPair as DeriveKey
from charm.core.engine.util import objectToBytes, bytesToObject
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.toolbox.conversion import Conversion
from charm.toolbox.bitstring import Bytes

groupObj = None
utilObj = None

listIndexNoOfN_StrToId = 9
listIndexNoOfl_StrToId = 10

def stringToInt(strID, zz, ll):
    checkUserGlobals()

    '''Hash the identity string and break it up in to l bit pieces'''
    h = hashlib.new('sha1')
    h.update(bytes(strID, 'utf-8'))
    _hash = Bytes(h.digest())
    val = Conversion.OS2IP(_hash) #Convert to integer format
    bstr = bin(val)[2:]   #cut out the 0b header

    v=[]
    for i in range(zz):  #z must be greater than or equal to 1
        binsubstr = bstr[ll*i : ll*(i+1)]
        intval = int(binsubstr, 2)
        intelement = groupObj.init(ZR, intval)
        v.append(intelement)
    return v

def intToBits(x, bitLen):
    """Converts an integer into a binary number and returns it as a list of ZR types of size length"""
    s = bin(int(x))[2:]
    if len(s) >= bitLen: 
        s = s[:bitLen] # cut anything above
        return [ groupObj.init(ZR, int(i)) for i in s ]
    else:
        # need to pad this many 0's
        extraZeros = bitLen - len(s)
        return [ groupObj.init(ZR, 0) for i in range(extraZeros)] + [ groupObj.init(ZR, int(i)) for i in s ]

def isList(object):
    objectTypeName = None

    try:
        objectTypeName = type(object).__name__
    except:
        assert False, "builtInFuncs.py:  could not obtain type/name of object passed in to isList."

    if (objectTypeName == 'list'):
        return 1

    return 0

def objectOut(group, d):
	checkUserGlobals()
	s = ""
	keys = d.keys()
	for i in keys:
		if type(d[i]) == pairing:
			s += str(i) + "=" + group.serialize(d[i]).decode() + "\n"
		else:
			s += str(i) + "=" + d[i].decode()
	return s

def writeToFile(name, s):
	checkUserGlobals()
	fd = open(name, 'w')
	fd.write(s)
	fd.close()

def GetString(GetString_Arg):
    checkUserGlobals()
    return GetString_Arg.getAttribute()

def createPolicy(policy_str):
	checkUserGlobals()
	return utilObj.createPolicy(policy_str)

def getAttributeList(policy):
	checkUserGlobals()
	return utilObj.getAttributeList(policy)

def calculateSharesDict(s, policy):
	checkUserGlobals()
	return utilObj.calculateSharesDict(s, policy)

def calculateSharesList(s, policy):
	checkUserGlobals()
	return utilObj.calculateSharesList(s, policy)

def prune(policy, S):
	checkUserGlobals()
	return utilObj.prune(policy, S)

def getCoefficients(policy):
	checkUserGlobals()
	return utilObj.getCoefficients(policy)

def sha1(message):
	checkUserGlobals()
	hashObj = hashlib.new('sha1') 
	h = hashObj.copy()
	h.update(bytes(message, 'utf-8'))
	return Bytes(h.digest())

def checkUserGlobals():
    global groupObj, utilObj
    
    if (groupObj == None):
        assert False, "groupObj (PairingGroup class) not defined in builtInFuncs.py"

    if (utilObj == None):
        #assert False, "utilObj (SecretUtil class) not defined in builtInFuncs.py"
        pass
    return
