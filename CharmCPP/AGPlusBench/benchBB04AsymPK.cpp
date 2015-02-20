#include "TestBB04IBE_pk_test.h"

#include <fstream>
#include <time.h>

void benchmarkBB(Bb04ibe & bb, ofstream & outfile0, ofstream & outfile1, ofstream & outfile2, ofstream & outfile3, int ID_string_len, int iterationCount, CharmListStr & setupResults, CharmListStr & keygenResults, CharmListStr & encryptResults, CharmListStr & decryptResults)
{
	Benchmark benchS, benchK, benchE, benchD; // , benchK;
    CharmList pk, msk, sk, ct;
    GT M;
    double s_in_ms, kg_in_ms, de_in_ms, en_in_ms;
    CharmListZR ID;
    ID.insert(0, bb.group.random(ZR_t));
    ID.insert(1, bb.group.random(ZR_t));


    benchS.start();
	bb.setup(msk, pk);
    benchS.stop();
	s_in_ms = benchS.computeTimeInMilliseconds();

    benchK.start();
	bb.keygen(2, pk, msk, ID, sk);
    benchK.stop();
    kg_in_ms = benchK.computeTimeInMilliseconds();

	cout << "Setup avg: " << benchS.getAverage() << " ms" << endl;
    stringstream sS;
	sS << ID_string_len << " " << benchS.getAverage() << endl;
	outfile3 << sS.str();
    setupResults[ID_string_len] = benchS.getRawResultString();

	cout << "Keygen avg: " << benchK.getAverage() << " ms" << endl;
    stringstream sK;
	sK << iterationCount << " " << benchK.getAverage() << endl;
	outfile0 << sK.str();
	keygenResults[ID_string_len] = benchK.getRawResultString();


//	for(int i = 0; i < iterationCount; i++) {
//		id = getID(ID_string_len);
//		benchK.start();
//		benchK.stop();
//		kg_in_ms = benchK.computeTimeInMilliseconds();
//	}
//	cout << "Keygen avg: " << benchK.getAverage() << " ms" << endl;
//    stringstream s0;
//	s0 << ID_string_len << " " << benchK.getAverage() << endl;
//	outfile0 << s0.str();
//    keygenResults[ID_string_len] = benchK.getRawResultString();
//
//	bb.keygen(mpk, msk, id, sk);

    //cout << "ct =\n" << ct << endl;
	bool finalResult;
	for(int i = 0; i < iterationCount; i++) {
		// run enc and dec
		M = bb.group.random(GT_t);
		benchE.start();
	    bb.encrypt(2, pk, M, ID, ct);
		benchE.stop();
		en_in_ms = benchE.computeTimeInMilliseconds();

		benchD.start();
		bb.decrypt(pk, sk, ct, M);
		benchD.stop();
		de_in_ms = benchD.computeTimeInMilliseconds();

		//if(finalResult == false) {
	    //  cout << "FAILED Verification." << endl;
	    //  return;
	    //}
	}
	cout << "Encrypt avg: " << benchE.getAverage() << " ms" << endl;
    stringstream s1;
	s1 << ID_string_len << " " << benchE.getAverage() << endl;
	outfile1 << s1.str();
    encryptResults[ID_string_len] = benchE.getRawResultString();

	cout << "Decrypt avg: " << benchD.getAverage() << " ms" << endl;
    stringstream s2;
	s2 << iterationCount << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decryptResults[ID_string_len] = benchD.getRawResultString();

    //if(finalResult) {
    //  cout << "Successful Verification!" << endl;
    //}
    return;
}

int main(int argc, const char *argv[])
{
	string FIXED = "fixed", RANGE = "range";
	if(argc != 4) { cout << "Usage " << argv[0] << ": [ iterationCount => 10 ] [ ID-string => 100 ] [ 'fixed' or 'range' ]" << endl; return -1; }

	int iterationCount = atoi( argv[1] );
	int ID_string_len = atoi( argv[2] );
	string fixOrRange = string(argv[3]);
	cout << "iterationCount: " << iterationCount << endl;
	cout << "ID-string: " << ID_string_len << endl;
	cout << "measurement: " << fixOrRange << endl;

	srand(time(NULL));
	Bb04ibe bb;
	string filename = string(argv[0]);
	stringstream s2, s3, s4;
	ofstream outfile0, outfile1, outfile2, outfile3;
	string f0 = filename + "_asym_keygen.dat";
	string f1 = filename + "_asym_encrypt.dat";
	string f2 = filename + "_asym_decrypt.dat";
	string f3 = filename + "_asym_setup.dat";
	outfile0.open(f0.c_str());
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());
    outfile3.open(f3.c_str());

	CharmListStr setupResults, keygenResults, encryptResults, decryptResults;
	if(isEqual(fixOrRange, RANGE)) {
		for(int i = 2; i <= ID_string_len; i++) {
			benchmarkBB(bb, outfile0, outfile1, outfile2, outfile3, i, iterationCount, setupResults, keygenResults, encryptResults, decryptResults);
		}
	}
	else if(isEqual(fixOrRange, FIXED)) {
		benchmarkBB(bb, outfile0, outfile1, outfile2, outfile3, ID_string_len, iterationCount, setupResults, keygenResults, encryptResults, decryptResults);
		s2 << "Raw: " << ID_string_len << " " << keygenResults[ID_string_len] << endl;
		s3 << "Raw: " << ID_string_len << " " << encryptResults[ID_string_len] << endl;
		s4 << "Raw: " << ID_string_len << " " << decryptResults[ID_string_len] << endl;
	}
	else {
		cout << "invalid option." << endl;
		return -1;
	}

	outfile0 << s2.str();
	outfile1 << s3.str();
	outfile2 << s4.str();
	outfile0.close();
	outfile1.close();
	outfile2.close();
    outfile3.close();
	return 0;
}

