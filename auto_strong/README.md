AutoStrong
===========

Most signature schemes are presented under the existential unforgeability definition wherein an adversary cannot produce a signature on a “new” message. However, strong unforgeability guarantees more -– that the adversary cannot produce a “new” signature even on a previously signed message. Strongly-unforgeable signatures are often used as a building block in signcryption and chosen-ciphertext secure encryption. 

There are several general transformations to obtain strongly unforgeable signatures from unforgeable signatures. We focus on the highly-efficient transformation due to Boneh, Shen and Waters (BSW) [1] that only applies if a signature is paritioned and a less efficient transformation due to Bellare-Shoup[2]. AutoStrong automatically applies both of these transformations but first determines whether a given signature satisfies the partitioning property. If so, it applies BSW, otherwise, the BS transform.

Installation
============

AutoStrong requires the following external tools: [Mathematica 9](http://www.wolfram.com/) and [Z3](https://z3.codeplex.com/) Theorem Prover.

Z3 Install 
===========
(Python 3 bindings available in unstable branch)
* Clone repository: `git clone https://git01.codeplex.com/z3` 

* Install instructions:

    `python scripts/mk_make.py --prefix=/home/leo`

    `cd build; make; make install`

Running The Tool
================

For the help menu, execute the following:

	python runAutoStrong.py --help
	AutoStrong:  convert an unforgeable signature to a strongly unforgeable signature in SDL.
	
	Arguments:
	
		-s, --sdl  [ filename ]
			: input SDL file description of scheme.
	
		-c, --config [ SDL config file ]
			: configuration parameters needed for AutoStrong.
	
		-v, --verbose   [ no-argument ]
			: enable verbose mode.
	
		-o, --outfile  [ filename prefix ]
			: generate code of new scheme in C++/Python for Charm.
	
		-b, --benchmark  [ no-arguments ]
			: benchmark AutoStrong execution time.
	
		-t, --skip-transform [ no-arguments ]
			: skip the application of the BSW or BS transform
	
		--path [ path/to/dir/ ]
			: destination for AutoStrong output files. Default: current dir.

Configuration
=============

TODO: add config option details

References
==========

[1]. Dan Boneh, Emily Shen, and Brent Waters. Strongly unforgeable signatures based on computational Diffie-Hellman. In PKC, pages 229–240, 2006.

[2]. Mihir Bellare and Sarah Shoup. Two-tier signatures, strongly unforgeable signatures, and fiat-shamir without random oracles. In PKC, pages 201–216, 2007.

