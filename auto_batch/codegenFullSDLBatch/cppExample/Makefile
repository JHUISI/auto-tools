CXX	:= g++
#CXXFLAGS := -fno-strict-aliasing -fno-common -g -m64 -O2 -fwrapv -O3 -Wall
CXXFLAGS := -g -m64 -O2 -O3 -Wall

# should be set by codegen
SDL_SRC := bls
NAME    := test_bls
# CURVE := ssp 
CURVE   := mnt

OBJECTS	:= group.o $(SDL_SRC).o 
LIB     := miracl-$(CURVE).a
 
# link SDL object file with miracl lib 
.PHONY: $(NAME)
$(NAME): lib $(OBJECTS) 
	$(CXX) $(OBJECTS) $(LIB) -o $(NAME)

# compile target SDL sourcefile
$(SDL_SRC).o: $(SDL_SRC).cpp
	$(CXX) $(CXXFLAGS) -c $(SDL_SRC).cpp -o $(SDL_SRC).o

group.o: group.cpp
	$(CXX) $(CXXFLAGS) -c group.cpp -o group.o
	
# need target for building miracl version lib
.PHONY: lib
lib:
	sh build_miracl.sh $(CURVE)

clean:
	rm *.o
