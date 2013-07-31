AutoGroup
=========

Often, pairing-based cryptographic schemes are described using symmetric groups. While these groups simplify the description of new cryptographic schemes, they are rarely the most efficient setting for implementation. Asymmetric groups represent the state-of-the-art in terms of efficiency and converting schemes from symmetric to an asymmetric solution currently requires manual analysis. We demonstrate with AutoGroup how to automate such conversions using SMT solvers as a core building block.  

Installation
============

To use AutoGroup, you must first install the [Charm-Crypto](https://github.com/jhuisi/charm/downloads) framework (v0.43) to execute the automatically generated the asymmetric scheme in Python and/or C++.

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
			

An example for how to execute AutoGroup on the Camenisch-Lysyanskaya (CL) signature scheme with basic options:

	python runAutoGroup.py --sdl schemes/cl04.sdl --config configCL -o TestCL -v

Note that AutoGroup was designed to handle both encryption and signature schemes.

Configuration
=============

AutoGroup provides several configuration parameters to tune conversion to an asymmetric solution. The configuration file is specified in Python with the following options:

``schemeType`` : for describing the type of input scheme. For public-key encryption, ``"PKENC"`` and for signature types, ``"PKSIG"``.

``short`` : to find a solution that shortens the representation of the ``"ciphertext"``, ``"secret-keys"`` or ``"both"`` for encryption. For signature schemes, ``"signatures"`` or ``"public-keys"`` or ``"both"``

``operation`` : to find a solution that reduces the computation time based on ``exp``(exponentiation) or ``mul``(multiplication). 




