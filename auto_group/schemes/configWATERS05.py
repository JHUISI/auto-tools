schemeType = "PKSIG"
#short = "public-keys"
short = "signature" 
#operation = "exp"

keygenFuncName 	= "keygen"
signFuncName 	= "sign"
verifyFuncName 	= "verify"

masterPubVars = ["pk"]
masterSecVars = ["sk"]

keygenPubVar = "pk"
keygenSecVar = "sk" 
signatureVar = "sig" 
functionOrder = [keygenFuncName, signFuncName, verifyFuncName]
