AutoBatch
=========

As devices everywhere increasingly communicate with each other, many security applications will require low-bandwidth signatures that can be processed quickly. Pairing-based signatures can be very short, but are often costly to verify. Fortunately, they also tend to have efficient batch verification algorithms. Finding these batching algorithms by hand, however, can be tedious and error prone.

We address this by presenting AutoBatch, an automated tool for generating batch verification code in either Python or C++ from a high level representation of a signature scheme. AutoBatch outputs both software and, for transparency, a LaTeX file describing the batching algorithm and arguing that it preserves the unforgeability of the original scheme.

We tested AutoBatch on over a dozen pairing-based schemes to demonstrate that a computer could find competitive batching solutions in a reasonable amount of time. Indeed, it proved highly competitive. In particular, it found an algorithm that is significantly faster than a batching algorithm from Eurocrypt 2010. Another novel contribution is that it handles cross-scheme batching, where it searches for a common algebraic structure between two distinct schemes and attempts to batch them together.

AutoBatch is a useful tool for cryptographic designers and implementors, and to our knowledge, it is the first attempt to outsource to machines the design, proof writing and implementation of signature batch verification schemes.

Full Version of ACM CCS 2012 publication: http://eprint.iacr.org/2013/175

Installation
============

The [Charm-Crypto](https://github.com/jhuisi/charm/downloads) framework (v0.42 or newer) is required to execute the automatically generated batch verification algorithm in Python and/or C++. IMPORTANT: make sure you install the [Stanford PBC library](http://crypto.stanford.edu/pbc/download.html) and also install Python 3 or greater.

To install the Python 3 bindings for Z3:

    git clone git@github.com:Z3Prover/z3.git -b unstable
    python3 scripts/mk_make.py
    cd build
    make


Running The Tool
================

For the help menu, execute the following:

	python runAutoBatch.py --help
	Batcher, 1.0 
	
	Arguments: 
	
		-f, --sdl  [ filename ]
			: input SDL file description of signature scheme.
	
		-o, --outfile  [ filename ]
			: output file for SDL batch verifier.
	
		-p, --proof [ no-argument ]
			: generate proof of security for batch verification algorithm
	
		-v, --verbose   [ no-argument ]
			: enable verbose output to highest level for Batcher.
	
		-t, --threshold [ no-argument ]
			: measure the "cross-over" point between batch and individual verification from 0 to N.
	
		-d, --precompute [ no-argument ]
			: determine if there are additional variables that can be precomputed in verification equation
	
		-c, --partial-codegen  [ no-argument ]
			: output internal format for partial SDL required codegen (backwards compatibility).
	
		-s, --strategy [ no-argument ]
			: select a technique search strategy for Batcher. Pruned-BFS is only search supported.
	
		-l, --library [ miracl or relic ]
			: underlying crypto library being used.
	
		-q, --query [ no-argument ]
			: takes a test statement for debugging SDL parser
	
		--path [ path/to/dir/ ]
			: destination for AutoBatch output files. Default: current dir.

An example for how to execute AutoBatch on the BLS signature scheme with some standard options:

	python runAutoBatch.py --sdl schemes/BLS/bls.sdl --outfile schemes/BLS/bls-full-batch.sdl --path schemes/BLS/ --proof -v


Disclaimer
==========

AutoBatch is a proof-of-concept tool for assisting cryptographers in automatically designing batch verification algorithms. Although AutoBatch is [Free Software](http://www.gnu.org/philosophy/free-sw.html), released under GNU GPL version 3, keep in mind that it is extensively research-quality software. It has only been thoroughly tested on test cases discussed in our CCS paper and on other internally generated test cases. AutoBatch is still considered research-grade software, but we are constantly improving it to be as robust as possible. 

For bug reports, comments/questions and other inquires, email us at akinyelj [AT] cs.jhu.edu OR mpagano [ AT ] cs.jhu.edu.
