#!/bin/bash

#FILESIZE=$(stat -c%s "$FILENAME")
#echo "Size of $FILENAME = $FILESIZE bytes."

set -x

# good
python runAutoBatch.py --sdl schemes/BLS/bls.sdl --outfile schemes/BLS/bls-full-batch2.sdl
diff schemes/BLS/bls-full-batch.sdl schemes/BLS/bls-full-batch2.sdl > bls_result.txt

# good
python runAutoBatch.py --sdl schemes/BOYEN/boyen.sdl --outfile schemes/BOYEN/boyen-full-batch2.sdl
diff schemes/BOYEN/boyen-full-batch.sdl schemes/BOYEN/boyen-full-batch2.sdl > boyen_result.txt

# good
python runAutoBatch.py --sdl schemes/CHCH/chch.sdl --outfile schemes/CHCH/chch-full-batch2.sdl
diff schemes/CHCH/chch-full-batch.sdl schemes/CHCH/chch-full-batch2.sdl > chch_result.txt

# good
python runAutoBatch.py --sdl schemes/CHP/chp.sdl --outfile schemes/CHP/chp-full-batch2.sdl
diff schemes/CHP/chp-full-batch.sdl schemes/CHP/chp-full-batch2.sdl > chp_result.txt

# good
python runAutoBatch.py --sdl schemes/CL/cl.sdl --outfile schemes/CL/cl-full-batch2.sdl
diff schemes/CL/cl-full-batch.sdl schemes/CL/cl-full-batch2.sdl > cl_result.txt

# good
python runAutoBatch.py --sdl schemes/HESS/hess.sdl --outfile schemes/HESS/hess-full-batch2.sdl
diff schemes/HESS/hess-full-batch.sdl schemes/HESS/hess-full-batch2.sdl > hess_result.txt

# good
python runAutoBatch.py --sdl schemes/HW/hw.sdl --outfile schemes/HW/hw-full-batch2.sdl
diff schemes/HW/hw-full-batch.sdl schemes/HW/hw-full-batch2.sdl > hw_result.txt

# good
python runAutoBatch.py --sdl schemes/VRF/vrf.sdl --outfile schemes/VRF/vrf-full-batch2.sdl
diff schemes/VRF/vrf-full-batch.sdl schemes/VRF/vrf-full-batch2.sdl > vrf_result.txt

# good
python runAutoBatch.py --sdl schemes/WATERS05/waters05.sdl --outfile schemes/WATERS05/waters05-full-batch2.sdl
diff schemes/WATERS05/waters05-full-batch.sdl schemes/WATERS05/waters05-full-batch2.sdl > waters05_result.txt

# good
python runAutoBatch.py --sdl schemes/WATERS09/waters09.sdl --outfile schemes/WATERS09/waters09-full-batch2.sdl
diff schemes/WATERS09/waters09-full-batch.sdl schemes/WATERS09/waters09-full-batch2.sdl > waters09_result.txt

# good
python runAutoBatch.py --sdl schemes/BBS/bbs.sdl --outfile schemes/BBS/bbs-full-batch2.sdl
diff schemes/BBS/bbs-full-batch.sdl schemes/BBS/bbs-full-batch2.sdl > bbs_result.txt

# good
python runAutoBatch.py --sdl schemes/WATERS09/dse09var.sdl --outfile schemes/WATERS09/dse09var-full-batch2.sdl

set +x
