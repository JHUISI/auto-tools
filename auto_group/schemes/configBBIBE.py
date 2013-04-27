schemeType = "PKENC"
#short = "secret_keys"
#short = "ciphertext"
short = "both"

setupFuncName = "setup"
keygenFuncName = "keygen"
encryptFuncName = "encrypt"
decryptFuncName = "decrypt"

masterPubVars = ["pk"]
masterSecVars = ["msk"]

keygenPubVar = "pk"
keygenSecVar = "sk"
ciphertextVar = "ct"
