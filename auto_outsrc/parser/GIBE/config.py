schemeType = "PKENC"
short = "secret_keys"
#short = "ciphertext"
#short = "both"
#operation = "exp"

setupFuncName = "setup"
keygenFuncName = "keygen"
encryptFuncName = "encrypt"
decryptFuncName = "decrypt"

masterPubVars = ["pk"]
masterSecVars = ["mk"]

keygenPubVar = "pk"
keygenSecVar = "sk"
ciphertextVar = "ct"

rootNodeName = 'root'
addNodePrefix = 'ADD'
mulNodePrefix = 'MUL'
leafNodeName = 'LEAF0'
listNodeName = 'LIST0'
