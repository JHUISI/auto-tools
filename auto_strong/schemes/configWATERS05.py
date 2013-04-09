schemeType = "PKSIG"

setupFuncName 	= "setup"
signFuncName 	= "sign"
verifyFuncName 	= "verify"

masterPubVars = ["pk"]
masterSecVars = ["sk"]

keygenPubVar = "pk"
keygenSecVar = "sk" 
messageVar = "m"
signatureVar = "sig" 
functionOrder = [setupFuncName, signFuncName, verifyFuncName]

