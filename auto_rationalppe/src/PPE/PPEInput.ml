(* This file is distributed under the MIT License (see LICENSE). *)

(*s Input for non-parametric problems.\\ *)

(*i*)
open Util
open LPoly
(*i*)

(*******************************************************************)
(* \hd{Group settings, group elements, and assumptions (see .mli file for docs)} *)

let degree = ref 1;;
let fid_counter = ref 0;;


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
  | Expzp of recipe * rpoly
  | Identity 

type circuit = 
  | ACCEPT
  | REJECT
  | EMPTY
  | AND of circuit * circuit
  | OR of circuit * circuit
  | NOT of circuit 
  | PPE of recipe * recipe


type group_elem = {
  ge_id : recipe;
  ge_rpoly : rpoly;
  ge_rdenom : rpoly;
  ge_group : group_id option;
}

type ppe = {
  ppe_cgs : closed_group_setting;
  (* ppe_fixed : group_elem list; *)
  ppe_zp : group_elem list;
  (* ppe_unfixed : group_elem list; *)
  ppe_trusted : group_elem list;
  ppe_untrusted : group_elem list;
  completionGt : group_elem list;
  normcompletionGt : group_elem list;
  commondenom : rpoly;
}

let extract_fid fid = 
  match fid with 
  | Param(i) -> i
  | Iso(_,_) -> fail_assm "Invalid Iso"
  | Emap(_,_) -> fail_assm "Invalid emap"
  | Multiply(_) -> fail_assm "Invalid multiply"
  | Exp(_) -> fail_assm "Invalid exp"
  | Identity -> fail_assm "Invalid identity"
  | Expzp(_,_) -> fail_assm "Invalid Expzp"
  | _ -> fail_assm "Invalid FID!!!"

let extract_group ge = 
  match ge with 
  | None -> fail_assm "Extracting group of a poly without a group"
  | Some g -> g

(* let equal_rp_list a b =
  list_equal (fun f g -> RP.equal f g) a b *)

let equal_group_elem a b = a.ge_group = b.ge_group && RP.equal a.ge_rpoly b.ge_rpoly



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
  let inp = L.filter (fun ge -> not (RP.equal RP.one ge.ge_rpoly) or not (RP.equal RP.one ge.ge_rdenom) ) inp in
  let ones =
    L.map
      (fun gid -> { ge_group = Some gid; ge_rpoly = RP.one; ge_rdenom = RP.one; ge_id = Param(0) })
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

let validate_input cgs trusted untrusted zp = 
  (*Verify that the variable set fixed and unfixed contains variables and not polynomials*)
  (* ensure_variables (fixed@unfixed); *)
  (* Takes a poly and outputs list of variables in it *)
  (* let fixed_vars = RP.vars_of_list (L.map (fun g -> g.ge_rpoly) fixed) in
  let unfixed_vars = RP.vars_of_list (L.map (fun g -> g.ge_rpoly) unfixed) in 
  let zp_vars = RP.vars_of_list (L.map (fun g -> g.ge_rpoly) zp) in
  
  let vars_in_trusted = RP.vars_of_list (L.map (fun g -> g.ge_rpoly) trusted) in
  let vars_in_untrusted = RP.vars_of_list (L.map (fun g -> g.ge_rpoly) untrusted) in

  let vars = fixed_vars@unfixed_vars@zp_vars in
  let vars_in_polys = vars_in_trusted@vars_in_untrusted in
 *)
  (* if (L.exists (fun v -> not (L.mem v fixed_vars)) vars_in_trusted)  (*Check if any variable in trusted polys contains any non fixed variable*)
    then (fail_assm "A trusted polynomial contains a variable not in fixed set");
  if (L.exists (fun v -> not (L.mem v vars)) vars_in_polys)          (*Check if any variable in any polys contains any non fixed/unfixed variable*)
    then (fail_assm "A polynomial contains a variable not in fixed & unfixed sets ");
   *)
  check_duplicates_ids (trusted@untrusted);  (*check if any FID is repeated*)
  check_ids_format (trusted@untrusted);      (*check if 0 fid is used only for unit polynomials*)
  F.fprintf Format.std_formatter "\nAssigning FID 0 to every unit polynomial 1\n";

  let trusted  = standardize_ones cgs trusted in
  ensure_valid_groups cgs (trusted@untrusted);
  
  {ppe_cgs = cgs; ppe_trusted = trusted; ppe_untrusted = untrusted; ppe_zp = zp; completionGt = []; normcompletionGt = []; commondenom = RP.one}
                                            (* Check that  *)
(*******************************************************************)
(* \hd{Commands in input language} *)

type cmd =
  | AddIsos of iso list
  | AddMaps of emap list
  | SetPrimeNum of int
(*   | AddFixed of group_elem list
  | AddUnfixed of group_elem list *)
  | AddTrusted of group_elem list
  | AddUntrusted of group_elem list
  | AddZp of group_elem list

type incomp_assm = {
  ia_gs            : group_setting;
  ia_trusted       : group_elem list;
  ia_untrusted     : group_elem list;
(*   ia_fixed         : group_elem list;
  ia_unfixed       : group_elem list; *)
  ia_zp            : group_elem list;
}

let empty_ias = {
  ia_gs = { gs_isos = []; gs_emaps = []; gs_prime_num = 1 };
  ia_trusted = [];
  ia_untrusted = [];
(*   ia_fixed = [];
  ia_unfixed = []; *)
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
(*   | AddFixed ges ->
    { ias with ia_fixed = ias.ia_fixed @ ges }
  | AddUnfixed ges ->
    { ias with ia_unfixed = ias.ia_unfixed @ ges } *)
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
  validate_input cgs ias.ia_trusted ias.ia_untrusted ias.ia_zp
  (* validate_input cgs ias.ia_trusted ias.ia_untrusted ias.ia_fixed ias.ia_unfixed ias.ia_zp *)
  
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
  if RP.equal ge.ge_rdenom RP.one
  then F.fprintf fmt "%a : %a" RP.pp ge.ge_rpoly pp_group_id ge.ge_group
  else F.fprintf fmt "%a/%a : %a" RP.pp ge.ge_rpoly RP.pp ge.ge_rdenom pp_group_id ge.ge_group
  (* match ge.ge_rdenom with
  | RP.from_int 1 -> F.fprintf fmt "%a : %a" RP.pp ge.ge_rpoly pp_group_id ge.ge_group
  | _ -> F.fprintf fmt "%a/%a : %a" RP.pp ge.ge_rpoly RP.pp ge.ge_rdenom pp_group_id ge.ge_group
 *)
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
(*   | AddFixed ges ->
    F.fprintf fmt "Fixed %a.\n" (pp_list ", " pp_group_elem) ges
  | AddUnfixed ges ->
    F.fprintf fmt "Unfixed %a.\n" (pp_list ", " pp_group_elem) ges *)
  | AddTrusted ges ->
    F.fprintf fmt "Trusted  %a.\n" (pp_list ", " pp_group_elem) ges
  | AddUntrusted ges ->
    F.fprintf fmt "Untrusted  %a.\n" (pp_list ", " pp_group_elem) ges
  | AddZp ges ->
    F.fprintf fmt "Zp %a.\n" (pp_list ", " pp_group_elem) ges
(*i*)


let rec pp_recipe fmt c =
  match c with
  | Param(i)     -> F.fprintf fmt "F%i" i
  | Iso(iso, c)  -> F.fprintf fmt "Iso_%a(%a)" pp_iso_s iso pp_recipe c
  | Emap(em, cs) -> F.fprintf fmt "e(%a)" (pp_list "," pp_recipe) cs
  | Multiply(cs) -> F.fprintf fmt "%a" (pp_list "*" pp_recipe) cs
  | Exp(c, const) -> if const = 1 then 
                        F.fprintf fmt "%a" pp_recipe c
                    else 
                        F.fprintf fmt "(%a)^%d" pp_recipe c const
  | Expzp(f, zp) -> F.fprintf fmt "%a^%a" pp_recipe f RP.pp zp
  | Identity -> F.fprintf fmt "I"

let rec pp_fid fmt c = 
    match c with 
    | Param(i) -> F.fprintf fmt "F%i" i
    | Expzp(f, zp) -> F.fprintf fmt "%a^%a" pp_fid f RP.pp zp
    | _ -> fail_assm "Can only print ids with this function!"

let rec pp_recipes fmt rs = 
  let rs = L.map (fun f -> f.ge_id) rs in 
  F.fprintf fmt "%a" (pp_list "*" pp_recipe) rs

let rec pp_circuit fmt ckt = 
    match ckt with 
    | OR(ckt1,ckt2) -> 
        F.fprintf fmt "(%a OR %a)" pp_circuit ckt1 pp_circuit ckt2
   (*  | AND(ckt1, ckt2) -> 
        (match ckt2 with 
        | ACCEPT -> F.fprintf fmt "%a" pp_circuit ckt1
        | _ -> F.fprintf fmt "(%a AND %a)" pp_circuit ckt1 pp_circuit ckt2) *)
    | AND(ckt1, ckt2) ->  F.fprintf fmt "(%a AND %a)" pp_circuit ckt1 pp_circuit ckt2
    | NOT(ckt) -> 
        F.fprintf fmt "(NOT %a)" pp_circuit ckt
    | PPE(lhs, rhs) ->
        F.fprintf fmt "%a =  %a" pp_recipe lhs pp_recipe rhs
    | ACCEPT -> F.fprintf fmt "ACC"
    | REJECT -> F.fprintf fmt "REJ"
    | EMPTY -> F.fprintf fmt " "


(* val recipe_list_compare : recipe list -> recipe list -> int
 *)
let rec recipe_compare r1 r2 = 
    let rec recipe_list_compare rs1 rs2 =
        let cmp_list = L.map2 (fun r1 r2 -> recipe_compare r1 r2) rs1 rs2 in
        if L.exists (fun b -> b <> 0) cmp_list then L.find (fun b -> b <> 0) cmp_list else 0 in
    match r1, r2 with
    | Param(i), Param (j) -> compare i j
    | Iso(iso1, c1), Iso(iso2, c2) when iso1 = iso2 -> recipe_compare c1 c2
    | Emap(em1, cs1), Emap(em2, cs2) when (em1 = em2) && ((L.length cs1) = (L.length cs2)) -> recipe_list_compare cs1 cs2 
    | Multiply(cs1), Multiply(cs2) when (L.length cs1) = (L.length cs2) -> recipe_list_compare cs1 cs2 
    | Multiply(cs1), Multiply(cs2) -> compare (L.length cs1) (L.length cs2)
    (* not(L.exists2 (fun c1 c2 -> not(recipe_compare c1 c2)) cs1 cs2) *)
    | Exp(c1, const1), Exp(c2, const2) when const1 = const2 -> recipe_compare c1 c2
    | Exp(c1, const1), Exp(c2, const2) -> compare const1 const2
    | Expzp(f1, zp1), Expzp(f2, zp2) when RP.equal zp1 zp2 -> recipe_compare f1 f2
    | Expzp(f1, zp1), Expzp(f2, zp2) -> RP.compare zp1 zp2
    | Identity, Identity -> 0
    
(*     | Param(_), Iso(_,_) -> 1
    | Param(_), Emap(_,_) -> 1
    | Param(_), Multiply(_) -> 1
    | Param(_), Exp(_,_) -> 1
    | Param(_), Expzp(_,_) -> 1
    | Param(_), Identity -> 1 *)

    | Param(_), _ -> 1

    | Iso(_,_), Param(_) -> -1
    | Iso(_,_), _ -> 1

    | Emap(_,_), Param(_) -> -1
    | Emap(_,_), Iso(_,_) -> -1
    | Emap(_,_), _ -> 1

    | Multiply(_), Param(_) -> -1
    | Multiply(_), Iso(_,_) -> -1
    | Multiply(_), Emap(_,_) -> -1
    | Multiply(_), _ -> 1

    | Exp(_,_), Param(_) -> -1
    | Exp(_,_), Iso(_,_) -> -1
    | Exp(_,_), Emap(_,_) -> -1
    | Exp(_,_), Multiply(_) -> -1
    | Exp(_,_), _ -> 1

    | Expzp(_,_), Param(_) -> -1
    | Expzp(_,_), Iso(_,_) -> -1
    | Expzp(_,_), Emap(_,_) -> -1
    | Expzp(_,_), Multiply(_) -> -1
    | Expzp(_,_), Exp(_,_) -> -1
    | Expzp(_,_), _ -> 1

    | Identity, _ -> -1    
 (*    
    | Iso(_,_), _ -> 1
    | Emap(_,_), _ -> 1
    | Multiply(_), _ -> 1
    | Exp(_,_), _ -> 1
    | Expzp(_,_), _ -> 1
    | _, Identity -> 1
  *)| _, _ -> -1






let gate_compare (input1, input2, gate1) (input3, input4, gate2) = 
    (* F.fprintf Format.std_formatter "\nComparing %d %d %d, %d %d %d" input1 input2 gate1 input3 input4 gate2;  *)
    if compare gate1 gate2 != 0 then
    (
        (* F.fprintf Format.std_formatter "\nGate comparison %d" (compare gate1 gate2); *)
        compare gate1 gate2
    )
    else if gate1 = 3 then
    (
        (* F.fprintf Format.std_formatter "\nNOT gate comparison %d" (compare input1 input3); *)
        compare input1 input3 
    )
    else
        if compare input1 input3 != 0 then
        (
            if (compare input1 input4 = 0) && (compare input2 input3 = 0) then
                0
            else 
                compare input1 input3
        )
        else
            compare input2 input4
 (*        let y = compare input2 input4 in
        if x <> 0 then x
        else if y <> 0 then y
        else if z <> 0 then z
        else 0
  *)   
  (* if (input1 = input3) && (input2 = input4) && (gate1 = gate2) then 0 else 1 *)

let ppe_compare (lhs1, rhs1) (lhs2, rhs2) = 
    let x = recipe_compare lhs1 lhs2 in
    if x != 0 then
        x
    else
        recipe_compare rhs1 rhs2

module CktMap = Map.Make(struct type t = int * int * int let compare = gate_compare end)   (*It maps input_wire_id * input_wire_id * gate -> output_wire_id *) 
module PPEMap = Map.Make(struct type t = recipe * recipe let compare = ppe_compare  end)   (*It maps input_wire_id * input_wire_id * gate -> output_wire_id *) 

let ppe_count = ref 0;;
let gate_count = ref 0;;
let ckt_hash_table = ref CktMap.empty;;
let ppe_hash_table = ref PPEMap.empty;;

(*
(* OR Gate = 1,  AND gate = 2,  NOT gate = 3, ACC = 0*)
let rec opt_pp_circuit fmt ckt = 
    match ckt with 
    | OR(ckt1,ckt2) -> 
        let input1 = opt_pp_circuit fmt ckt1 in 
        let input2 = opt_pp_circuit fmt ckt2 in 
        if (input1 = 0) || (input2 = 0) then (*One of the circuits evaluate to ACC *)
            0
        else
            let gate = 1 in 
            (* F.fprintf Format.std_formatter "\nFinding %d %d %d" input1 input2 gate; *)
            let output = try CktMap.find (input1, input2, gate) !ckt_hash_table with Not_found -> -1 in
            if output = -1 then 
            (
                (* F.fprintf Format.std_formatter "\nInserting %d %d %d" input1 input2 gate; *)
                gate_count := !gate_count + 1;
                ckt_hash_table := CktMap.add (input1, input2, gate) (!gate_count) !ckt_hash_table;
                F.fprintf fmt "\nP%d : P%d OR P%d" !gate_count input1 input2;
                !gate_count
            )
            else
                output
    | AND(ckt1, ckt2) -> 
        let input1 = opt_pp_circuit fmt ckt1 in 
        let input2 = opt_pp_circuit fmt ckt2 in 
        if (input1 = 0) then
            input2
        else if (input2 = 0) then
            input1 
        else
            let gate = 2 in 
            (* F.fprintf Format.std_formatter "\nFinding %d %d %d" input1 input2 gate; *)
            let output = try CktMap.find (input1, input2, gate) !ckt_hash_table with Not_found -> -1 in
            if output = -1 then 
            (
                (* F.fprintf Format.std_formatter "\nInserting %d %d %d" input1 input2 gate; *)
                gate_count := !gate_count + 1;
                ckt_hash_table := CktMap.add (input1, input2, gate) (!gate_count) !ckt_hash_table;
                F.fprintf fmt "\nP%d : P%d AND P%d" !gate_count input1 input2;
                !gate_count
            )
            else
                output
    | NOT(ckt) -> 
        let input1 = opt_pp_circuit fmt ckt in 
        let input2 = 0 in 
        let gate = 3 in 
        (* F.fprintf Format.std_formatter "\nFinding %d %d %d" input1 input2 gate; *)
        let output = try CktMap.find (input1, input2, gate) !ckt_hash_table with Not_found -> -1 in
        if output = -1 then
        (
            (* F.fprintf Format.std_formatter "\nInserting %d %d %d" input1 input2 gate; *)
            gate_count := !gate_count + 1;
            ckt_hash_table := CktMap.add (input1, input2, gate) (!gate_count) !ckt_hash_table;   
            F.fprintf fmt "\nP%d : NOT P%d" !gate_count input1;
            !gate_count
        )
        else
            output
    | ACCEPT -> 0
    | EMPTY -> -1
    | PPE(lhs, rhs) ->
        try PPEMap.find (lhs, rhs) !ppe_hash_table with Not_found -> (F.fprintf Format.std_formatter "\nPPE Not found %a = %a" pp_recipe lhs pp_recipe rhs; -1)
*)

let pp_ppe fmt (lhs, rhs) = 
    F.fprintf fmt "%a = %a" pp_recipe lhs pp_recipe rhs

let rec print_ppe_map fmt ppes = 
    PPEMap.iter (fun (lhs, rhs) x -> F.fprintf fmt " %a = %a   (%s), " pp_recipe lhs pp_recipe rhs x) ppes

(*Outputs true if ppes_only_in_ckt1 has (ppe, no) and ppes_only_in_ckt2 has (ppe, yes) or viceversa*)
let is_trivially_true ppes_only_in_ckt1 ppes_only_in_ckt2 = 
    let different = PPEMap.exists (fun ppe x -> not (PPEMap.mem ppe ppes_only_in_ckt2)) ppes_only_in_ckt1 in
    let different = different || PPEMap.exists (fun ppe x -> not (PPEMap.mem ppe ppes_only_in_ckt1)) ppes_only_in_ckt2 in 
    (*the flag different is true if the set of ppes in ppes_only_in_ckt2 and ppes_only_in_ckt1 are different*)
    
    if (not different) && (PPEMap.cardinal ppes_only_in_ckt1) = 1 && (PPEMap.cardinal ppes_only_in_ckt2) = 1 then
        let common = ref false in 
        let contradicting = ref false in (*represents if there is a poly with "yes" in ppes_including_ckt1 and "no" in ppes_including_ckt2 or vice-versa*)    
        PPEMap.iter (fun ppe1 x -> let y = PPEMap.find ppe1 ppes_only_in_ckt2 in
                                            if ((x = "yes" && y = "no") || (x = "no" && y = "yes")) then (contradicting := true;) 
                                            else if ((x = "yes" && y = "yes") || (x = "no" && y = "no")) then (common := true;)
                            ) ppes_only_in_ckt1;
        if !contradicting && (not !common) then
        (
            (* F.fprintf Format.std_formatter "  \nOR evaluates to true: %a  :::: %a "  print_ppe_map ppes_only_in_ckt1 print_ppe_map ppes_only_in_ckt2;  *)
            true
        )
        else
            false
    else
        false 

(* OR Gate = 1,  AND gate = 2,  NOT gate = 3, ACC = 0*)
(*here current_ppes is a map between PPES to {-1,1}. 
If a ppe is mapped to 1, it means that the overal circuit is of the form (ppe and ... and ckt). Otherwise, the overall circuit is of the form (not ppe and ... ckt)*)
(*  On circuit  x and ( (not x and c1) or (x and c2)) 
 oututs   x and c2
*)
let rec opt_pp_circuit fmt ckt current_ppes = 
    (* F.fprintf Format.std_formatter "\nopt_pp_circuit: \ncurrent_ppes %a \ncircuit: %a" print_ppe_map current_ppes pp_circuit ckt;  *)

    match ckt with 
    | OR(ckt1,ckt2) -> 
        let (input1, ppes_including_ckt1) = opt_pp_circuit fmt ckt1 current_ppes in 
        let (input2, ppes_including_ckt2) = opt_pp_circuit fmt ckt2 current_ppes in 
        if (input1 = 0) || (input2 = 0) then (*One of the circuits evaluate to ACC *)
            (0, current_ppes)
        else if (input1 = -1) then
            (input2, ppes_including_ckt2)
        else if (input2 = -1) then
            (input1, ppes_including_ckt1)
        else
            let ppes_only_in_ckt1 = PPEMap.filter ( fun ppe1 x -> not (PPEMap.exists (fun curppe y -> if ppe_compare ppe1 curppe = 0 
                                                                                            then true
                                                                                          else false 
                                                                         ) current_ppes) 
                                            ) ppes_including_ckt1 in 
            let ppes_only_in_ckt2 = PPEMap.filter ( fun ppe1 x -> not (PPEMap.exists (fun curppe y -> if ppe_compare ppe1 curppe = 0 
                                                                                            then true
                                                                                          else false 
                                                                         ) current_ppes) 
                                            ) ppes_including_ckt2 in 

            (* let different = ref false in    *)
            

            if is_trivially_true ppes_only_in_ckt1 ppes_only_in_ckt2 then (*Both ppes_only_in_ckt1 and ppes_only_in_ckt2 have same set of ppes *) (*Every ppe in ppes_only_in ckt1 and ppes_only_in ckt2 are associated with different literal*)
                    (0, current_ppes)
            else 
                let gate = 1 in 
                (* F.fprintf Format.std_formatter "\nFinding %d %d %d" input1 input2 gate; *)
                let output = try CktMap.find (input1, input2, gate) !ckt_hash_table with Not_found -> -1 in
                if output = -1 then 
                (
                    (* F.fprintf Format.std_formatter "\nInserting %d %d %d" input1 input2 gate; *)
                    gate_count := !gate_count + 1;
                    ckt_hash_table := CktMap.add (input1, input2, gate) (!gate_count) !ckt_hash_table;
                    F.fprintf fmt "\nG%d : G%d OR G%d" !gate_count input1 input2;
                    (!gate_count, current_ppes)
                )
                else
                    (output, current_ppes)



    | AND(ckt1, ckt2) -> 
        let (input1, ppes_including_ckt1) = opt_pp_circuit fmt ckt1 current_ppes in 
        if (input1 = -1) then       (*If ckt1 evaluates to rej*)
            (-1, current_ppes)
        else
            let (input2, ppes_including_ckt2) = if (input1 = 0) then  opt_pp_circuit fmt ckt2 current_ppes   (*If input1 evaluates to acc*) 
                                                else opt_pp_circuit fmt ckt2 ppes_including_ckt1     (*If input1 does not evaluate to acc*)
                                            in 
            if (input2 = -1) then   (*one of the circuits evaluates to 0*)
                (-1, current_ppes)
            else if (input1 = 0) then    (*ckt1 evaluates to 1*)
                (input2, ppes_including_ckt2)
            else if (input2 = 0) then
                (input1, ppes_including_ckt1)
            else
                let gate = 2 in 
                (* F.fprintf Format.std_formatter "\nFinding %d %d %d" input1 input2 gate; *)
                let output = try CktMap.find (input1, input2, gate) !ckt_hash_table with Not_found -> -1 in
                if output = -1 then 
                (
                    (* F.fprintf Format.std_formatter "\nInserting %d %d %d" input1 input2 gate; *)
                    gate_count := !gate_count + 1;
                    ckt_hash_table := CktMap.add (input1, input2, gate) (!gate_count) !ckt_hash_table;
                    F.fprintf fmt "\nG%d : G%d AND G%d" !gate_count input1 input2;
                    (!gate_count, ppes_including_ckt2)
                )
                else
                    (output, ppes_including_ckt2)
    | NOT(ckt1) -> 
        let (input1, ppes_including_ckt) = opt_pp_circuit fmt ckt1 current_ppes in 
        let input2 = 0 in 
        let gate = 3 in 
        if input1 = -1 then (0, current_ppes)  (*if ckt evaluates to 0, then output acc*)
        else if input1 = 0 then (-1, current_ppes) (*if ckt evaluates to acc, then output rej*)
        (* F.fprintf Format.std_formatter "\nFinding %d %d %d" input1 input2 gate; *)
        else
        (
            let final_ppes = ref ppes_including_ckt in
            PPEMap.iter (fun ppe x -> let dummy = try PPEMap.find ppe current_ppes with Not_found ->
                                     ( 
                                        (* let x = try PPEMap.find ppe !final_ppes with Not_found -> (fail_assm "PPE not found when printing NOT gate"; -2) in *)
                                        if x = "yes" then
                                            (final_ppes := PPEMap.add ppe "no" !final_ppes; "something")
                                        else
                                            (final_ppes := PPEMap.add ppe "yes" !final_ppes; "something")      
                                    ) in 
                                    ()
                        )
                                     ppes_including_ckt; (*for each ppe added during call for ckt1, replace 1 with -1, and vice versa*)
            let output = try CktMap.find (input1, input2, gate) !ckt_hash_table with Not_found -> -1 in
            if output = -1 then
            (
                (* F.fprintf Format.std_formatter "\nInserting %d %d %d" input1 input2 gate; *)
                gate_count := !gate_count + 1;
                ckt_hash_table := CktMap.add (input1, input2, gate) (!gate_count) !ckt_hash_table;   
                F.fprintf fmt "\nG%d : NOT G%d" !gate_count input1;
                (!gate_count, !final_ppes)
            )
            else
                (output, !final_ppes)
        )
    | ACCEPT -> (0, current_ppes)
    | EMPTY -> (-1, current_ppes)
    | PPE(lhs, rhs) -> 
        let ppe = try PPEMap.find (lhs, rhs) !ppe_hash_table with Not_found -> (F.fprintf Format.std_formatter "\nPPE Not found %a = %a" pp_recipe lhs pp_recipe rhs; -1) in
        let flag = try PPEMap.find (lhs, rhs) current_ppes with Not_found -> "notfound" in
        if flag = "yes" then (0, current_ppes)
        else if flag = "no" then (-1, current_ppes)
        else (ppe, PPEMap.add (lhs, rhs) "yes" current_ppes)




let rec print_ppes ckt = 
    match ckt with 
    | OR(ckt1,ckt2) -> 
        print_ppes ckt1; 
        print_ppes ckt2
    | AND(ckt1, ckt2) -> 
        print_ppes ckt1; 
        print_ppes ckt2
    | NOT(ckt) -> 
        print_ppes ckt 
    | PPE(lhs, rhs) ->
        let output = try PPEMap.find (lhs, rhs) !ppe_hash_table with Not_found -> -1 in
        if output = -1 then
        (
            ppe_count := !ppe_count + 1; 
            ppe_hash_table := PPEMap.add (lhs, rhs) !ppe_count !ppe_hash_table;
            F.fprintf Format.std_formatter "\nG%d : %a = %a" !ppe_count pp_recipe lhs pp_recipe rhs;
        )
    | ACCEPT -> ( )
    | REJECT -> ( )
    | EMPTY -> ( )

let optimize_pp_circuit fmt ckt = 
    ckt_hash_table := CktMap.empty; 
    ppe_hash_table := PPEMap.empty; 
    print_ppes ckt; 
    gate_count := !ppe_count; 
    opt_pp_circuit fmt ckt PPEMap.empty;
    (* F.fprintf Format.std_formatter "-------------------!!!!!!!!!!!!!!!\n"; *)
    ()
    
(*     let count = try MonMap.find mon !mons_map_lst1 with Not_found -> 0 in
    mons_map_lst1 := MonMap.add mon (count+1) !mons_map_lst1;
 *)
(*i*)
(*******************************************************************)
(* \hd{Internals for testing} *)

module Internals = struct
  let gs_is_cyclic = gs_is_cyclic
end
(*i*)

