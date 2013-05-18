AutoGroup
=========

Often, pairing-based cryptographic schemes are described using symmetric groups. While these groups simplify the description of new cryptographic schemes, they are rarely the most efficient setting for implementation. Asymmetric pairings represent the state of the art in terms of efficiency and converting schemes from symmetric to an asymmetric setting currently requires manual analysis. We demonstrate with AutoGroup how to automate such conversions using SMT solvers as a core building block.  

Installation
============

To use AutoGroup, you must first install the [Charm-Crypto](https://github.com/jhuisi/charm/downloads) framework (v0.43) to execute the automatically generated batch verification algorithm in Python and/or C++.

AutoGroup also requires the [Z3](https://z3.codeplex.com/) Theorem prover (with Python 3 bindings).

Running The Tool
================

For the help menu, execute the following:

	python runAutoGroup.py --help
	AutoGroup:  sym.-to-asym. conversion for cryptographic schemes in SDL.
	
	Arguments:
	
		-s, --sdl  [ filename ]
			: input SDL file description of scheme.
	
		-c, --config [ SDL config file ]
			: configuration parameters needed for AutoGroup.
	
		-v, --verbose   [ no-argument ]
			: enable verbose output to highest level for Batcher.
	
		-o, --outfile  [ filename prefix ]
			: generate code of new scheme in C++/Python for Charm.
	
		-b, --benchmark  [ no-arguments ]
			: benchmark AutoGroup execution time.
	
		-e, --estimate [ no-arguments ]
			: estimate bandwidth for keys and ciphertext/signatures.
			

An example for how to execute AutoGroup on the CL signature scheme with basic options:

	python runAutoGroup.py -s schemes/cl04.sdl -c configCL -o TestCL 

Note that AutoGroup was designed to handle both encryption and signature schemes.

Configuration
=============

TODO : add config parameter details.
