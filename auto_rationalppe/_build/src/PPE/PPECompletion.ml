 (* This file is distributed under the MIT License (see LICENSE). *)

(*i*)
open Util
open LPoly
open PPEInput
(*i*)


(* let lmult_rp_vect gs rpss =
  L.fold_left
    (fun acc rps -> L.map (fun (f,g) -> RP.mult f g) (L.combine acc rps))
    RP.one
    rpss
 *)

let shape ges = L.map (fun ge -> (ge.ge_id, (extract_group ge.ge_group))) ges

(* let rec rp_equal r1 r2 = 
  match r1, r2 with
  | Param(i), Param (j) -> compare i j
  | Iso(iso1, c1), Iso(iso2, c2) when iso1 = iso2 -> rp_equal c1 c2
  | Emap(em1, cs1), Emap(em2, cs2) when (em1 = em2) && ((L.length cs1) = (L.length cs2)) -> not(L.exists2 (fun c1 c2 -> not(rp_equal c1 c2)) cs1 cs2)
  | Multiply(cs1), Multiply(cs2) when (L.length cs1) = (L.length cs2) -> not(L.exists2 (fun c1 c2 -> not(rp_equal c1 c2)) cs1 cs2)
  | Exp(c1, const1), Exp(c2, const2) when const1 = const2 -> rp_equal c1 c2
  | Expzp(f1, zp1), Expzp(f2, zp2) when RP.equal zp1 zp2 -> rp_equal f1 f2
  | _ -> -1
 *)
module IntMap = Map.Make(struct type t = int let compare = compare end)
(* module IntMap = Map.Make(struct type t = recipe let compare = rp_equal end) *)
let fid_map = ref IntMap.empty;;
let find_poly fid = try IntMap.find fid !fid_map with Not_found -> (F.fprintf Format.std_formatter "\nSomething wrong!!!!!!!!!!\n"; (RP.one, RP.one))


(* \ic{Apply a recipe to a list of inputs.} *)
let apply_recipe recip0 : (rpoly * rpoly) =
  let rec go recip : (rpoly * rpoly) =
    match recip with
    | Param i        -> find_poly i
                        (* let f = L.find (fun g -> extract_fid g.ge_id = i) inputs in 
                        f.ge_rpoly *)
    | Expzp (recip1, zp) -> 
        let (num, denom) = go recip1 in 
        (RP.mult num zp, denom)
    | Emap(_,recips) ->
      let rpss = L.map go recips in
      L.fold_left (fun (accnum, accdenom) (num, denom) -> (RP.mult accnum num), (RP.mult accdenom denom)) (RP.one, RP.one) rpss
(*       RP.lmult rpss *)
    | Iso(_,recip)   -> go recip
    | _ -> fail_assm "\nError! Unknown recipe\n";
  in
  go recip0

(* \ic{Recipe polynomials such as $W_1*W_2 + W_3$, Different recipes can correspond
   to the same recipe polynomial.} *)
module ReP = MakePoly(struct
  type t = int
  let pp = pp_int
  let equal = (=)
  let compare = compare
end) (IntRing)

(* \ic{[apply_completion_ops cops inputs] applies completion ops [cops] to [inputs].} *)
let apply_completion_ops cops cgid =
  let time = Unix.gettimeofday() in
  let output = L.map (fun cop -> let (num, denom) = apply_recipe cop in 
        {ge_rpoly = num; ge_rdenom = denom; ge_id = cop; ge_group = Some cgid}) cops in
  (* F.fprintf Format.std_formatter "\nTook %fs time to compute completion list polynomials from recipes" (Unix.gettimeofday() -. time); *)
  output

(* \ic{Sets of recipe polynomials. } *)
module Srep = Set.Make(struct type t = ReP.t let compare = ReP.compare end)

(* \ic{[srep_add_set k v m] adds [v] to the set stored under key [k] in [m].} *) 
let srep_add_set = add_set Srep.empty Srep.add

(* \ic{Map with pairs of group ids and recipe polynomials as keys.} *)
module Mrep = Map.Make(struct
  type t = group_id * ReP.t
  let compare (gid1,f1) (gid2,f2) =
    let d = compare gid1 gid2 in
    if d <> 0 then d else ReP.compare f1 f2
end)

(*******************************************************************)
(* \hd{Computation of completion operations} *)

(* \ic{[completion_ops gs cgid inp_type] computes a
   sufficient set of isomorphism and multilinear map
   applications with respect to the group setting [gs]
   and an input list with group ids [inp_gids]
   such that all computable elements in [cgid]
   can be computed by first applying these operations
   followed only by [add] and [neg].} *)
(* find_known contains the actual set of recipe polynomials for a given gid.
  find_recipe contains how the recipe polynomial is obtained given a gid and recipe polynomial *)
let completion_ops cgs cgid inp_gids =

  (* \ic{We keep a map from group ids to known recipe polynomials.} *)
  let m_known = ref Ms.empty in
  let find_known gid = try Ms.find gid !m_known with Not_found -> Srep.empty in

  (* \ic{We keep a map from known recipe polynomials to their recipes.} *)
  let m_recipes = ref Mrep.empty in
  let find_recipe gid rp = Mrep.find (gid,rp) !m_recipes in

  (* \ic{The [add] function adds a recipe polynomial if it is new.
     It uses the [changed] variable to track changes to [m_known].} *)
     (* The first argument rp is the polynomial like W1*W3 (recipe polynomial). Second argumnet recipe is the way we obtained it like Emap(W1, W3) *)
  let changed = ref false in
  let add (rp : ReP.t) (recipe : recipe) (gid : string) =
    let known = find_known gid in
    if Srep.mem rp known then ()
    else (
      changed := true;
      m_known := srep_add_set gid rp !m_known;
      m_recipes := Mrep.add (gid,rp) recipe !m_recipes
    )
  in

  (* \ic{ We first add all input polynomials $W_i$ with recipe $W_i$.
     For the first entries corresponding to $1$, we use the input polynomial $1$.} *)
  (* let first_non_one = Ss.cardinal cgs.cgs_gids in *)
  let var_counter = ref 1 in
  L.iter
    (fun (inprecipe,gid) -> add (ReP.var !var_counter) inprecipe gid; var_counter := !var_counter +1) inp_gids;
    (* (L.mapi (fun i gid -> (i,gid)) inp_gids); *)

  (* \ic{We then use the following loop for completion:} *)
  let rec complete () =
    changed := false;

    (* \ic{We loop over all $\phi: i \to i'$, for all
       $g \in$ [m_known[i]] with recipe $\zeta$, we add $g$ to
       [m_known[i']] with recipe $\phi(\zeta)$.} *)
    L.iter
      (fun i ->
         let gid, gid' = i.iso_dom, i.iso_codom in
         Srep.iter
           (fun rp -> add rp (Iso(i,find_recipe gid rp)) gid')
           (find_known gid))
      cgs.cgs_isos;

    (* \ic{We loop over all $e: i_1 \times \ldots \times i_k \to i'$,
       for all
       $(g_1,\ldots,g_k) \in$ [m_known[i_1]] $\times \ldots \times$ [m_known[i_k]]
       with recipe $(\zeta_1,\ldots,\zeta_k)$, we add $g_1 * \ldots * g_k$ to
       [m_known[i']] with recipe $e(\zeta_1,\ldots,\zeta_k)$.} *)
    L.iter
      (fun e ->
         let gids, gid' = e.em_dom, e.em_codom in
         let known_rps = L.map (fun gid -> Srep.elements (find_known gid)) gids in
         L.iter
           (fun rps ->
              let recips = L.map2 (fun gid rp -> find_recipe gid rp) gids rps in
              add (ReP.lmult rps) (Emap(e,recips)) gid')
           (cart_prod known_rps))
      cgs.cgs_emaps;
  
    (* \ic{If nothing changed, we return a list of recipes and group ids.
       Otherwise, we loop again.} *)
    if !changed then complete ()
    else L.map
           (fun rp -> find_recipe cgid rp)
           (Srep.elements (Ms.find cgid !m_known))
  in
  complete ()


let completion_ops2 cgs cgid inp_gids1 inp_gids2 =

  (* \ic{We keep a map from group ids to known recipe polynomials.} *)
  let m_known = ref Ms.empty in
  let m_known2 = ref Ms.empty in
  let find_known gid = try Ms.find gid !m_known with Not_found -> Srep.empty in
  let find_known2 gid = try Ms.find gid !m_known2 with Not_found -> Srep.empty in


  (* \ic{We keep a map from known recipe polynomials to their recipes.} *)
  let m_recipes = ref Mrep.empty in
  let m_recipes2 = ref Mrep.empty in
  let find_recipe gid rp = Mrep.find (gid,rp) !m_recipes in
  let find_recipe2 gid rp = Mrep.find (gid,rp) !m_recipes2 in

  (* \ic{The [add] function adds a recipe polynomial if it is new.
     It uses the [changed] variable to track changes to [m_known].} *)
  let changed = ref false in
  let add (rp : ReP.t) (recipe : recipe) (gid : string) =
    let known = find_known gid in
    if Srep.mem rp known then ()
    else (
      changed := true;
      m_known := srep_add_set gid rp !m_known;
      m_recipes := Mrep.add (gid,rp) recipe !m_recipes
    )
  in

  let add2 (rp : ReP.t) (recipe : recipe) (gid : string) =
    let known = find_known2 gid in
    if Srep.mem rp known then ()
    else (
      changed := true;
      m_known2 := srep_add_set gid rp !m_known2;
      m_recipes2 := Mrep.add (gid,rp) recipe !m_recipes2
    )
  in

  (* \ic{ We first add all input polynomials $W_i$ with recipe $W_i$.
     For the first entries corresponding to $1$, we use the input polynomial $1$.} *)
  (* let first_non_one = Ss.cardinal cgs.cgs_gids in *)
  let var_counter = ref 1 in
  L.iter
    (fun (inprecipe,gid) -> add (ReP.var !var_counter) inprecipe gid; var_counter := !var_counter + 1) inp_gids1;
  L.iter
    (fun (inprecipe,gid) -> add2 (ReP.var !var_counter) inprecipe gid; var_counter := !var_counter + 1) inp_gids2;
  (* F.fprintf Format.std_formatter "\nCardinals %d %d\n" (Mrep.cardinal !m_recipes) (Mrep.cardinal !m_recipes2); *)
    (* (L.mapi (fun i gid -> (i,gid)) inp_gids); *)

  (* \ic{We then use the following loop for completion:} *)
  (* let rec complete () =
    changed := false; *)

    (* \ic{We loop over all $\phi: i \to i'$, for all
       $g \in$ [m_known[i]] with recipe $\zeta$, we add $g$ to
       [m_known[i']] with recipe $\phi(\zeta)$.} *)
    L.iter
      (fun i ->
         let gid, gid' = i.iso_dom, i.iso_codom in
         Srep.iter
           (fun rp -> add rp (Iso(i,find_recipe gid rp)) gid')
           (find_known gid))
      cgs.cgs_isos;

    (* \ic{We loop over all $e: i_1 \times \ldots \times i_k \to i'$,
       for all
       $(g_1,\ldots,g_k) \in$ [m_known[i_1]] $\times \ldots \times$ [m_known[i_k]]
       with recipe $(\zeta_1,\ldots,\zeta_k)$, we add $g_1 * \ldots * g_k$ to
       [m_known[i']] with recipe $e(\zeta_1,\ldots,\zeta_k)$.} *)
    L.iter
      (fun e ->
         let gids, gid' = e.em_dom, e.em_codom in
         let known_rps = L.map (fun gid -> Srep.elements (find_known gid)) gids in
         L.iter
           (fun rps ->
              let recips = L.map2 (fun gid rp -> find_recipe gid rp) gids rps in
              add (ReP.lmult rps) (Emap(e,recips)) gid')
           (cart_prod known_rps))
      cgs.cgs_emaps;

    (* F.fprintf Format.std_formatter "\nFirst part done\n"; *)
    (* print_newline(); *)

    L.iter
      (fun i ->
         let gid, gid' = i.iso_dom, i.iso_codom in
         Srep.iter
           (fun rp -> add2 rp (Iso(i,find_recipe2 gid rp)) gid')
           (find_known2 gid))
      cgs.cgs_isos;


    L.iter
      (fun e ->
         let gids, gid' = e.em_dom, e.em_codom in
         let known_rps1 = L.map (fun gid -> Srep.elements (find_known gid)) gids in
         let known_rps2 = L.map (fun gid -> Srep.elements (find_known2 gid)) gids in
         (* F.fprintf Format.std_formatter "\ngid Length = %d %d %d %d \n" (L.length (L.nth known_rps1 1)) (L.length (L.nth known_rps1 0)) (L.length (L.nth known_rps2 1)) (L.length (L.nth known_rps2 0)); *)
         let tuples = (cart_prod2 known_rps1 known_rps2) in
         (* F.fprintf Format.std_formatter "\nLength = %d %d\n" (L.length tuples) (L.length (L.nth tuples 1)); *)
         L.iter
           (fun rps ->
              (* F.fprintf Format.std_formatter "\nLengths = %d %d\n" (L.length gids) (L.length rps); *)
              let m_recipes3 = Mrep.merge (fun key val1 val2 -> match val1, val2 with 
                                                                |Some x, None -> Some x
                                                                |None, Some x -> Some x
                                                                |_ -> fail_assm "Both maps have same recipe!") !m_recipes !m_recipes2 in
              let recips = L.map2 (fun gid rp -> Mrep.find (gid,rp) m_recipes3) gids rps in
              add (ReP.lmult rps) (Emap(e,recips)) gid'
           )
           tuples)
      cgs.cgs_emaps;  
    (* \ic{If nothing changed, we return a list of recipes and group ids.
       Otherwise, we loop again.} *)
    (* if !changed then complete () *)
    (* else  *)
    (* F.fprintf Format.std_formatter "\nFinished\n"; *)
    L.map
           (fun rp -> find_recipe cgid rp)
           (Srep.elements (Ms.find cgid !m_known))
(*   in
  complete () *)


let completion_for_group gs cgid (inputs : group_elem list) =
    (* F.fprintf Format.std_formatter "\ncompletion_for_group"; *)
  fid_map := IntMap.empty;
  (* L.iter (fun f -> fid_map := IntMap.add (extract_fid f.ge_id) f.ge_rpoly !fid_map;) inputs; *)
  L.iter (fun f ->  match f.ge_id with 
                    | Param(i) -> fid_map := IntMap.add i (f.ge_rpoly, f.ge_rdenom) !fid_map;
                    | _ -> () ) inputs;
  let time = Unix.gettimeofday() in
  let cops = completion_ops gs cgid (shape inputs) in
  (* F.fprintf Format.std_formatter "\nTook %fs time to compute recipes" (Unix.gettimeofday() -. time); *)
  (* print_newline(); *)
      (* F.fprintf Format.std_formatter "\ncompletion_for_group applying"; *)
  (apply_completion_ops cops cgid, cops)

let new_completion_for_group gs cgid inputs1 inputs2 = 
  (* F.fprintf Format.std_formatter "Doing alternate completion %d %d\n" (L.length inputs1) (L.length inputs2); *)
  (* L.iter (fun f -> F.fprintf Format.std_formatter "%a in G%s, " RP.pp f.ge_rpoly (extract_group f.ge_group);) inputs2; *)
  fid_map := IntMap.empty;
(*   L.iter (fun f -> fid_map := IntMap.add (extract_fid f.ge_id) f.ge_rpoly !fid_map;) inputs1;
  L.iter (fun f -> fid_map := IntMap.add (extract_fid f.ge_id) f.ge_rpoly !fid_map;) inputs2; *)
  L.iter (fun f ->  match f.ge_id with 
                    | Param(i) -> fid_map := IntMap.add i (f.ge_rpoly, f.ge_rdenom) !fid_map; 
                    | _ -> () ) (inputs1@inputs2);
  let time = Unix.gettimeofday() in
  let cops = completion_ops2 gs cgid (shape inputs1) (shape inputs2) in
  (* F.fprintf Format.std_formatter "\nTook %fs time to compute recipes" (Unix.gettimeofday() -. time); *)
  (* print_newline(); *)
  (apply_completion_ops cops cgid, cops)


(* let completions_for_group gs cgid linputs rinputs =
  assert (shape linputs = shape rinputs);
  let cops = completion_ops gs cgid (shape linputs) in
  ( apply_completion_ops cops linputs
  , apply_completion_ops cops rinputs
  , cops) 
*)

(*i*)
(*******************************************************************)
(* \hd{Pretty printing} *)

(* let rec pp_recipe fmt c =
  match c with
  | Param(i)     -> F.fprintf fmt "F%i" i
  | Iso(iso, c)  -> F.fprintf fmt "%a(%a)" pp_iso_s iso pp_recipe c
  | Emap(em, cs) -> F.fprintf fmt "%a(%a)" pp_emap_s em (pp_list "," pp_recipe) cs
 *)




(*i*)