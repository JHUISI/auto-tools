AutoTools: automated tools
==========================

A collection of Python tools being developed towards automatically transforming cryptographic primitives in different and interesting ways:

* [AutoBatch](https://github.com/JHUISI/auto-tools/tree/master/auto_batch): an automated tool for designing batch verification algorithms.

* [AutoStrong](https://github.com/JHUISI/auto-tools/tree/master/auto_strong): an automated tool for converting existentially unforgeable signatures into ones that are strongly unforgeable.

* [AutoGroup](https://github.com/JHUISI/auto-tools/tree/master/auto_group): an automated tool for optimizing pairing-based encryption and signature schemes using SMT solver techniques.

* [CloudSource](https://github.com/JHUISI/auto-tools/tree/master/auto_outsrc): an automated tool for outsourcing the computation of pairing-based schemes to untrusted cloud proxies. 

The above tools take as input a scheme description language (SDL) of a cryptographic algorithm then performs the described transformation. See subdirectories for how to run each tool and sample SDL schemes. Please contact us if you have any questions or comments at akinyelj [ AT ] cs.jhu.edu OR mpagano [ AT ] cs.jhu.edu. 

Scheme Description Language
===========================

SDL is a domain-specific language for abstractly representing cryptographic schemes. In the current instantiation, SDL focuses mainly on pairing-based encryption and signature primitives. There are several SDL schemes within this repository which demonstrate the syntax and semantics of the language. 