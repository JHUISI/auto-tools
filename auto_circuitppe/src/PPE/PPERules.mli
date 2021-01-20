
open Util
open PPEInput 
open Sage_Solver


val rule1 : st_sage -> ppe -> int -> (bool * circuit * ppe)

val rule2 : st_sage -> ppe -> int -> (bool * ppe)

val rule3 : st_sage -> ppe -> int -> (bool * circuit * circuit * ppe * ppe)

val rule4 : st_sage -> ppe -> int -> (bool * circuit * ppe * ppe)

(* val rule5 : st_sage -> ppe -> int -> (bool * circuit * circuit * ppe * ppe)

val rule6 : st_sage -> ppe -> int -> (bool * circuit * ppe * ppe)
 *)
