schemeType = "PKSIG"

keygenFuncName = "keygen"
signFuncName = "sign"
verifyFuncName = "verify"

masterPubVars = ["mpk"]
masterSecVars = ["msk"]

keygenPubVar = "pk"
keygenSecVar  = "sk"
messageVar = "m"
signatureVar = "sig"

functionOrder = [keygenFuncName, signFuncName, verifyFuncName]
