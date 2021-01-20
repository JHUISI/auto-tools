(* This file is distributed under the MIT License (see LICENSE). *)

open Poly
open Util

(* \ic{We use strings as variables for constraint polyomials.} *)
module SP = MakePoly(
  struct
    type t = string
    let pp = pp_string
    let equal = (=)
    let compare = compare
  end) (IntRing)
