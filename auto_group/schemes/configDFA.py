schemeType = "PKENC"
#short = "secret_keys"
short = "ciphertext"
secparam = "BN256"

setupFuncName = "setup"
keygenFuncName = "keygen"
encryptFuncName = "encrypt"
decryptFuncName = "decrypt"

masterPubVars = ["mpk"]
masterSecVars = ["msk"]

keygenPubVar = "mpk"
keygenSecVar = "sk"
ciphertextVar = "ct"
