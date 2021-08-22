DESTDIR    ?=
PREFIX     ?= /usr/local
VERSION    ?= $(shell date '+%F')
DISTDIR    := easycrypt-$(VERSION)
INSTALL    := scripts/install/install-sh
PWD        := $(shell pwd)

BINDIR := $(PREFIX)/bin

INSTALL    := scripts/install/install-sh

#############################################################################

OCAMLBUILD_OPTS = -tag annot -tag debug -use-ocamlfind
OCAMLBUILD_OPTS += -use-menhir -menhir "menhir -v"

ifeq ($(shell echo $$TERM), dumb)
 OCAMLBUILD_OPTS += -classic-display
endif

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
  LIBFLAGS=-lflags -cclib,-Xlinker,-cclib,--no-as-needed,-cclib,-Lc_src,-cclib,-lpari,-cclib,-lparistubs
endif
ifeq ($(UNAME_S),Darwin)
  LIBFLAGS=-lflags -cclib,-Lc_src,-cclib,-lpari,-cclib,-lparistubs
endif

OCAMLBUILD=LD_LIBRARY_PATH=_build/c_src/ ocamlbuild
CFLAGS="-w +a-e-9"

#############################################################################
 
.PHONY: autorationalppe.native doc install uninstall

all: autorationalppe.native

autorationalppe.native:
	test -d _build/c_src || mkdir -p _build/c_src
	gcc -fPIC -c c_src/pari_stubs.c -o _build/c_src/pari_stubs.o
	ar rc _build/c_src/libparistubs.a _build/c_src/pari_stubs.o
	gcc -shared -o _build/c_src/libparistubs.so _build/c_src/pari_stubs.o -lpari
	$(OCAMLBUILD) $(OCAMLBUILD_OPTS) -cflags $(CFLAGS) $(LIBFLAGS) src/Tool/autorationalppe.native

install:
	$(INSTALL) -m 0755 -d $(DESTDIR)$(BINDIR)
	$(INSTALL) -m 0755 -T autorationalppe.native $(DESTDIR)$(BINDIR)/auto-ppe
	cp _build/c_src/libparistubs.so /usr/lib

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/auto-ppe

#############################################################################
# Development

clean:
	-rm doc/tool.pdf
	$(OCAMLBUILD) -clean

byte:
	$(OCAMLBUILD) -tag annot -tag debug -cflags $(CFLAGS) $(LIBFLAGS) $(FINDLIBFLAGS) $(MENHIRFLAGS) src/Tool/ggt.byte
	OCAMLRUNPARAM="-b" ./ggt.byte examples/dhe.ggt

# paramtest:
# 	$(OCAMLBUILD) -tag annot -tag debug -cflags $(CFLAGS) $(LIBFLAGS) $(FINDLIBFLAGS) $(MENHIRFLAGS) src/Param/ParamTest.native
# 	./ParamTest.native

# nonparamtest:
# 	$(OCAMLBUILD) -tag annot -tag debug -cflags $(CFLAGS) $(LIBFLAGS) $(FINDLIBFLAGS) $(MENHIRFLAGS) src/NonParam/NonParamTest.native
# 	./NonParamTest.native

# interactivetest:
# 	$(OCAMLBUILD) -tag annot -tag debug -cflags $(CFLAGS) $(LIBFLAGS) $(FINDLIBFLAGS) $(MENHIRFLAGS) src/Interactive/InteractiveTest.native
# 	./InteractiveTest.native

ppetest:
	$(OCAMLBUILD) -tag annot -tag debug -cflags $(CFLAGS) $(LIBFLAGS) $(FINDLIBFLAGS) $(MENHIRFLAGS) src/PPE/PPETest.native
	./PPETest.native

webdoc:
	pandoc -s -S --toc -c buttondown.css README > web/help.html


loc:
	find src -name \*.ml\* | xargs wc -l

cleangen:
	rm -rf gen
	mkdir gen
	mkdir gen/attack

%.inferred.mli:
	ocamlbuild -use-ocamlfind $(OCAMLBUILDFLAGS) src/Poly/$@ && cat _build/src/Poly/$@
	ocamlbuild -use-ocamlfind $(OCAMLBUILDFLAGS) src/Util/$@ && cat _build/src/Util/$@
	ocamlbuild -use-ocamlfind $(OCAMLBUILDFLAGS) src/PPE/$@ && cat _build/src/PPE/$@
	ocamlbuild -use-ocamlfind $(OCAMLBUILDFLAGS) src/Synthesis/$@ && cat _build/src/Synthesis/$@


#############################################################################
# Document generation

INFRA_MODULES=Util/Util.ml Poly/PolyInterfaces.mli Poly/Poly.mli Poly/Poly.ml

# NONPARAM_MODULES= NonParam/NonParamInput.mli NonParam/NonParamInput.ml \
#   NonParam/NonParamCompletion.ml NonParam/NonParamCompletion.mli \
#   Solver/Sage_Solver.ml \
#   NonParam/NonParamParser.mly NonParam/NonParamLexer.mll \
#   NonParam/NonParamAnalyze.ml \
#   NonParam/NonParamTest.ml

# PARAM_MODULES=Param/ParamInput.mli Param/ParamInput.ml \
#   Param/ParamConstraints.ml Solver/Z3_Solver.ml \
#   Param/ParamParser.mly Param/ParamLexer.mll Param/ParamAnalyze.ml \
#   Param/ParamTest.ml

# INTERACTIVE_MODULES=Interactive/InteractiveInput.ml \
#   Interactive/InteractiveEval.ml \
#   Interactive/InteractiveParser.mly \
#   Interactive/InteractiveLexer.mll \
#   Interactive/InteractiveBounded.ml \
#   Interactive/InteractiveFormalSum.ml \
#  Interactive/InteractiveUnbounded.ml \
#   Interactive/InteractiveAnalyze.ml \
#   Interactive/InteractiveTest.ml

SYNTH_MODULES=Synthesis/Synthesis.ml

TOOL_MODULES = Tool/ggt.ml

INFRA_FILES=$(addprefix src/,$(INFRA_MODULES))
# NONPARAM_FILES=$(addprefix src/,$(NONPARAM_MODULES))
# PARAM_FILES=$(addprefix src/,$(PARAM_MODULES))
# INTERACTIVE_FILES=$(addprefix src/,$(INTERACTIVE_MODULES))
SYNTH_FILES=$(addprefix src/,$(SYNTH_MODULES))
TOOL_FILES=$(addprefix src/,$(TOOL_MODULES))

doc:
	ocamlweb doc/prelude.tex \
	  doc/chap-infra.tex $(INFRA_FILES) \
	  # doc/chap-nonparam.tex $(NONPARAM_FILES) \
	  # doc/chap-param.tex $(PARAM_FILES) \
	  # doc/chap-interactive.tex $(INTERACTIVE_FILES) \
	  doc/chap-synth.tex $(SYNTH_FILES) \
	  doc/chap-tool.tex $(TOOL_FILES) \
	  doc/close.tex --no-preamble --header > doc/tool.tex.tmp
	echo "\end{document}" >> doc/tool.tex.tmp
	mv doc/tool.tex.tmp doc/tool.tex
	cd doc && latexmk -pv -pdf tool.tex
