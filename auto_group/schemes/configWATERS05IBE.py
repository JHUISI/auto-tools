schemeType = "PKENC"
assumption = "DBDH"

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
