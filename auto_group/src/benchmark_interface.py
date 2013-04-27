import src.miraclbench
#import src.relicbench


def getBenchmarkInfo(library="miracl"):
   curve = param_id = None
   if library == "miracl":
       curve = src.miraclbench.benchmarks
       param_id  = src.miraclbench.key # pairing-friendly curve over a extension field (prime-based)
#   elif library == "relic":
#       curve = src.relicbench.benchmarks
#       param_id  = src.relicbench.key # pairing-friendly curve over a extension field (prime-based)
   return (curve, param_id)
