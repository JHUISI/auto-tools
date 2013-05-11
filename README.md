AutoTools : automated cryptographic transformations
==========================================================

A collection of automated Python tools that we are developing towards transforming cryptographic primitives in different ways:

* [AutoBatch](https://github.com/JHUISI/auto-tools/tree/master/auto_batch): an automated tool for designing batch verification algorithms.

* [AutoStrong](https://github.com/JHUISI/auto-tools/tree/master/auto_strong): an automated tool for converting existentially unforgeable signatures into ones that are strongly unforgeable.

* [AutoGroup](https://github.com/JHUISI/auto-tools/tree/master/auto_group): an automated tool for optimizing pairing-based encryption and signature schemes using SMT solver techniques.

* [CloudSource](https://github.com/JHUISI/auto-tools/tree/master/auto_outsrc): an automated tool for outsourcing the computation of pairing-based schemes to untrusted cloud proxies. 

The above tools take as input a scheme description language (SDL) of a cryptographic algorithm then performs the described transformation. See subdirectories for how to run each tool and sample SDL schemes. Some are more mature than others but in due time all will be ready for public release.
