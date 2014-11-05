schemeType = "PKENC"
#assumes assumption/reduction are in matching order
assumption = ["DBDH", "DLIN"]
#assumption = ["DBDH"]
reduction = ["reductionWATERS09DBDH", "reductionWATERS09DLIN", "reductionWATERS09DLIN2"]
#reduction = ["reductionWATERS09DBDH"]

schemeType = "PKENC"
#short = "secret-keys"
short = "public-keys"
#short = "ciphertext"
#short = "both"
#operation = "exp"

setupFuncName = "setup"
keygenFuncName = "keygen"
encryptFuncName = "encrypt"
decryptFuncName = "decrypt"

masterPubVars = ["mpk"]
masterSecVars = ["msk"]

keygenPubVar = "mpk"
keygenSecVar  = "sk"
ciphertextVar = "ct"

assumpMasterPubVars = ["assumpVar"]
assumpMasterSecVars = ["assumpKey"]

assumpSetupFuncName = "setup"
assumpFuncName = "assump"

reducSetupFuncName = "setup"
reducQueryFuncName = "queries"
reducChallengeFuncName = "challenge"

reducCiphertextVar = "ct"
reducQueriesSecVar = "reducsk"

reducMasterPubVars = ["assumpVar", "reducpk"]
reducMasterSecVars = ["reducmsk", "reducVar"]

#maps assumption variables to reduction variables ie 'ct2':'C2' (assump:reduc)
reductionMap = {'g':'g', 'f':'f', 'nu':'nu', 'c1':'c1', 'r':'r', 'G':'G', 'F':'F', 'T':'T', 'A':'A', 'B':'B', 'C':'C'}

