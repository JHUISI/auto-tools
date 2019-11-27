(*s Input for non-parametric problems.\\ *)

(*i*)
open Util
(*i*)

(*******************************************************************)
(* \hd{Group settings, group elements, and assumptions} *)

(* \ic{Each group has an identifier.} *)
type group_id = string

(* \ic{An isomorphism has a domain and a codomain.} *)
type iso = { iso_dom : group_id; iso_codom : group_id; }

(* \ic{A multi-linear map has a domain and a codomain.} *)
type emap = { em_dom : group_id list; em_codom : group_id; }

(* \ic{A group setting consists of isomorphisms and multilinear maps.
       Group ids are implicit.} *)
type group_setting = {
  gs_isos : iso list;
  gs_emaps : emap list;
  gs_prime_num : int;
}

type recipe =
  | Param of int
  | Iso   of iso * recipe
  | Emap  of emap * recipe list
  | Multiply of recipe list
  | Exp of recipe * int

(* \ic{%
   A closed group setting consists of isomorphisms, multilinear maps,
   the target group, and the set of group ids. It has been validated.} *)
type closed_group_setting = private {
  cgs_isos      : iso list;
  cgs_emaps     : emap list;
  cgs_prime_num : int;
  cgs_target    : group_id;
  cgs_gids      : Ss.t;
}


(* \ic{Random polyomials such as $X*X + Y$.} *)
type rvar = string

(* \ic{Random polyomials such as $X*X + Y$.} *)
module RP : LPolyInterfaces.Poly with type var = rvar and type coeff = Big_int.big_int

type rpoly = RP.t

(* \ic{[rp_to_vector mon_basis f] converts [f] to a coefficient vector with respect to the
   monomial basis [mon_basis]. We do not check if [f] contains monomials not included in [mon_basis].} *)
val rp_to_vector : RP.monom list -> rpoly -> RP.coeff list

(* \ic{We model a group element as a list of random polynomials and
   a group identifier. The length of the list corresponds to the number
   of primes dividing the group order.} *)
type group_elem = {
  ge_id : recipe;
  ge_rpoly : rpoly;
  ge_group : group_id option;
}

type ppe = {
  ppe_cgs : closed_group_setting;
  ppe_fixed : group_elem list;
  ppe_zp : group_elem list;
  (* ppe_unfixed : group_elem list; *)
  ppe_trusted : group_elem list;
  ppe_untrusted : group_elem list;
}

val extract_group : group_id option -> group_id
val extract_fid : recipe -> int

val equal_group_elem : group_elem -> group_elem -> bool

val shape: group_elem list -> (int * group_id) list

(*******************************************************************)
(* \hd{Smart constructors for group settings and assumptions} *)

(* \ic{The given assumption is invalid.} *)
exception InvalidInput of string

(* \ic{Fail because assumption is invalid.} *)
val fail_assm : string -> 'a

(* \ic{Validate grout setting and create closed group setting.} *)
val close_group_setting : group_setting -> closed_group_setting

(* \ic{Create group setting for generic group (no isomorphisms and no maps, single group).} *)
val closed_generic_group : group_id -> int -> closed_group_setting

(*******************************************************************)
(* \hd{Commands for building assumptions} *)

type cmd =
  | AddIsos of iso list
  | AddMaps of emap list
  | SetPrimeNum of int
  | AddFixed of group_elem list
  | AddUnfixed of group_elem list
  | AddTrusted of group_elem list
  | AddUntrusted of group_elem list
  | AddZp of group_elem list

type incomp_assm = {
  ia_gs            : group_setting;
  ia_trusted       : group_elem list;
  ia_untrusted     : group_elem list;
  ia_fixed         : group_elem list;
  ia_unfixed       : group_elem list;
  ia_zp            : group_elem list;
}

val empty_ias : incomp_assm

val handle_cmd : cmd -> incomp_assm -> incomp_assm

val eval_cmds : cmd list -> ppe

(*i*)
val pp_iso        : F.formatter -> iso           -> unit
val pp_emap       : F.formatter -> emap          -> unit
val pp_iso_s      : F.formatter -> iso           -> unit
val pp_emap_s     : F.formatter -> emap          -> unit
val pp_group_id   : F.formatter -> group_id option  -> unit
val pp_rp_vec     : F.formatter -> rpoly list    -> unit
val pp_group_elem : F.formatter -> group_elem    -> unit
val pp_gs         : F.formatter -> group_setting -> unit
val pp_cmd        : F.formatter -> cmd           -> unit
(*i*)

(*i*)
(* Only for testing *)
module Internals : sig
  val gs_is_cyclic : group_setting -> bool
end
(*i*)
