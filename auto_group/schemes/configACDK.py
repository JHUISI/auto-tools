schemeType = "PKSIG"
assumption = ["DLIN-ACDKNO", "CDH-ACDKNO"]
reduction = ["reductionACDK12Lemma6", "reductionACDK12Lemma7", "reductionACDK12Lemma8"]

short = "public-keys"
#short = "signature"
#short = "assumption"
#short = "both"
#operation = "exp"

setupFuncName 	= "setup"
keygenFuncName 	= "keygen"
signFuncName 	= "sign"
verifyFuncName 	= "verify"

masterPubVars = ["gk"]
masterSecVars = ["sk"]

keygenPubVar = "vk"
keygenSecVar = "sk" 
signatureVar = "sig" 

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

assumption_reduction_map = { "reductionACDK12Lemma6" : "DLIN-ACDKNO", "reductionACDK12Lemma7" : "DLIN-ACDKNO", "reductionACDK12Lemma8" : "CDH-ACDKNO" }

