schemeType = "PKSIG"
assumption = ["CDH"]
reduction = ["reductionBLS1", "reductionBLS5"]

#short = "assumption"
#short = "secret-keys"
#short = "ciphertext"
#operation = "exp"
#short = "both"
#dropFirst = "secret-keys"
short = "public-keys"

keygenFuncName 	= "keygen"
signFuncName 	= "sign"
verifyFuncName 	= "verify"

masterPubVars = ["pk"]
masterSecVars = ["sk"]

keygenPubVar = "pk"
keygenSecVar = "sk" 
messageVar = "M"
signatureVar = "sig" 
#functionOrder = [keygenFuncName, signFuncName, verifyFuncName]

assumpMasterPubVars = ["assumpVar"]
assumpMasterSecVars = ["assumpKey"]

assumpSetupFuncName = "setup"
assumpFuncName = "assump"

reducSetupFuncName = "setup"
reducQueryFuncName = "queries"
#reducChallengeFuncName = "challenge"

reducCiphertextVar = "sig"
reducQueriesSecVar = ""

reducMasterPubVars = ["assumpVar", "reductionKey"]
reducMasterSecVars = ["assumpKey"]

#maps assumption variables to reduction variables ie 'ct2':'C2' (assump:reduc)
reductionMap = {'g':'g', 'g1':'g1', 'g2':'g2', 'ct1':'C1', 'ct2':'C2', 'ct3':'C3', 'd1':'d1', 'd2':'d2', 'A':'A', 'B':'B', 'C':'C', 'uprime':'ut'}


