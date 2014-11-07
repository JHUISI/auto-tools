schemeType = "PKENC"
assumption = ["DBDH"]
reduction = ["reductionWATERS05IBE"]

#short = "secret-keys"
#short = "ciphertext"
#operation = "exp"
#short = "both"
#dropFirst = "secret-keys"
short = "public-keys"

setupFuncName = "setup"
keygenFuncName = "keygen"
encryptFuncName = "encrypt"
decryptFuncName = "decrypt"

masterPubVars = ["pk"]
masterSecVars = ["msk"]

keygenPubVar = "pk"
keygenSecVar = "sk"
ciphertextVar = "ct"

assumpMasterPubVars = ["assumpVar"]
assumpMasterSecVars = ["assumpKey"]

assumpSetupFuncName = "setup"
assumpFuncName = "assump"

reducSetupFuncName = "setup"
reducQueryFuncName = "queries"
reducChallengeFuncName = "challenge"

reducCiphertextVar = "ct"
reducQueriesSecVar = "d"

reducMasterPubVars = ["assumpVar", "reductionKey"]
reducMasterSecVars = ["assumpKey", "reductionParams"]

#maps assumption variables to reduction variables ie 'ct2':'C2' (assump:reduc)
reductionMap = {'g':'g', 'g1':'g1', 'g2':'g2', 'ct1':'C1', 'ct2':'C2', 'ct3':'C3', 'd1':'d1', 'd2':'d2', 'A':'A', 'B':'B', 'C':'C', 'uprime':'ut'}

