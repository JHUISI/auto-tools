schemeType = "PKSIG"
short = "public_keys"
#short = "signatures"

keygenFuncName 	= "keygen"
signFuncName 	= "sign"
verifyFuncName 	= "verify"

masterPubVars = ["gpk"]
masterSecVars = ["gmsk"]

keygenPubVar = "gpk"
keygenSecVar = "sk" 
signatureVar = "sig" 

functionOrder = [keygenFuncName, signFuncName, verifyFuncName]
