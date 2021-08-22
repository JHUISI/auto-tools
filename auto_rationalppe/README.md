# AutoRationalPPE
Here is the implementation of our tool AutoRationalPPE. 

### Installation
The code of AutoRationalPPE is written in OCAML language. In order to compile OCAML files, please install OPAM. In MacOS, run
~~~~~
$ brew install opam
~~~~~
In ubuntu, run
~~~~~
$ sudo apt-get install opam
~~~~~

We use OCAML version 4.02.3 for AutoRationalPPE project. The code does not compile with latest version of OCAML. Install 4.02.3 version of OCAML with the following command.
~~~~~
$ opam switch autorationalppe --alias-of 4.02.3
$ eval `opam config env`
~~~~~
Here, autorationalppe could be replaced with any name. When you check the ocaml version, you should get 4.02.3
~~~~~
$ ocaml -version
4.02.3
~~~~~

Install OCAML packages using the following command.
~~~~~
$ opam install ocamlfind yojson.1.3.2 ctypes-foreign.0.4.0 ctypes.0.4.1 cryptokit.1.10 menhir
~~~~~
Here is the list of packages that will be installed after you run the above command. Many of the packages are not backward compatible. AutoRationalPPE code many not work with latest version of the packages. In case you installed the latest version of any package, please consider downgrading the package to the version below. 
~~~~~
$ opam list
# Installed packages for autorationalppe:
base-bigarray          base  Bigarray library distributed with the OCaml compiler
base-bytes             base  Bytes library distributed with the OCaml compiler
base-num               base  Num library distributed with the OCaml compiler
base-ocamlbuild        base  OCamlbuild binary and libraries distributed with the OCaml compiler
base-threads           base  Threads library distributed with the OCaml compiler
base-unix              base  Unix library distributed with the OCaml compiler
biniou                1.2.0  Binary data format designed for speed, safety, ease of use and backward compatibility as protocols evolve
conf-m4                   1  Virtual package relying on m4
conf-pkg-config         1.1  Virtual package relying on pkg-config installation.
conf-which                1  Virtual package relying on which
conf-zlib                 1  Virtual package relying on zlib
cppo                  1.6.4  Equivalent of the C preprocessor for OCaml programs
cryptokit              1.10  Cryptographic primitives library. 
ctypes                0.4.1  Combinators for binding to C libraries without writing any C.
ctypes-foreign        0.4.0  Virtual package for enabling the ctypes.foreign subpackage.
dune                  1.0.0  Fast, portable and opinionated build system
easy-format           1.3.1  High-level and functional interface to the Format module of the OCaml standard library
jbuilder         transition  This is a transition package, jbuilder is now named dune. Use the dune
menhir             20180905  LR(1) parser generator
num                       0  The Num library for arbitrary-precision integer and rational arithmetic
ocamlbuild                0  Build system distributed with the OCaml compiler since OCaml 3.10.0
ocamlfind             1.8.0  A library manager for OCaml
yojson                1.3.2  Yojson is an optimized parsing and printing library for the JSON format 
~~~~~

The tool additionally relies on Sage package. In Mac, sage can be installed with the following command. 

~~~~
$ brew cask install sage
~~~~

### Compilation
To compile AutoRationalPPE code, cd to the main folder of AutoRationalPPE and run
~~~~~
$ make
~~~~~

The example files are present in examples directory. To run example  examples/type1/BW.txt, run
~~~~~
$ ./autorationalppe.native examples/type1/BW.txt
~~~~~

### Possible Errors
When compiling AutoRationalPPE code, in case you get an error of type 
~~~~~
	Error: Files src/Util/Util.cmx
       and /Users/satya/.opam/autorationalppe/lib/yojson/yojson.cmx
       make inconsistent assumptions over implementation Yojson
~~~~~
it means the code is compiled against an outdated version of an interface. Simply run,
~~~~~
$ make clean
$ make
~~~~~

When you reopen terminal, OPAM automatically switches to the latest version OCAML. Check the version of OCAML by running $ ocaml -version. In case your version is not 4.02.3, you may get an error of type
~~~~~
Error: src/Util/util.cmi
is not a compiled interface for this version of OCaml.
It seems to be for an older version of OCaml.
~~~~~
In such a case, switch to OCAML version 4.02.3 with the following command. Run make command.
~~~~~
$ opam switch autorationalppe
$ eval `opam config env`
~~~~~
