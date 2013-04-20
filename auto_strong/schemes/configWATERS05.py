schemeType = "PKSIG"

keygenFuncName 	= "keygen"
signFuncName 	= "sign"
verifyFuncName 	= "verify"

masterPubVars = ["pk"]
masterSecVars = ["sk"]

keygenPubVar = "pk"
keygenSecVar = "sk" 
messageVar = "M"
signatureVar = "sig" 
functionOrder = [keygenFuncName, signFuncName, verifyFuncName]

