AutoTools: automated tools
==========================

[![Build Status](https://travis-ci.org/JHUISI/auto-tools.png)](https://travis-ci.org/JHUISI/auto-tools)

A collection of Python tools being developed towards automatically transforming cryptographic primitives in different and interesting ways:

* [AutoBatch](https://github.com/JHUISI/auto-tools/tree/master/auto_batch): an automated tool for designing batch verification algorithms.

* [AutoStrong](https://github.com/JHUISI/auto-tools/tree/master/auto_strong): an automated tool for converting existentially unforgeable signatures into ones that are strongly unforgeable.

* [AutoGroup+](https://github.com/JHUISI/auto-tools/tree/master/auto_group): an automated tool for optimizing pairing-based encryption and signature schemes using SMT solver techniques.

* [CloudSource](https://github.com/JHUISI/auto-tools/tree/master/auto_outsrc): an automated tool for outsourcing the computation of pairing-based schemes to untrusted cloud proxies. 

* [AutoPPE](https://github.com/JHUISI/auto-tools/tree/master/auto_ppe): an automated tool for creating a conjunction of pairing-product equations (PPEs) to verify a set of untrusted elements with respect to a set of trusted elements.

* [AutoCircuitPPE](https://github.com/JHUISI/auto-tools/tree/master/auto_circuitppe): an automated tool for creating a PPE Circuit (containing AND, OR, NOT and PPE gates) to verify a set of untrusted elements with respect to a set of untrusted elements.

* [AutoRationalPPE](https://github.com/JHUISI/auto-tools/tree/master/auto_rationalppe): an automated tool that extends AutoCircuitPPE to support rational polynomials.

The above tools take as input a scheme description language (SDL) of a cryptographic algorithm then performs the described transformation. See subdirectories for how to run each tool and sample SDL schemes. Please contact us if you have any questions or comments at akinyelj [ AT ] cs.jhu.edu OR mpagano [ AT ] cs.jhu.edu. 

Scheme Description Language
===========================

SDL is a domain-specific language for abstractly representing cryptographic schemes. In the current instantiation, SDL focuses mainly on pairing-based encryption and signature primitives. There are several SDL schemes within this repository that demonstrate the syntax and semantics of the language. For examples, click [here](https://github.com/JHUISI/auto-tools/wiki/Scheme-Description-Language).
