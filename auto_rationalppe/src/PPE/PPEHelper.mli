
open PPEInput
open Util 

val print_problem : ppe -> unit

val multiply_zp : group_elem -> group_elem list -> group_elem list

val remove_duplicates : group_elem list -> group_elem list

val add_non_duplicates : group_elem list -> group_elem list -> group_elem list

val transferpoly : ppe -> int -> ppe 

val remove : group_elem -> group_elem list -> group_elem list

val optimize1 : group_elem list -> group_elem list -> group_elem list

val optimize2 : group_elem list -> group_elem list -> group_elem list

val optimize : group_elem list -> group_elem list -> group_elem list * group_elem list

val normalize : group_elem list -> group_elem list * rpoly