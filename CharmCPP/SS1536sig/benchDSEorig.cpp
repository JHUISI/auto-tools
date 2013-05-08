#include "TestDSESigorig.h"
#include <fstream>
#include <time.h>

string getID(int len)
{
	string alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
	string id = "";
	int val, alpha_len = alphabet.size();
	for(int i = 0; i < len; i++)
	{
		val = (int) (rand() % alpha_len);
		id +=  alphabet[val];
	}
	cout << "Rand selected ID: '" << id << "'" << endl;
	return id;
}

void benchmarkDSE(Waters09sig & dse, ofstream & outfile0, ofstream & outfile1, ofstream & outfile2, int ID_string_len, int iterationCount, CharmListStr & keygenResults, CharmListStr & signResults, CharmListStr & verifyResults)
{
	Benchmark benchS, benchV; // , benchK;
    CharmList pk, sk, sig;
    string M; // = getID(ID_string_len); // "somebody@example.com and other people!!!!!";
    double de_in_ms, kg_in_ms;

	dse.keygen(pk, sk);
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
//	dse.keygen(mpk, msk, id, sk);

    //cout << "ct =\n" << ct << endl;
	bool finalResult;
	for(int i = 0; i < iterationCount; i++) {
		// run enc and dec
		M = getID(ID_string_len);
		benchS.start();
	    dse.sign(pk, sk, M, sig);
		benchS.stop();
		kg_in_ms = benchS.computeTimeInMilliseconds();

		benchV.start();
		finalResult = dse.verify(pk, M, sig);
		benchV.stop();
		de_in_ms = benchV.computeTimeInMilliseconds();

		if(finalResult == false) {
	      cout << "FAILED Verification." << endl;
	      return;
	    }
	}
	cout << "Sign avg: " << benchS.getAverage() << " ms" << endl;
    stringstream s1;
	s1 << ID_string_len << " " << benchS.getAverage() << endl;
	outfile1 << s1.str();
    signResults[ID_string_len] = benchS.getRawResultString();

	cout << "Verify avg: " << benchV.getAverage() << " ms" << endl;
    stringstream s2;
	s2 << iterationCount << " " << benchV.getAverage() << endl;
	outfile2 << s2.str();
	verifyResults[ID_string_len] = benchV.getRawResultString();

    if(finalResult) {
      cout << "Successful Verification!" << endl;
    }
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
	Waters09sig dse;
	string filename = string(argv[0]);
	stringstream s2, s3, s4;
	ofstream outfile0, outfile1, outfile2;
	string f0 = filename + "_sym_keygen.dat";
	string f1 = filename + "_sym_sign.dat";
	string f2 = filename + "_sym_verify.dat";
	//outfile0.open(f0.c_str());
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());

	CharmListStr keygenResults, signResults, verifyResults;
	if(isEqual(fixOrRange, RANGE)) {
		for(int i = 2; i <= ID_string_len; i++) {
			benchmarkDSE(dse, outfile0, outfile1, outfile2, i, iterationCount, keygenResults, signResults, verifyResults);
		}
		s4 << verifyResults << endl;
	}
	else if(isEqual(fixOrRange, FIXED)) {
		benchmarkDSE(dse, outfile0, outfile1, outfile2, ID_string_len, iterationCount, keygenResults, signResults, verifyResults);
//		s2 << "Raw: " << ID_string_len << " " << keygenResults[ID_string_len] << endl;
		s3 << "Raw: " << ID_string_len << " " << signResults[ID_string_len] << endl;
		s4 << "Raw: " << ID_string_len << " " << verifyResults[ID_string_len] << endl;
	}
	else {
		cout << "invalid option." << endl;
		return -1;
	}

	// outfile0 << s2.str();
	outfile1 << s3.str();
	outfile2 << s4.str();
	//outfile0.close();
	outfile1.close();
	outfile2.close();
	return 0;
}

