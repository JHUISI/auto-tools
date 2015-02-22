schemeType = "PKSIG"
assumption = ["DBDH"]
reduction = ["reductionWATERS05SIG"]

#short = "assumption"
#short = "secret-keys"
short = "signature"
#operation = "exp"
#short = "both"
#dropFirst = "secret-keys"
#short = "public-keys"

keygenFuncName 	= "keygen"
signFuncName 	= "sign"
verifyFuncName 	= "verify"

masterPubVars = ["pk"]
masterSecVars = ["sk"]

keygenPubVar = "pk"
keygenSecVar = "sk" 
signatureVar = "sig" 
functionOrder = [keygenFuncName, signFuncName, verifyFuncName]

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
reductionMap = {'g':'g', 'g1':'g1', 'g2':'g2', 'ct1':'C1', 'ct2':'C2', 'ct3':'C3', 'd1':'d1', 'd2':'d2', 'A':'A', 'B':'B', 'C':'C', 'uprime':'ut'}

# TODO: get this WORKING!!!
#graphit = True
