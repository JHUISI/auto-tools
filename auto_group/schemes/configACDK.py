schemeType = "PKSIG"
#short = "public_keys"
#short = "signature"
short = "both"
operation = "exp"

setupFuncName 	= "setup"
keygenFuncName 	= "keygen"
signFuncName 	= "sign"
verifyFuncName 	= "verify"

masterPubVars = ["gk"]
masterSecVars = ["sk"]

keygenPubVar = "vk"
keygenSecVar = "sk" 
signatureVar = "sig" 

