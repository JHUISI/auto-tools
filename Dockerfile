FROM ubuntu:16.04

RUN apt update && apt install --yes build-essential flex bison wget git subversion m4 python3 python3-dev python3-setuptools libgmp-dev libssl-dev
RUN wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz && tar xvf pbc-0.5.14.tar.gz && cd /pbc-0.5.14 && ./configure LDFLAGS="-lgmp" && make && make install && ldconfig
RUN git clone https://github.com/JHUISI/charm.git /charm && cd /charm && ./configure.sh && make && make install && ldconfig
RUN git clone https://github.com/Z3Prover/z3.git /z3 && cd /z3 && python3 scripts/mk_make.py && cd build && make && make install
COPY . /auto-tools
