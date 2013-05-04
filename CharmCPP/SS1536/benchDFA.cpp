
#include "TestDFA.h"

string getRandomHexString(int len)
{
	string hex = "0x";
	if(len == 2) return hex;
	else if(len > 2) {
		string alpha = "ABCDEFabcdef0123456789";
		int val, alpha_len = alpha.size();
		for(int i = 0; i < len-2; i++)
		{
			val = (int) (rand() % alpha_len);
			hex +=  alpha[val];
		}
		cout << "Hex Value: '" << hex << "'" << endl;
	}
	else {
		cout << "getRandomHexString: invalid len => " << len << endl;
		return "";
	}
	return hex;

}

void benchmarkDFA(Dfa12 & dfa12, ofstream & outfile0, ofstream & outfile1, ofstream & outfile2, int wStringCount, int iterationCount, int increment, CharmListStr & keygenResults, CharmListStr & encryptResults, CharmListStr & decryptResults)
{
	Benchmark benchT, benchD, benchK;
	string letters = "xABCDEFabcdef0123456789";
	dfa12.dfaUtil.constructDFA("0x(0|1|2|3|4|5|6|7|8|9|a|b|c|d|e|f|A|B|C|D|E|F)*", letters);
	CharmList mpk, sk, sk2, ct;
	CharmListStr alphabet = dfa12.dfaUtil.getAlphabet();
	CharmListStr w;
	CharmListInt Q = dfa12.dfaUtil.getStates(), F = dfa12.dfaUtil.getAcceptStates(); // get all states, and all accept states
	CharmMetaListInt T = dfa12.dfaUtil.getTransitions(); // get all transitions in DFA
	ZR bf0;
	G1 msk;
	GT M, newM, Cm;
	double kg_in_ms;

	//cout << "Q:\n" << Q << endl;
	//cout << "F:\n" << F << endl;
	//cout << "T:\n" << T << endl;

	dfa12.setup(alphabet, mpk, msk);
	for(int j = 0; j < iterationCount; j ++) {
		benchK.start();
		dfa12.keygen(mpk, msk, Q, T, F, sk2);
		benchK.stop();
		kg_in_ms = benchK.computeTimeInMilliseconds();
	}
	cout << "Keygen avg: " << benchK.getAverage() << " ms" << endl;
	stringstream s0;
	s0 << wStringCount << " " << benchK.getAverage() << endl;
	outfile0 << s0.str();
	keygenResults[wStringCount] = benchK.getRawResultString();

	dfa12.keygen(mpk, msk, Q, T, F, sk);

	//cout << "MPK:\n" << mpk << endl;
	//cout << "MSK:\n" << convert_str(msk) << endl;

    //dfa12.keygen(mpk, msk, Q, T, F, sk);

	//cout << "SK:\n" << skBlinded << endl;

	double de_in_ms;

	for(int i = 0; i < iterationCount; i ++) {
		w = dfa12.dfaUtil.getSymbols(getRandomHexString(wStringCount)); // "aba"
		M = dfa12.group.random(GT_t);
		benchT.start();
		dfa12.encrypt(mpk, w, M, ct);
		benchT.stop();
		kg_in_ms = benchT.computeTimeInMilliseconds();

		if(dfa12.dfaUtil.accept(w)) {
			cout << "isAccept: true" << endl;
			CharmMetaListInt Ti = dfa12.dfaUtil.getTransitions(w); // 1
			cout << "State transitions to decrypt: " << Ti.length() << endl;
			int x = dfa12.dfaUtil.getAcceptState(Ti); // 2

			benchD.start();
			dfa12.decrypt(sk, ct, newM, Ti, x);
			benchD.stop();
			de_in_ms = benchD.computeTimeInMilliseconds();
		}
	}
	cout << "Encrypt avg: " << benchT.getAverage() << " ms" << endl;
	stringstream s1;
	s1 << wStringCount << " " << benchT.getAverage() << endl;
	outfile1 << s1.str();
	encryptResults[wStringCount] = benchT.getRawResultString();

	cout << "Decrypt avg: " << benchD.getAverage() << " ms" << endl;
	stringstream s2;
	s2 << wStringCount << " " << benchD.getAverage() << endl;
	outfile2 << s2.str();
	decryptResults[wStringCount] = benchD.getRawResultString();
//		cout << convert_str(M) << endl;
//		cout << convert_str(newM) << endl;
	if(M == newM) {
	  cout << "Successful Decryption!" << endl << endl;
	}
	else {
	  cout << "FAILED Decryption." << endl << endl;
	}

    return;
}

int main(int argc, const char *argv[])
{
	string FIXED = "fixed", RANGE = "range";
	if(argc != 5) { cout << "Usage " << argv[0] << ": [ iterationCount => 10 ] [ wStringCount => 1000 ] [ incrementCount => 25 ] [ 'fixed' or 'range' ]" << endl; return -1; }

	int iterationCount = atoi( argv[1] );
	int wStringCount = atoi( argv[2] );
	int incrementCount = atoi( argv[3] );
	string fixOrRange = string( argv[4] );
	cout << "iterationCount: " << iterationCount << endl;
	cout << "wStringCount: " << wStringCount << endl;
	cout << "incrementCount: " << incrementCount << endl;
	cout << "measurement: " << fixOrRange << endl;

	Dfa12 dfa12;
	string filename = string(argv[0]);
	ofstream outfile0, outfile1, outfile2;
	string f0 = filename + "_sym_keygen.dat";
	string f1 = filename + "_sym_encrypt.dat";
	string f2 = filename + "_sym_decrypt.dat";
	outfile0.open(f0.c_str());
	outfile1.open(f1.c_str());
	outfile2.open(f2.c_str());

	CharmListStr keygenResults, encryptResults, decryptResults;
	if(isEqual(fixOrRange, RANGE)) {
		for(int i = 2; i <= wStringCount; i += incrementCount) {
			cout << "Benchmark with " << i << " wStringCount." << endl;
			benchmarkDFA(dfa12, outfile0, outfile1, outfile2, i, iterationCount, incrementCount, keygenResults, encryptResults, decryptResults);
			stringstream s4;
			s4 << i << " " << decryptResults[i] << endl;
			outfile2 << s4.str();
			outfile2.flush();
		}
	}
	else if(isEqual(fixOrRange, FIXED)) {
		cout << "Benchmark with " << wStringCount << " wStringCount." << endl;
		benchmarkDFA(dfa12, outfile0, outfile1, outfile2, wStringCount, iterationCount, incrementCount, keygenResults, encryptResults, decryptResults);
		stringstream s2, s3, s4;
		s2 << wStringCount << " " << keygenResults[wStringCount] << endl;
		outfile0 << s2.str();
		outfile0.flush();
		s3 << wStringCount << " " << encryptResults[wStringCount] << endl;
		outfile1 << s3.str();
		outfile1.flush();
		s4 << wStringCount << " " << decryptResults[wStringCount] << endl;
		outfile2 << s4.str();
		outfile2.flush();
	}
	else {
		cout << "invalid option." << endl;
		return -1;
	}
	outfile0.close();
	outfile1.close();
	outfile2.close();
//	cout << "<=== Transform benchmarkWATERS breakdown ===>" << endl;
//	cout << transformResults << endl;
//	cout << "<=== Transform benchmarkWATERS breakdown ===>" << endl;
//	cout << "<=== decrypt benchmarkWATERS breakdown ===>" << endl;
//	cout << decryptResults << endl;
//	cout << "<=== decrypt benchmarkWATERS breakdown ===>" << endl;

	return 0;
}

//	Dfa12 dfa12;
//	dfa12.dfaUtil.constructDFA("ab*a", "ab");
//	CharmListStr w = dfa12.dfaUtil.getSymbols("aba");
//	CharmMetaListInt Ti = dfa12.dfaUtil.getTransitions(w); // 1
//	int x = dfa12.dfaUtil.getAcceptState(Ti); // 2

//	dfa12.dfaUtil.constructDFA("(0|1|2|3|4|5|6|7|8|9)*-(a|b|c)*-(0|1|2|3|4|5|6|7|8|9)*", "abc0123456789-"); // "abcdefghijklmnopqrstuvwxyz0123456789"
