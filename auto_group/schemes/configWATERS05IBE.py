schemeType = "PKENC"
assumption = "DBDH"
reduction = "reductionWATERS05IBE"

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

assumpSetupFuncName = "assumpsetup"
assumpFuncName = "assump"

reducSetupFuncName = "setup"
reducQueryFuncName = "queries"
reducChallengeFuncName = "challenge"

reducCiphertextVar = "ct"
reducQueriesSecVar = "d"

reducMasterPubVars = ["assumpVar", "reductionKey"]
reducMasterSecVars = ["assumpKey", "reductionParams"]

