#include "TestACDKNO_pk_test.h"
#include <fstream>
#include <time.h>

void benchmarkACDK(Acdk12 & acdk, ofstream & outfile0, ofstream & outfile1, ofstream & outfile2, ofstream & outfile3, int ID_string_len, int iterationCount, CharmListStr & setupResults, CharmListStr & keygenResults, CharmListStr & signResults, CharmListStr & verifyResults)
{
	Benchmark benchSU, benchK, benchS, benchV; // , benchK;
	CharmList gk, vk, sk, M, sig;
    ZR m1, m2;
    double su_in_ms, kg_in_ms, s_in_ms, v_in_ms;

    benchSU.start();
	acdk.setup(gk);
    benchSU.stop();
	su_in_ms = benchSU.computeTimeInMilliseconds();

    benchK.start();
	acdk.keygen(gk, vk, sk);
    benchK.stop();
    kg_in_ms = benchK.computeTimeInMilliseconds();

	cout << "Setup avg: " << benchSU.getAverage() << " ms" << endl;
    stringstream sSU;
	sSU << ID_string_len << " " << benchSU.getAverage() << endl;
	outfile3 << sSU.str();
    setupResults[ID_string_len] = benchSU.getRawResultString();

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
//	acdk.keygen(mpk, msk, id, sk);

    //cout << "ct =\n" << ct << endl;
	bool finalResult;
	for(int i = 0; i < iterationCount; i++) {
		// run enc and dec
		m1 = acdk.group.random(ZR_t);
		m2 = acdk.group.random(ZR_t);
		benchS.start();
	    acdk.sign(gk, vk, sk, m1, m2, M, sig);
		benchS.stop();
		s_in_ms = benchS.computeTimeInMilliseconds();

		benchV.start();
		finalResult = acdk.verify(gk, vk, M, sig);
		benchV.stop();
		v_in_ms = benchV.computeTimeInMilliseconds();

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
	Acdk12 acdk;
	string filename = string(argv[0]);
	stringstream s2, s3, s4;
	ofstream outfile0, outfile1, outfile2, outfile3;
	string f0 = filename + "_asym_keygen.dat";
	string f1 = filename + "_asym_encrypt.dat";
	string f2 = filename + "_asym_decrypt.dat";
	string f3 = filename + "_asym_setup.dat";
	//outfile0.open(f0.c_str());
	outfile0.open(f0.c_str());
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());
    outfile3.open(f3.c_str());

	CharmListStr setupResults, keygenResults, signResults, verifyResults;
	if(isEqual(fixOrRange, RANGE)) {
		for(int i = 2; i <= ID_string_len; i++) {
			benchmarkACDK(acdk, outfile0, outfile1, outfile2, outfile3, i, iterationCount, setupResults, keygenResults, signResults, verifyResults);
		}
		s4 << verifyResults << endl;
	}
	else if(isEqual(fixOrRange, FIXED)) {
		benchmarkACDK(acdk, outfile0, outfile1, outfile2, outfile3, ID_string_len, iterationCount, setupResults, keygenResults, signResults, verifyResults);
		s2 << "Raw: " << ID_string_len << " " << keygenResults[ID_string_len] << endl;
		s3 << "Raw: " << ID_string_len << " " << signResults[ID_string_len] << endl;
		s4 << "Raw: " << ID_string_len << " " << verifyResults[ID_string_len] << endl;
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
}

