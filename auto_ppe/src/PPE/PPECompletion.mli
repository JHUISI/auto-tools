(*i*)
open PPEInput
open Util
(*i*)

(* \ic{%
   Given a group setting and a list of group elements ([inputs]),
   return the elements of the completion residing in the target group
   and the corresponding recipes. The list of recipes only depends on
   the shape of the [inputs] list.} *)
val completion_for_group :
  closed_group_setting ->
  group_id ->
  group_elem list ->
  (group_elem list * recipe list)

val new_completion_for_group:
  closed_group_setting ->
  group_id ->
  group_elem list ->
  group_elem list ->
  (group_elem list * recipe list)


(* \ic{Same as before, but for two input lists at once computing
   the recipes only once.} *)
(* val completions_for_group :
  closed_group_setting ->
  group_id -> group_elem list -> group_elem list ->
  (rpoly list * rpoly list * recipe list) *)

val rp_equal : recipe -> recipe -> bool
val pp_recipe : F.formatter -> recipe -> unit
val pp_recipes : F.formatter -> group_elem list -> unit