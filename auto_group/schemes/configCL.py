schemeType = "PKSIG"
assumption = ["LRSW"]
reduction = ["reductionCL"]

#short = "public-keys"
short = "signature"
#short = "both"
#operation = "exp"

setupFuncName 	= "setup"
keygenFuncName 	= "keygen"
signFuncName 	= "sign"
verifyFuncName 	= "verify"

masterPubVars = None
masterSecVars = None

keygenPubVar = "pk"
keygenSecVar = "sk" 
signatureVar = "sig" 

assumpMasterPubVars = ["assumpVar"]
assumpMasterSecVars = ["assumpKey"]

assumpSetupFuncName = "setup"
assumpFuncName = "assump"

reducSetupFuncName = "setup"
reducQueryFuncName = "queries"
reducChallengeFuncName = ""

reducCiphertextVar = ""
reducQueriesSecVar = "sig"

reducMasterPubVars = ["assumpVar", "reductionKey"]
reducMasterSecVars = ["assumpKey", "reductionParams"]

#maps assumption variables to reduction variables ie 'ct2':'C2' (assump:reduc)
reductionMap = {'g':'g', 'x':'x', 'y':'y', 'X':'X', 'Y':'Y', 'a':'a', 'b':'b', 'c':'c'}

graphit = True
