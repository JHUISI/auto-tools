"""
Bellare-Shoup Transformation - if a signature is NOT partitionable, then we can apply the less efficient BS transform to 
convert the signature to a strongly-unforgeable signature.
"""
import src.sdlpath, importlib
import sdlparser.SDLParser as sdl
from sdlparser.SDLang import *
from src.sdltechniques import *

output = """\n
require := blah1.sdl
require := blah2.sdl

BEGIN :: func:newFunc
input := {None}

s := newFunc( )


"""
