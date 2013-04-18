"""
Bellare-Shoup Transformation - if a signature is NOT partitionable, then we can apply the less efficient BS transform to 
convert the signature to a strongly-unforgeable signature.
"""
import src.sdlpath, importlib
import sdlparser.SDLParser as sdl
from sdlparser.SDLang import *
from src.sdltechniques import *
