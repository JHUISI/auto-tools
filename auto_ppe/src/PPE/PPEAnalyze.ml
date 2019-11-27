(* This file is distributed under the MIT License (see LICENSE). *)

(*i*)
open Util
open PPEInput
open PPECompletion
(* open LPoly *)


module S = String
let ppes = ref ([]:string list);; 
let ppe = ref "";;
let optimized_ppe = ref "";;
let optimized_ppes = ref ([]:string list);;
let degree = ref 1;;
let fid_counter = ref 0;;
let trusted = ref([]:group_elem list);;
let untrusted = ref([]:group_elem list);;
let fixed = ref([]:group_elem list);;
let zp = ref([]:group_elem list);;
let to_compute_completion = ref([]:group_elem list);;
let computed_completion = ref([]:group_elem list);;
let completionGt = ref([]:group_elem list);;

(*******************************************************************)
(* \hd{Analysis functions} *)

(* \ic{[get_vector_repr pss] returns the list of vector representations of
    of the lists polynomials [pss] with respect to the set of monomials occuring in [pss].
    It also returns the computed monomial basis.} *)
let get_vector_repr pss =
  let mbasis =
    conc_map (fun ps -> RP.mons ps.ge_rpoly) pss |>
      sorted_nub compare
  in
  let vps = L.map (fun ps -> (rp_to_vector mbasis) ps.ge_rpoly) pss in
  (mbasis, vps)

let pp_coeff_vector v = 
  L.iter (fun c -> F.fprintf Format.std_formatter "%a, " RP.pp_coeff c) v

let pp_coeff_matrix m = 
  L.iter (fun v -> (pp_coeff_vector v; F.fprintf Format.std_formatter "\n")) m

let pp_int_vector v = 
  L.iter (fun c -> F.fprintf Format.std_formatter "%d, " c) v

let pp_int_matrix m = 
  L.iter (fun v -> (pp_int_vector v; F.fprintf Format.std_formatter "\n")) m

let remove p lst = 
  L.filter (fun ele -> not (ele.ge_group = p.ge_group && RP.equal ele.ge_rpoly p.ge_rpoly)) lst

let rec repeat_vector element length = 
  if length = 1 then [element]
  else element::(repeat_vector element (length-1))

let remove_duplicates lst = 
  L.fold_left (fun acc f -> if (L.exists (fun g -> (RP.equal f.ge_rpoly g.ge_rpoly) && (f.ge_group = g.ge_group)) acc) then acc
                              else f::acc) [] lst
let add_non_duplicates lst1 lst2 = 
  L.fold_left (fun acc f -> if (L.exists (fun g -> (RP.equal f.ge_rpoly g.ge_rpoly) && (f.ge_group = g.ge_group)) acc) then acc
                              else f::acc) lst2 lst1

let multiply_zp poly zp = 
  assert (!degree >= 1);
  if (L.length zp) = 0 then []
  else if (!degree = 1) then 
  (
    let output = L.fold_left (fun acc p -> acc@[{ge_rpoly = (RP.mult p.ge_rpoly poly.ge_rpoly); ge_group = poly.ge_group; ge_id = Param(-1)}]) [] zp in
    let output = L.map (fun f -> fid_counter := !fid_counter+1; {f with ge_id = Param(!fid_counter-1)}) output in 
    output
  )
  else
  ( 
    (* F.fprintf Format.std_formatter "\nMultiplying %a with list " RP.pp poly.ge_rpoly; *)
    L.iter (fun f -> F.fprintf Format.std_formatter " %a, " RP.pp f.ge_rpoly) zp; 
    let rec mul l1 l2 num = (*multiply every element of l1 with every element in l2*)
      let l3 = L.fold_left (fun acc p -> acc@(L.map (fun a -> {ge_rpoly = (RP.mult p.ge_rpoly a.ge_rpoly); ge_group = poly.ge_group; ge_id = Param(-1)}) l1)) [] l2 in
      if num > 1 then l3@(mul l3 l2 (num-1))
      else l1@l3
    in
    let output = (mul [poly] zp !degree) in
    let output = remove_duplicates output in
    let output = L.map (fun f -> fid_counter := !fid_counter+1; {f with ge_id = Param(!fid_counter-1)}) output in 
    (* F.fprintf Format.std_formatter "\n Resultant output ";
    L.iter (fun f -> F.fprintf Format.std_formatter " F%d = %a, " (extract_fid f.ge_id) RP.pp f.ge_rpoly) output;*)
    output
  )

let get_1 (a,_) = a
let get_2 (_,a) = a

(*filter polynomials in lst2 that contains only monomials present in polynomials of lst1*)
let optimize1 lst1 lst2 : group_elem list=
  let mons = ref ([]:RP.monom list) in
  let new_mons = ref (conc_map (fun ps -> RP.mons ps.ge_rpoly) lst1) in
  let lst = ref (L.map (fun f -> ref (false, f)) lst2) in
  let htbl = Hashtbl.create 400000 in
  L.iter (fun element -> L.iter (fun (mon, _) -> Hashtbl.add htbl (RP.get_key mon) element) (get_2 !element).ge_rpoly ) !lst;

  let rec go a : group_elem list = 
    let time = Unix.gettimeofday() in
    mons := sorted_nub RP.mon_compare (!new_mons@(!mons));
    (* F.fprintf Format.std_formatter "\nTook %fs time to sort mons" (Unix.gettimeofday() -. time); print_newline(); *)

    (*Set polys containing new_mons to true*)
    let new_polys = ref ([]:group_elem list) in
    let time = Unix.gettimeofday() in
    L.iter (fun mon -> let vector = Hashtbl.find_all htbl (RP.get_key mon) in
                             L.iter (fun element -> 
                                                   if (get_1 !element) then (new_polys := !new_polys;)
                                                   else if RP.is_non_zero_coeff_in_sorted_poly (get_2 !element).ge_rpoly mon then 
                                                   (
                                                      new_polys := (get_2 !element)::(!new_polys);
                                                      element := (true, get_2 !element);
                                                   )
                                   ) vector;
            ) !new_mons;
    
    (* lst := L.map (fun (bit, f) -> if bit then (true, f) 
                                  else if (L.exists (fun mon -> RP.is_non_zero_coeff_in_sorted_poly f.ge_rpoly mon) !new_mons) then
                                  (
                                    new_polys := f::!new_polys;
                                    (true, f)
                                  )
                                  else (false, f)
                 ) !lst; *)
    (* F.fprintf Format.std_formatter "\nTook %fs time to compute %d new_polys using %d new_mons" (Unix.gettimeofday() -. time) (L.length !new_polys) (L.length !new_mons); print_newline(); *)
    (*extract monomials from new_polys*)
    let time = Unix.gettimeofday() in
    new_mons := (conc_map (fun ps -> RP.mons ps.ge_rpoly) !new_polys);
    (*filter new_mons that are not already present in mons*)
    new_mons := L.fold_left (fun acc mon -> if (RP.mon_exists !mons mon) then acc
                              else mon::acc) [] !new_mons;
    (* F.fprintf Format.std_formatter "\nTook %fs time to compute %d new_mons from %d new_polys" (Unix.gettimeofday() -. time) (L.length !new_mons) (L.length !new_polys); print_newline(); *)

    if (L.length !new_mons) <> 0 then
      (go 1)
    else
      (L.filter (fun element -> get_1 !element) !lst)
      |> L.map (fun element -> get_2 !element)
  in
  go 1

module MonMap = Map.Make(struct type t = RP.monom let compare = RP.mon_compare end)
  
(*For each monomial that occurs in lst, maintain a count on number of polynomials it occurs in. 
If a monomial occurs in only one polynomial and the monomial is not present in lst2, then remove the corresponding polynomial from lst1*)
let optimize2 lst1 lst2 : group_elem list = 
  let mons = ref ([]:RP.monom list) in
  let mons_map_lst1 = ref MonMap.empty in
  let add_in_lst1 mon = 
    let count = try MonMap.find mon !mons_map_lst1 with Not_found -> 0 in
    mons_map_lst1 := MonMap.add mon (count+1) !mons_map_lst1;
  in
  let time = Unix.gettimeofday() in
  L.iter (fun ps -> L.iter (fun mon -> add_in_lst1 mon) (RP.mons ps.ge_rpoly);) lst1;
  (* F.fprintf Format.std_formatter "\nTook %fs time to create map of lst1 " (Unix.gettimeofday() -. time); print_newline(); *)

  let time = Unix.gettimeofday() in
  let mons_in_lst2 = ref (conc_map (fun ps -> RP.mons ps.ge_rpoly) lst2 |> sorted_nub RP.mon_compare) in
  (* F.fprintf Format.std_formatter "\nTook %fs time to compute mons in lst2" (Unix.gettimeofday() -. time); print_newline(); *)

  let mons_in_lst1 = ref ([]:RP.monom list) in
  (* F.fprintf Format.std_formatter "\nMonomials with lst1 = %d" (MonMap.cardinal !mons_map_lst1); *)
  (*mons_in_lst1 that has a count of 1 and do not occur in mons_in_lst2*)
  let time = Unix.gettimeofday() in
  mons_map_lst1 := MonMap.filter (fun mon count -> if (count <> 1) then false
                                                      else if RP.mon_exists !mons_in_lst2 mon then false
                                                      else (mons_in_lst1 := mon::!mons_in_lst1; true)) !mons_map_lst1;
  (* F.fprintf Format.std_formatter "\nTook %fs time to filter %d mons in lst1" (Unix.gettimeofday() -. time) (L.length !mons_in_lst1); print_newline(); *)
  (* F.fprintf Format.std_formatter "\nRemoving %d monomials" (L.length !mons_in_lst1); *)
  let time = Unix.gettimeofday() in
  let output = L.filter (fun f -> not(L.exists (fun mon -> RP.is_non_zero_coeff_in_sorted_poly f.ge_rpoly mon) !mons_in_lst1)) lst1 in 
  (* F.fprintf Format.std_formatter "\nTook %fs time to filter corresponding polynomials in lst1" (Unix.gettimeofday() -. time); print_newline(); *)
  (* F.fprintf Format.std_formatter "\nReduced number of polynomials in f.(completion of G1) from %d to %d" (L.length lst1) (L.length output); *)
  output

(*This algorithm takes 2 lists of polynomials as input.
We want to express polynomails in lst2 in terms of polynomials in lst1
This functio removes some polynomials in lst1 which trivially have zero coefficient.
Iterate over optimize1 and optimize2 algorithm until no more changes occur*)
let optimize lst1 lst2 = 
  let time = Unix.gettimeofday() in
  let lst1 = L.map (fun f -> {f with ge_rpoly = RP.sort_based_on_monomials f.ge_rpoly}) lst1 in
  let lst2 = L.map (fun f -> {f with ge_rpoly = RP.sort_based_on_monomials f.ge_rpoly}) lst2 in
  (* F.fprintf Format.std_formatter "\n       Took %fs seconds to sort." (Unix.gettimeofday() -. time); *)
  let lst11 = ref lst1 in
  let lst22 = ref lst2 in
  let cnt = ref 1 in

  let rec go a =
    F.fprintf Format.std_formatter "\nOptimization round %d" !cnt;
    cnt := !cnt + 1;
    let l1 = (L.length !lst11) in
    let l2 = (L.length !lst22) in

    let time = Unix.gettimeofday() in
    lst22 := optimize1 !lst11 !lst22;
    (* F.fprintf Format.std_formatter "\nReduced the polynomials in completion of GT from %d to %d" l2 (L.length !lst22); *)
    (* F.fprintf Format.std_formatter "\n       Took %fs seconds." (Unix.gettimeofday() -. time); *)

    let time = Unix.gettimeofday() in 
    lst11 := optimize2 !lst11 !lst22;
    (* F.fprintf Format.std_formatter "\nReduced number of polynomials in f.(completion of G1) from %d to %d" l1 (L.length !lst11); *)
    (* F.fprintf Format.std_formatter "\n       Took %fs seconds." (Unix.gettimeofday() -. time); *)
    print_newline();

    if ((L.length !lst11) = l1) && ((L.length !lst22) = l2) then
      (!lst11,!lst22)
    else
      go 1
  in
  go 1

let add_to_trusted cgs untrusted_poly = 
  trusted := untrusted_poly::!trusted;
  if (extract_group untrusted_poly.ge_group) = cgs.cgs_target then
  (
    completionGt := untrusted_poly::!completionGt;
    computed_completion := untrusted_poly::!computed_completion;
  )
  else
  (
    to_compute_completion := untrusted_poly::!to_compute_completion;
  );;

let update_completion_list cgs =
(*   let (completionlist,_) = completion_for_group cgs cgs.cgs_target !trusted in
  completionGt := completionlist;; *)
  if L.length (!to_compute_completion) <> 0 then
  (
    if L.length !computed_completion <> 0 then
    (
      let (completionlist,_) = (new_completion_for_group cgs cgs.cgs_target !to_compute_completion !computed_completion) in
      completionGt := add_non_duplicates completionlist !completionGt
    )
    else
    (
      let (completionlist,_) = completion_for_group cgs cgs.cgs_target !to_compute_completion in
      completionGt := completionlist
    );
    computed_completion := (!to_compute_completion)@(!computed_completion);
    to_compute_completion := [];
    []
  ) else []

let list_equal [a;b] = 
  if (a = b) then true else false

(*This function optimizes the PPEs so that the number of pairing operations become lesser.
For eg. if e(g1, g2), e(g1, g*3) as input, it outputs e(g1, g2*g3). *)
let optimize_ppes naive_ppes =
  (* let opimtized_ppes = ref ([]:group_elem list) in *)
  L.fold_left (fun optimized_ppes f -> match f.ge_id with
                            | Param(i) -> f::optimized_ppes
                            | _ -> (let (a1, a2) = L.fold_left (fun (ac1, ac2) (pos, g) -> match ac1.ge_id, g.ge_id with
                                               | Param(-1), _ -> (ac1, ac2)
                                               | Exp(Emap(em1,[r1;r2]), c), Emap(em2, [Multiply(r3); r4]) when (em1 = em2) && (rp_equal r2 r4) -> ({ac1 with ge_id = Param(-1)},
                                                                                        replace ac2 pos {g with ge_id = Emap(em1, [Multiply(Exp(r1,c)::r3); r2])})
                                               | Exp(Emap(em1,[r1;r2]), c), Emap(em2, [r3; r4]) when (em1 = em2) && (rp_equal r2 r4) -> ({ac1 with ge_id = Param(-1)},
                                                                                        replace ac2 pos {g with ge_id = Emap(em1, [Multiply([Exp(r1,c); r3]); r2])})
                                               
                                               | Emap(em1,[r1;r2]), Exp(Emap(em2, [r3; r4]), c) when (em1 = em2) && (rp_equal r2 r4) -> ({ac1 with ge_id = Param(-1)},
                                                                                        replace ac2 pos {g with ge_id = Emap(em1, [Multiply([r1; Exp(r3,c)]); r2])})
                                               
                                               | Emap(em1, [r1;r2]), Emap(em2, [r3;r4]) when (em1 = em2) && (rp_equal r2 r4) -> ({ac1 with ge_id = Param(-1)},
                                                                                        replace ac2 pos {g with ge_id = Emap(em1, [Multiply([r1; r3]); r2])})
                                               
                                               | Exp (Emap(em1,[r1;r2]), c), Emap(em2, [r4; Multiply(r3)]) when (em1 = em2) && (rp_equal r1 r4) -> ({ac1 with ge_id = Param(-1)},
                                                                                        replace ac2 pos {g with ge_id = Emap(em1, [r1; Multiply(Exp(r2, c)::r3)])})
                                               | Exp (Emap(em1,[r1;r2]), c), Emap(em2, [r4; r3]) when (em1 = em2) && (rp_equal r1 r4) -> ({ac1 with ge_id = Param(-1)},
                                                                                        replace ac2 pos {g with ge_id = Emap(em1, [r1; Multiply([Exp(r2,c); r3])])})
                                               | Emap(em1, [r1;r2]), Emap(em2, [r4;r3]) when (em1 = em2) && (rp_equal r1 r4) -> ({ac1 with ge_id = Param(-1)},
                                                                              replace ac2 pos {g with ge_id = Emap(em1, [r1; Multiply([r2; r3])])})
                                               
                                               (*For symmetric pairings*)
                                               | Exp(Emap(em1,[r1;r2]), c), Emap(em2, [r3; Multiply(r4)]) when (em1 = em2) && list_equal em1.em_dom && (rp_equal r2 r3) -> ({ac1 with ge_id = Param(-1)},
                                                                                        replace ac2 pos {g with ge_id = Emap(em1, [Multiply(Exp(r1,c)::r4); r2])})
                                               | Exp(Emap(em1,[r1;r2]), c), Emap(em2, [r3; r4]) when (em1 = em2) && list_equal em1.em_dom && (rp_equal r2 r3) -> ({ac1 with ge_id = Param(-1)},
                                                                                        replace ac2 pos {g with ge_id = Emap(em1, [Multiply([Exp(r1,c); r4]); r2])})
                                               
                                               | Emap(em1,[r1;r2]), Exp(Emap(em2, [r3; r4]), c) when (em1 = em2) && list_equal em1.em_dom && (rp_equal r2 r3) -> ({ac1 with ge_id = Param(-1)},
                                                                                        replace ac2 pos {g with ge_id = Emap(em1, [Multiply([r1; Exp(r4,c)]); r2])})
                                               
                                               | Emap(em1, [r1;r2]), Emap(em2, [r3;r4]) when (em1 = em2) && list_equal em1.em_dom && (rp_equal r2 r3) -> ({ac1 with ge_id = Param(-1)},
                                                                                        replace ac2 pos {g with ge_id = Emap(em1, [Multiply([r1; r4]); r2])})
                                               
                                               | Exp (Emap(em1,[r1;r2]), c), Emap(em2, [r4; Multiply(r3)]) when (em1 = em2) && list_equal em1.em_dom && (rp_equal r2 r4) -> ({ac1 with ge_id = Param(-1)},
                                                                                        replace ac2 pos {g with ge_id = Emap(em1, [r2; Multiply(Exp(r1, c)::r3)])})
                                               | Exp (Emap(em1,[r1;r2]), c), Emap(em2, [r4; r3]) when (em1 = em2) && list_equal em1.em_dom && (rp_equal r2 r4) -> ({ac1 with ge_id = Param(-1)},
                                                                                        replace ac2 pos {g with ge_id = Emap(em1, [r2; Multiply([Exp(r1,c); r3])])})
                                               | Emap(em1, [r1;r2]), Emap(em2, [r4;r3]) when (em1 = em2) && list_equal em1.em_dom && (rp_equal r2 r4) -> ({ac1 with ge_id = Param(-1)},
                                                                              replace ac2 pos {g with ge_id = Emap(em1, [r2; Multiply([r1; r3])])})

                                               | _, _ -> (ac1, ac2)
                                               )  
                                               (f, optimized_ppes) (L.mapi (fun pos h -> (pos,h)) optimized_ppes)
                                    in
                                    match a1.ge_id with
                                    | Param(-1) -> a2
                                    | _ -> f::optimized_ppes
                                  )
              ) [] naive_ppes

let rule1 (cgs, changed) untrusted_poly= 
  if changed then changed (*Don't continue if changed bit is set to true*)
  (*Check if the untrusted_poly contains only the variables in trusted set*)
  else
  (
        let vars_in_trusted = RP.vars_of_list (L.map (fun ge -> ge.ge_rpoly) !trusted) in
        let vars_in_given = RP.vars untrusted_poly.ge_rpoly in
        if (L.exists (fun var -> not (L.mem var vars_in_trusted)) vars_in_given) then changed
        else
        (     
            F.fprintf Format.std_formatter "\nComputing completion for by rule1\n";
            
            let time = Unix.gettimeofday() in
            (* Instead of computing completion list from scratch, updating the previously computed completion list*)
            update_completion_list cgs;
            (* let (compt,_) = completion_for_group cgs cgs.cgs_target !trusted in *)
            let compt = !completionGt in
            F.fprintf Format.std_formatter "\nProcessing untrusted polynomial F%d by rule1\n" (extract_fid untrusted_poly.ge_id);
            F.fprintf Format.std_formatter "Took %fs time to compute completion lists. Size of trusted set = %d. Size of completion list = %d.\n" (Unix.gettimeofday() -. time) (L.length !trusted) (L.length compt);
             
            let time = Unix.gettimeofday() in
            let (l, compt) = optimize [untrusted_poly] compt in
            F.fprintf Format.std_formatter "\nTook %fs time to optimize. " (Unix.gettimeofday() -. time);
            if (L.length l) = 0 then
            (
                F.fprintf Format.std_formatter "Rule not applied at optimization phase\n"; print_newline();
                changed
            )
            else
            (
                let time = Unix.gettimeofday() in 
                let (basis, matrix) = get_vector_repr (untrusted_poly::compt) in

                let matrix = L.tl matrix in
                F.fprintf Format.std_formatter "\nTook %fs time to compute basis. Size of trusted set = %d. Size of reduced completion list = %d. No. of monomials = %d. Solving equation of form x.M = v where x is the required coefficient vector and dimensions of M = %d*%d.\n" (Unix.gettimeofday() -. time) (L.length !trusted) (L.length compt) (L.length (L.nth matrix 0)) (L.length matrix) (L.length (L.nth matrix 0));
                 
                let vec = rp_to_vector basis untrusted_poly.ge_rpoly in
               (* pp_coeff_vector vec; *)
               (* F.fprintf Format.std_formatter "\nResult\n"; *)
               let time  = Unix.gettimeofday() in 
               let res = Sage_Solver.lin_solve matrix vec in 
               F.fprintf Format.std_formatter "Took %fs time to solve\n" (Unix.gettimeofday() -. time); 
               match res with
               | Some(x) -> 
                            if extract_group untrusted_poly.ge_group = cgs.cgs_target then
                            ( 
                                ppe := F.asprintf "F%d = " (extract_fid untrusted_poly.ge_id);
                            )
                            else
                            (
                                ppe := F.asprintf "e(F%d,F0) = " (extract_fid untrusted_poly.ge_id);
                            );
                            optimized_ppe := F.asprintf "%s" !ppe;
                            
                            let naive_ppe = ref ([]:group_elem list) in
                            let l = L.length x in
                            let first = ref true in
                            F.fprintf Format.std_formatter "Almost done!\n";
                            for i = 0 to (l-1) do
                                let exp = (L.nth x i) in
                                if exp <> 0 then
                                (
                                        (* F.fprintf Format.std_formatter "%a %d \n" pp_recipe (L.nth compt i).ge_id exp; *)
                                      if !first then (first := false;)
                                      else (ppe := (F.asprintf "%s  * " !ppe););
                                      if exp = 1 then (
                                        naive_ppe := (L.nth compt i)::!naive_ppe;
                                        ppe := (F.asprintf "%s%a" !ppe pp_recipe (L.nth compt i).ge_id);)
                                      else (
                                        naive_ppe := {(L.nth compt i) with ge_id = Exp((L.nth compt i).ge_id, exp)}::!naive_ppe;
                                        ppe := (F.asprintf "%s(%a)^%d" !ppe pp_recipe (L.nth compt i).ge_id exp);)
                                )
                            done;
                            F.fprintf Format.std_formatter "\nNaive PPE %s" !ppe;
                            optimized_ppe := F.asprintf "%s%a" !optimized_ppe pp_recipes (optimize_ppes !naive_ppe);
                            F.fprintf Format.std_formatter "\nOptimized PPE %s" !optimized_ppe;
                            ppes := (!ppe)::(!ppes);
                            optimized_ppes := (!optimized_ppe)::(!optimized_ppes);
                            F.fprintf Format.std_formatter "\nF%d moved to trusted set by rule 1\n" (extract_fid untrusted_poly.ge_id);        
                            add_to_trusted cgs untrusted_poly;
                            untrusted := (remove untrusted_poly !untrusted);
                            true
               | None -> (F.fprintf Format.std_formatter "Rule not applied\n"; 
                          changed
                        )
            )
        )
    )        
    


let rule2 (cgs, changed) untrusted_poly = 
  if changed then changed
  else
  (
    let vars_in_trusted = RP.vars_of_list (L.map (fun ge -> ge.ge_rpoly) !trusted) in
    let vars_in_given = RP.vars untrusted_poly.ge_rpoly in
    let new_vars = L.filter (fun var -> not (L.mem var vars_in_trusted)) vars_in_given in
    if L.length new_vars <> 1 then 
    (
      (* F.fprintf Format.std_formatter "\n%a contains lot of variables\n" RP.pp untrusted_poly.ge_rpoly; *)
      changed
    )
    else
    (
      F.fprintf Format.std_formatter "\nProcessing untrusted polynomial F%d = %a by rule2\n" (extract_fid untrusted_poly.ge_id) RP.pp untrusted_poly.ge_rpoly;
      let new_var = (L.nth new_vars 0) in
      if (RP.has_power untrusted_poly.ge_rpoly new_var [1;3;5;7;11;13;17;19]) && (RP.is_consts (RP.coeff_poly untrusted_poly.ge_rpoly new_var)) then 
      (
        F.fprintf Format.std_formatter "F%d moved to trusted set and %s moved to fixed set by rule 2\n" (extract_fid untrusted_poly.ge_id) new_var;
        fixed := ({ge_id = Param(-1); ge_group = None; ge_rpoly = RP.var new_var}::!fixed);
        add_to_trusted cgs untrusted_poly;
        untrusted := (remove untrusted_poly !untrusted);
        true
      )
      else
      (
        F.fprintf Format.std_formatter "Rule not applied\n";
        changed
      )
    )
  )
  
(* \ic{Analyze assumption.} *)
(* let rec analyze problem =
  F.fprintf Format.std_formatter "\n......................................................................\n";
  let (cgs, fixed, trusted, untrusted, changed) = L.fold_left (fun acc poly -> rule1 acc poly) (problem.ppe_cgs, problem.ppe_fixed, problem.ppe_trusted, problem.ppe_untrusted, false) problem.ppe_untrusted in
  let (cgs, fixed, trusted, untrusted, changed) = L.fold_left (fun acc poly -> rule2 acc poly) (cgs, fixed, trusted, untrusted, changed) untrusted in
  if changed then 
    analyze {ppe_cgs = cgs; ppe_fixed = fixed; ppe_trusted = trusted; ppe_untrusted = untrusted; ppe_order = problem.ppe_order}
  else 
    (cgs, fixed, trusted, untrusted) *)

let rec analyze cgs =
  print_newline();
  F.fprintf Format.std_formatter "\n......................................................................\n";
  let (_, changed) = L.fold_left (fun (cgs, changed) poly -> (cgs, rule2 (cgs, changed) poly)) (cgs, false) !untrusted in
  if changed then analyze cgs
  else
  (
    let (_, changed) = L.fold_left (fun (cgs, changed) poly -> (cgs, rule1 (cgs, changed) poly)) (cgs, changed) !untrusted in
    if changed then 
      analyze cgs
    else
      (cgs, !fixed, !trusted, !untrusted)
  )


let solve problem = 
  fid_counter := L.fold_left (fun acc f -> if (acc < (extract_fid f.ge_id)) then (extract_fid f.ge_id) else acc) 0 (problem.ppe_trusted@problem.ppe_untrusted); 
  fid_counter := !fid_counter+1;
  let added = L.fold_left (fun acc f -> acc @ (multiply_zp f problem.ppe_zp)) [] problem.ppe_trusted  in
  F.fprintf Format.std_formatter "\nAdding set : ";
  L.iter (fun f -> F.fprintf Format.std_formatter " %a in G%s, " RP.pp f.ge_rpoly (extract_group f.ge_group)) added;
  L.iter (fun f -> F.fprintf Format.std_formatter "\nF%d = %a in G%s" (extract_fid f.ge_id) RP.pp f.ge_rpoly (extract_group f.ge_group);) (problem.ppe_trusted@problem.ppe_untrusted@added);
  
  trusted := (problem.ppe_trusted@added);
  untrusted := problem.ppe_untrusted;
  to_compute_completion := !trusted;
  fixed := problem.ppe_fixed;
  zp := problem.ppe_zp;
  analyze problem.ppe_cgs
  (* (problem.ppe_cgs, problem.ppe_fixed, problem.ppe_trusted, problem.ppe_untrusted) *)


(*******************************************************************)
(* \hd{Analyze assumption given as string or from file} *)

(* \ic{Convert lexer and parser errors to error with meaningful message.} *)
let wrap_error f s =
  let sbuf = Lexing.from_string s in
  begin try
    f sbuf
  with
  | PPEParser.Error ->
    let start = Lexing.lexeme_start sbuf in
    let err =
      Printf.sprintf
        "Syntax error at offset %d (length %d): \
         parsed ``%s'',\nerror at ``%s''"
        start
        (S.length s)
        (if start >= S.length s then s  else (S.sub s 0 start))
        (if start >= S.length s then "" else (S.sub s start (S.length s - start)))
    in
    print_endline err;
    failwith err
  | PPELexer.Error msg ->
    raise (failwith (Printf.sprintf "%s" msg))
  | InvalidInput _ as e ->
    raise e
  | _ ->
    failwith "Unknown error while lexing/parsing."
  end

let p_cmds = wrap_error (PPEParser.cmds_t PPELexer.lex)

let analyze_from_string scmds = 
  let time = Unix.gettimeofday() in 
  let output = scmds |> p_cmds |> eval_cmds |> solve in
  Printf.printf "Execution time : %fs\n" (Unix.gettimeofday() -. time);
  output

let analyze_file fn = input_file fn |> analyze_from_string


(*i*)
(*******************************************************************)
(* \hd{Pretty printing} *)

(* let pp_untrusted fmt ge = 
  F.fprintf fmt "U";
 *)
let pp_result_info fmt (_, _, _, untrusted) = 
(*   F.fprintf fmt "\n\nFixed set : ";
  L.iter (fun f -> F.fprintf fmt " %a, " RP.pp f.ge_rpoly) fixed;
  F.fprintf fmt "\n\nTrusted set : ";
  L.iter (fun f -> F.fprintf fmt " %a in G%s, " RP.pp f.ge_rpoly (extract_group f.ge_group)) trusted; *)
  F.fprintf fmt "\n\nUntrusted set : ";
  L.iter (fun f -> F.fprintf fmt " F%d, " (extract_fid f.ge_id)) untrusted;
  F.fprintf fmt "\n\nPPEs : ";
  L.iter (fun s -> F.fprintf fmt "%s,   " s) !optimized_ppes;
  if (L.length untrusted) = 0 then
    F.fprintf fmt "\n\nOuptut : PPE Testable :)"
  else
    F.fprintf fmt "\n\nOutput : Unknown :(";
  F.fprintf fmt "\n";
