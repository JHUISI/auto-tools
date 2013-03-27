import batcher.miraclbench2
import batcher.relicbench

#global curve, param_id
#library = "relic" # or "relic"

def getBenchmarkInfo(library):
#   global curve, param_id
   curve = param_id = None
   if library == "miracl":
       curve = batcher.miraclbench2.benchmarks
       param_id  = batcher.miraclbench2.key # pairing-friendly curve over a extension field (prime-based)
   elif library == "relic":
       curve = batcher.relicbench.benchmarks
       param_id  = batcher.relicbench.key # pairing-friendly curve over a extension field (prime-based)
   return (curve, param_id)
