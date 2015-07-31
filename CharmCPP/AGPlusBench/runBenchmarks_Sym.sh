echo -e "\nBB04 Sym\n"
./TestBB04Sym 100 10 fixed

echo -e "\nBB04 Asym PK\n"
./TestBB04IBE_pk_test 100 10 fixed

echo -e "\nBB04 Asym SK\n"
./TestBB04IBE_sk_test 100 10 fixed

echo -e "\nBB04 Asym CT\n"
./TestBB04IBE_ct_test 100 10 fixed

echo -e "\nBB04 Asym Assumption\n"
./TestBB04IBE_assump_test 100 10 fixed

echo -e "\nACDKNO Sym\n"
./TestACDKNOSym 100 10 fixed

echo -e "\nACDKNO Asym PK\n"
./TestACDKNO_pk_test 100 10 fixed

echo -e "\nACDKNO Asym Sig\n"
./TestACDKNO_sig_test 100 10 fixed

echo -e "\nACDKNO Asym Assumption\n"
./TestACDKNO_assump_test 100 10 fixed

