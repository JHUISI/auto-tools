(* This file is distributed under the MIT License (see LICENSE). *)

(*s Input for non-parametric problems.\\ *)

(*i*)
open Util
open LPoly
(*i*)

(*******************************************************************)
(* \hd{Group settings, group elements, and assumptions (see .mli file for docs)} *)

exception InvalidInput of string

let fail_assm s = raise (InvalidInput s)

type group_id = string

type iso = {
  iso_dom   : group_id;
  iso_codom : group_id
}

type emap = {
  em_dom   : group_id list;
  em_codom : group_id
}

type group_setting = {
  gs_isos      : iso list;
  gs_emaps     : emap list;
  gs_prime_num : int
}

type closed_group_setting = {
  cgs_isos      : iso list;
  cgs_emaps     : emap list;
  cgs_prime_num : int;
  cgs_target    : group_id;
  cgs_gids      : Ss.t
}

type rvar = string

module RP = MakePoly(struct
  type t = rvar
  let pp = pp_string
  let equal = (=)
  let compare = compare
end) (IntRing)

type rpoly = RP.t

let rp_to_vector mon_basis f = L.map (fun m -> RP.coeff f m) mon_basis

(*******************************************************************)
(* \hd{Recipes and recipe polynomials} *)

(* \ic{A recipe describes how to compute a term from a list of inputs.
   [Param(i)] stands for taking the $i$-th element,
   [Iso(i,r)] stands for computing $r$ and then applying the isomorphism $i$, and
   [Emap(e,rs)] stands for computing $rs$ and then applying the map $e$.} *)
type recipe =
  | Param of int
  | Iso   of iso * recipe
  | Emap  of emap * recipe list
  | Multiply of recipe list
  | Exp of recipe * int


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

let extract_fid fid = 
  match fid with 
  | Param(i) -> i
  | _ -> fail_assm "Invalid FID!!!"

let extract_group ge = 
  match ge with 
  | None -> fail_assm "Extracting group of a poly without a group"
  | Some g -> g

(* let equal_rp_list a b =
  list_equal (fun f g -> RP.equal f g) a b *)

let equal_group_elem a b = a.ge_group = b.ge_group && RP.equal a.ge_rpoly b.ge_rpoly

let shape ges = L.map (fun ge -> ((extract_fid ge.ge_id), (extract_group ge.ge_group))) ges


(*******************************************************************)
(* \hd{Cyclicity of group settings} *)

(* \ic{[gs_group_ids gs] returns the group ids occuring in domains and codomains in [gs].} *)
let gs_group_ids gs =
  let add_gids s l = Ss.union s (ss_of_list l) in
  let gids = L.fold_left (fun s i -> add_gids s [i.iso_codom; i.iso_dom]) Ss.empty gs.gs_isos
  in L.fold_left (fun s e -> add_gids s (e.em_codom::e.em_dom)) gids gs.gs_emaps

(* \ic{%
   [gs_iso_edges gs] returns the edges induced by the isomorphisms in [gs].
   Concretely, it returns a map [m] such that [m[i]] contains all [j]
   such that there is a $\phi : i \to j$.} *)
let gs_iso_edges gs =
  L.fold_left (fun m i -> ss_add_set i.iso_dom i.iso_codom m) Ms.empty gs.gs_isos

(* \ic{%
   [gs_emap_edges gs] returns the edges induced by the multilinear maps in [gs].
   Concretely, it returns a map [m] such that [m[i]] contains all [j]
   such that there is an $e : \ldots \times i \times \ldots \to j$.} *)
let gs_emap_edges gs =
  L.fold_left
    (fun m e -> L.fold_left (fun m src -> ss_add_set src e.em_codom m) m e.em_dom)
    Ms.empty
    gs.gs_emaps

(* \ic{Internal exception for [gs_is_cyclic].} *)
exception Cyclic of group_id

(* \ic{%
   [gs_is_cyclic gs] returns [true] if the group setting has
   a cycle that allows for an unbounded number of mutiplications.
   More precisely, consider the weighted graph with group ids $i$ as
   vertices and edges $i \mapsto i'$ of weight zero for all isomorphisms
   $\phi: i \to i'$ and edges $i_1 \mapsto i',\ldots, i_k \mapsto i'$ with weight
   one for all multilinear maps $e : i_1 \times \ldots \times i_k \to i'$.
   The group setting is cyclic iff the graph has a cycle with non-zero
   weight.} *)
let gs_is_cyclic gs =
  let succs gid m = try Ms.find gid m with Not_found -> Ss.empty in
  let iso_edges  = gs_iso_edges gs in
  let emap_edges = gs_emap_edges gs in
  let unexplored = ref (gs_group_ids gs) in
  
  (* \ic{Start at [n] and explore reachable nodes. Keep track of
         path weight and path members.} *)
  let rec explore n path_weight path_mems =
    if Ss.mem n path_mems then (if path_weight then raise (Cyclic n))
    else (
      unexplored := Ss.remove n !unexplored;
      let path_mems = Ss.add n path_mems in
      Ss.iter (fun n -> explore n true        path_mems) (succs n emap_edges);
      Ss.iter (fun n -> explore n path_weight path_mems) (succs n iso_edges)
    )
  in

  (* \ic{Iterate [explore] for unexplored nodes until [Cyclic] is raised
     or all nodes are explored.} *)
  let rec loop () =
    if Ss.is_empty !unexplored then false
    else
      try explore (Ss.choose !unexplored) false Ss.empty; loop ()
      with Cyclic _ -> true
  in loop ()

(*******************************************************************)
(* \hd{Computation of target group} *)

(* \ic{%
   [gs_rev_iso_edges gs] returns the backwards edges induced by the
   isomorphisms and multilinear maps in [gs].
   Concretely, it returns a map [m] such that [m[j]] contains all [i]
   such that there is a $\phi : i \to j$ or $e : \ldots \times i \times \ldots \to j$.} *)
let gs_rev_edges gs =
  let m =
    L.fold_left (fun m i -> ss_add_set i.iso_codom i.iso_dom m) Ms.empty gs.gs_isos
  in
  L.fold_left
    (fun m e -> L.fold_left (fun m src -> ss_add_set e.em_codom src m) m e.em_dom)
    m
    gs.gs_emaps

(* \ic{Internal exception for [gs_find_target].} *)
exception TargetFound of group_id

(* \ic{%
   [gs_find_target gs] returns [Some(gid)] if elements from all groups
   can be moved to [gid] by applying isomorphisms and multilinear maps.
   For the multilinear maps, we assume that the adversary can get a handle
   to the group generator (polynomial $1$) in all groups.} *)
let gs_find_target gs =
  let rev_edges  = gs_rev_edges gs in
  let preds gid = try Ms.find gid rev_edges with Not_found -> Ss.empty in
  let all_gids = gs_group_ids gs in
  let reachable n =
    let visited = ref (Ss.singleton n) in
    let rec go n =
      if not (Ss.mem n !visited)
      then
        visited := Ss.add n !visited;
        Ss.iter go (preds n)
    in
    go n;
    if Ss.equal all_gids !visited then raise (TargetFound n)
  in
  try  Ss.iter (fun gid -> reachable gid) (gs_group_ids gs); None
  with TargetFound n -> Some n

(*******************************************************************)
(* \hd{Smart constructors for group settings and assumptions} *)


let closed_generic_group gid prime_num =
  { cgs_isos   = [];
    cgs_emaps  = [];
    cgs_prime_num = prime_num;
    cgs_gids   = Ss.singleton gid;
    cgs_target = gid }

let close_group_setting gs =
  if gs.gs_isos = [] && gs.gs_emaps = [] then
    fail_assm "No isomorphisms and no maps, use closed_generic_group.";
  if gs_is_cyclic gs then fail_assm "Group setting is cyclic.";
  match gs_find_target gs with
  | Some t -> 
    let gids = gs_group_ids gs in
    { cgs_isos   = gs.gs_isos;
      cgs_emaps  = gs.gs_emaps;
      cgs_prime_num = gs.gs_prime_num;
      cgs_gids   = gids;
      cgs_target = t }
  | None ->
    fail_assm "No target group"

let ensure_valid_groups cgs ges =
  if (List.exists (fun ge -> match ge.ge_group with 
                            | None -> fail_assm "polynomial without group"
                            | Some g -> not (Ss.mem g cgs.cgs_gids)
                  ) ges)
  then fail_assm "The problem contains elements in invalid group"

let standardize_ones cgs inp =
  (* let one = replicate RP.one cgs.cgs_prime_num in *)
  let inp = L.filter (fun ge -> not (RP.equal RP.one ge.ge_rpoly)) inp in
  let ones =
    L.map
      (fun gid -> { ge_group = Some gid; ge_rpoly = RP.one; ge_id = Param(0) })
      (Ss.elements cgs.cgs_gids |> L.sort compare)
  in
  ones @ inp


let check_duplicates_ids lst = 
  L.fold_left (fun acc f -> if (L.exists (fun g -> (extract_fid g.ge_id) = (extract_fid f.ge_id)) acc) then fail_assm "2 polynomials have same FID"
                            else f::acc) [] lst

let check_ids_format lst = 
  L.iter (fun g ->  if (extract_fid g.ge_id) < 0 then fail_assm "FID < 0 for a polynomial"
                    else if (not(RP.equal RP.one g.ge_rpoly)) && ((extract_fid g.ge_id) = 0) then fail_assm "Only an identity polynomial 1 can have FID 0"
         ) lst

(*Check if the list contains variables*)
let ensure_variables rpoly_list = 
  if (L.exists (fun rpoly -> not (RP.is_var rpoly.ge_rpoly)) rpoly_list)
  then fail_assm "Fixed or Unfixed set contains a polynomial"

let validate_input cgs trusted untrusted fixed unfixed zp = 
  (*Verify that the variable set fixed and unfixed contains variables and not polynomials*)
  ensure_variables (fixed@unfixed);
  (* Takes a poly and outputs list of variables in it *)
  let fixed_vars = RP.vars_of_list (L.map (fun g -> g.ge_rpoly) fixed) in
  let unfixed_vars = RP.vars_of_list (L.map (fun g -> g.ge_rpoly) unfixed) in 
  let zp_vars = RP.vars_of_list (L.map (fun g -> g.ge_rpoly) zp) in
  
  let vars_in_trusted = RP.vars_of_list (L.map (fun g -> g.ge_rpoly) trusted) in
  let vars_in_untrusted = RP.vars_of_list (L.map (fun g -> g.ge_rpoly) untrusted) in

  let vars = fixed_vars@unfixed_vars@zp_vars in
  let vars_in_polys = vars_in_trusted@vars_in_untrusted in

  if (L.exists (fun v -> not (L.mem v fixed_vars)) vars_in_trusted)  (*Check if any variable in trusted polys contains any non fixed variable*)
    then (fail_assm "A trusted polynomial contains a variable not in fixed set");
  if (L.exists (fun v -> not (L.mem v vars)) vars_in_polys)          (*Check if any variable in any polys contains any non fixed/unfixed variable*)
    then (fail_assm "A polynomial contains a variable not in fixed & unfixed sets ");
  
  check_duplicates_ids (trusted@untrusted);  (*check if any FID is repeated*)
  check_ids_format (trusted@untrusted);      (*check if 0 fid is used only for unit polynomials*)
  F.fprintf Format.std_formatter "\nAssigning FID 0 to every unit polynomial 1\n";

  let trusted  = standardize_ones cgs trusted in
  ensure_valid_groups cgs (trusted@untrusted);
  
  {ppe_cgs = cgs; ppe_fixed = fixed; ppe_trusted = trusted; ppe_untrusted = untrusted; ppe_zp = zp}
                                            (* Check that  *)
(*******************************************************************)
(* \hd{Commands in input language} *)

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

let empty_ias = {
  ia_gs = { gs_isos = []; gs_emaps = []; gs_prime_num = 1 };
  ia_trusted = [];
  ia_untrusted = [];
  ia_fixed = [];
  ia_unfixed = [];
  ia_zp = [];
}

let handle_cmd cmd ias =
  match cmd with
  | AddIsos isos ->
    { ias with
      ia_gs = { ias.ia_gs with
                gs_isos = ias.ia_gs.gs_isos @ isos } }
  | SetPrimeNum i ->
    { ias with ia_gs = { ias.ia_gs with gs_prime_num = i } }
  | AddMaps emaps ->
    { ias with
      ia_gs = { ias.ia_gs with
                gs_emaps = ias.ia_gs.gs_emaps @ emaps } }
  | AddTrusted ges  ->
    { ias with ia_trusted = ias.ia_trusted @ ges }
  | AddUntrusted ges ->
    { ias with ia_untrusted = ias.ia_untrusted @ ges }
  | AddFixed ges ->
    { ias with ia_fixed = ias.ia_fixed @ ges }
  | AddUnfixed ges ->
    { ias with ia_unfixed = ias.ia_unfixed @ ges }
  | AddZp ges -> 
    { ias with ia_zp = ias.ia_zp @ ges} 

let eval_cmds cmds =
  let ias = L.fold_left (fun ia cmd -> handle_cmd cmd ia) empty_ias cmds in
  let gs = ias.ia_gs in
  let cgs =
    if gs.gs_isos = [] && gs.gs_emaps = []
    then fail_assm "No pairing operations or isomorphisms given"
    else close_group_setting gs
  in
  validate_input cgs ias.ia_trusted ias.ia_untrusted ias.ia_fixed ias.ia_unfixed ias.ia_zp
  
(*i*)
(*******************************************************************)
(* \hd{Pretty printing} *)

let pp_iso fmt i = F.fprintf fmt "phi : %s -> %s" i.iso_dom i.iso_codom

let pp_emap fmt e =
  F.fprintf fmt "e : %a -> %s" (pp_list " * " pp_string) e.em_dom e.em_codom

let pp_iso_s fmt i = F.fprintf fmt "G%s,G%s" i.iso_dom i.iso_codom

let pp_emap_s fmt e =
  F.fprintf fmt "e_G%s" e.em_codom

let pp_group_id fmt gid =
  F.fprintf fmt "G_%s" (extract_group gid)

let pp_rp_vec fmt rps =
  match rps with
  | [rp] -> RP.pp fmt rp
  | _    -> F.fprintf fmt "(%a)" (pp_list ", " RP.pp) rps

let pp_group_elem fmt ge =
  F.fprintf fmt "%a : %a" RP.pp ge.ge_rpoly pp_group_id ge.ge_group

let pp_gs fmt gs =
  F.fprintf fmt "group setting:\n  %a\n  %a\n"
    (pp_list "\n  " pp_iso) gs.gs_isos
    (pp_list "\n  " pp_emap) gs.gs_emaps

let pp_cmd fmt cmd =
  match cmd with
  | SetPrimeNum i ->
    F.fprintf fmt "composite: %i.\n" i
  | AddIsos isos ->
    F.fprintf fmt "isos: %a.\n" (pp_list ", " pp_iso) isos
  | AddMaps emaps ->
    F.fprintf fmt "maps: %a.\n" (pp_list ", " pp_emap) emaps
  | AddFixed ges ->
    F.fprintf fmt "Fixed %a.\n" (pp_list ", " pp_group_elem) ges
  | AddUnfixed ges ->
    F.fprintf fmt "Unfixed %a.\n" (pp_list ", " pp_group_elem) ges
  | AddTrusted ges ->
    F.fprintf fmt "Trusted  %a.\n" (pp_list ", " pp_group_elem) ges
  | AddUntrusted ges ->
    F.fprintf fmt "Untrusted  %a.\n" (pp_list ", " pp_group_elem) ges
  | AddZp ges ->
    F.fprintf fmt "Zp %a.\n" (pp_list ", " pp_group_elem) ges
(*i*)

(*i*)
(*******************************************************************)
(* \hd{Internals for testing} *)

module Internals = struct
  let gs_is_cyclic = gs_is_cyclic
end
(*i*)

