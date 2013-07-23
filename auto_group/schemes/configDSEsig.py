schemeType = "PKSIG"
#short = "public-keys"
#short = "signature"
short = "both"
#operation = "exp"

keygenFuncName = "keygen"
signFuncName = "sign"
verifyFuncName = "verify"

masterPubVars = ["mpk"]
masterSecVars = ["msk"]

keygenPubVar = "pk"
keygenSecVar  = "sk"
signatureVar = "sig"

functionOrder = [keygenFuncName, signFuncName, verifyFuncName]
