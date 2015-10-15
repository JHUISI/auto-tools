AutoGroup+
==========

Often, pairing-based cryptographic schemes are described using symmetric groups. While these groups simplify the description of new cryptographic schemes, they are rarely the most efficient setting for implementation. Asymmetric groups represent the state-of-the-art in terms of efficiency and converting schemes from symmetric to an asymmetric solution currently requires manual analysis. We demonstrate with AutoGroup how to automate such conversions using SMT solvers as a core building block.  

AutoGroup: [ACM CCS 2013](http://dl.acm.org/citation.cfm?id=2516718)

AutoGroup+: [ACM CCS 2015](http://dl.acm.org/citation.cfm?doid=2810103.2813601) [eprint](http://eprint.iacr.org/2015/290)

Installation
============

AutoGroup+ requires Python 3 or greater and you will need the [Charm-Crypto](https://github.com/jhuisi/charm/downloads) framework (v0.43) to execute the automatically generated asymmetric scheme in Python and/or C++.

AutoGroup+ also requires the [Z3](https://github.com/Z3Prover/z3) Theorem prover (with Python 3 bindings).

Here are the install steps for Z3:

    git clone https://github.com/Z3Prover/z3.git
    python3 scripts/mk_make.py
    cd build
    make

Running The Tool
================

For the help menu, execute the following:

    #: python3 runAutoGroup.py -h
    usage: runAutoGroup.py [-h] -o OUTFILE -s SDL [-v] -c CONFIG [-l LIBRARY] [-b]
                           [-e] [--short SHORT] [--path PATH] [--print] [-a]
    
    sym.-to-asym. conversion for cryptographic schemes in SDL.
    
    optional arguments:
      -h, --help            show this help message and exit
      -o OUTFILE, --outfile OUTFILE
                            generate code of new scheme in C++/Python for Charm
      -s SDL, --sdl SDL     input SDL file description of scheme
      -v, --verbose         enable verbose mode
      -c CONFIG, --config CONFIG
                            configuration parameters needed for AutoGroup
      -l LIBRARY, --library LIBRARY
                            which library to benchmark against: miracl or relic
      -b, --benchmark       benchmark AutoGroup execution time
      -e, --estimate        estimate bandwidth for keys and ciphertext/signatures
      --short SHORT         what to minimize: public-keys, secret-keys,
                            assumption, ciphertext, signatures
      --path PATH           destination for AutoGroup+ output files. Default:
                            current dir
      --print               print the selected options
      -a, --autogroup       run AutoGroup only (and not AutoGroup+)
			

An example for how to execute AutoGroup on the Camenisch-Lysyanskaya (CL) signature scheme with basic options:

	python3 runAutoGroup.py --sdl schemes/cl04.sdl --config schemes/configCL.py -o TestCL -v

Note that AutoGroup+ was designed to handle both encryption and signature schemes.

Configuration
=============

AutoGroup provides several configuration parameters to tune conversion to an asymmetric solution. 
The configuration file is specified in Python with the following options:

``schemeType`` : for describing the type of input scheme. For public-key encryption, ``"PKENC"`` and for signature types, ``"PKSIG"``.

``operation`` : to find a solution that reduces the computation time based on cost of ``"exp"``(exponentiation) or ``"mul"``(multiplication). 

``dropFirst`` : in the event that there are multiple solutions that satisfy the ``"both"`` option of the ``short`` representation requirement, users must specify what option to relax to constrain the options further. The options are ``"public-key"`` or ``"signatures"`` for signatures and ``"secret-keys"`` or ``"ciphertext"`` for encryption.

The next set of variables describe basic aspects of the signature or encryption scheme:

``keygenPubVar``: denotes the user's public-key

``keygenSecVar``: denotes the user's secret-key 

``signatureVar``: denotes the signature if scheme type is ``PKSIG``

``ciphertextVar``: denotes the ciphertext if scheme type is ``PKENC``

``masterPubVars``: denotes the public parameters available to all users of the system (if applicable)

``masterSecVars``: denotes the master secret-key (if applicable)

We require function names of algorithms described in the SDL specified as ``setupFuncName`` and ``keygenFuncName``. Also, for signature schemes, must specify the ``signFuncName`` and ``verifyFuncName``. For encryption, must specify the ``encryptFuncName`` and ``decryptFuncName``. 

We provide a complete configuration file example for the CL signature:

	schemeType = "PKSIG"
	operation = "exp"
	
	setupFuncName 	= "setup"
	keygenFuncName 	= "keygen"
	signFuncName 	= "sign"
	verifyFuncName 	= "verify"
	
	masterPubVars = None
	masterSecVars = None
	
	keygenPubVar = "pk"
	keygenSecVar = "sk" 
	signatureVar = "sig" 

See more examples in the ``schemes`` directory.
 