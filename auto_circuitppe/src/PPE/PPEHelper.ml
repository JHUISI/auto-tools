open Util
open PPEInput
open PPECompletion


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
    (* F.fprintf Format.std_formatter "\nOptimization round %d" !cnt; *)
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
    (* print_newline(); *)

    if ((L.length !lst11) = l1) && ((L.length !lst22) = l2) then
      (!lst11,!lst22)
    else
      go 1
  in
  go 1


let print_problem problem =
    F.fprintf Format.std_formatter "\nTrusted set in G1: ";
    L.iter (fun f -> if (extract_group f.ge_group) <> problem.ppe_cgs.cgs_target then 
                    F.fprintf Format.std_formatter "%a = %a, " pp_fid f.ge_id  RP.pp f.ge_rpoly) problem.ppe_trusted;
    F.fprintf Format.std_formatter "\nTrusted set in GT: ";
    L.iter (fun f -> if (extract_group f.ge_group) = problem.ppe_cgs.cgs_target then 
                    F.fprintf Format.std_formatter "%a = %a, " pp_fid f.ge_id RP.pp f.ge_rpoly) problem.ppe_trusted;
    F.fprintf Format.std_formatter "\nUntrusted set in G1: ";
    L.iter (fun f -> if (extract_group f.ge_group) <> problem.ppe_cgs.cgs_target then 
                F.fprintf Format.std_formatter "%a = %a, " pp_fid f.ge_id RP.pp f.ge_rpoly) problem.ppe_untrusted;
    F.fprintf Format.std_formatter "\nUntrusted set in GT: ";
    L.iter (fun f -> if (extract_group f.ge_group) = problem.ppe_cgs.cgs_target then 
                F.fprintf Format.std_formatter "%a = %a, " pp_fid f.ge_id RP.pp f.ge_rpoly) problem.ppe_untrusted    

let remove_duplicates lst = 
  L.fold_left (fun acc f -> if (L.exists (fun g -> (RP.equal f.ge_rpoly g.ge_rpoly) && (f.ge_group = g.ge_group)) acc) then acc
                              else f::acc) [] lst

let multiply_zp poly zp = 
  assert (!degree >= 1);
  (* fid_counter := counter; *)
  if (L.length zp) = 0 then []
  else if (!degree = 1) then 
  (
    let output = L.fold_left (fun acc p -> acc@[{ge_rpoly = (RP.mult p.ge_rpoly poly.ge_rpoly); ge_group = poly.ge_group; ge_id = Expzp(poly.ge_id, p.ge_rpoly)}]) [] zp in
    (* let output = L.map (fun f -> fid_counter := !fid_counter+1; {f with ge_id = Param(!fid_counter-1)}) output in  *)
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
 
let add_non_duplicates lst1 lst2 = 
  L.fold_left (fun acc f -> if (L.exists (fun g -> (RP.equal f.ge_rpoly g.ge_rpoly) && (f.ge_group = g.ge_group)) acc) then acc
                              else f::acc) lst2 lst1

let remove p lst = 
  L.filter (fun ele -> not (ele.ge_group = p.ge_group && RP.equal ele.ge_rpoly p.ge_rpoly)) lst

let transferpoly problem k = 
    let poly = (L.nth problem.ppe_untrusted k) in 
(*     let counter = L.fold_left (fun max p -> if max < extract_fid p.ge_id then extract_fid p.ge_id else max) 0 problem.ppe_trusted in 
    let counter = L.fold_left (fun max p -> if max < extract_fid p.ge_id then extract_fid p.ge_id else max) counter problem.ppe_untrusted in  *)
    let added = multiply_zp poly problem.ppe_zp in
    let added = poly::added in
(*     let fixedlist = RP.vars_of_list (L.map (fun ge -> ge.ge_rpoly) problem.ppe_trusted) in
    let problem = {problem with ppe_fixed = L.map (fun var -> {ge_id=Param(-1); ge_group=None; ge_rpoly=RP.var var}) fixedlist} in  *)

(*     let completion = if (extract_group poly.ge_group) = problem.ppe_cgs.cgs_target then
        (
            poly::problem.completionGt
        )
        else
        (
            let (completionlist,_) = (new_completion_for_group problem.ppe_cgs problem.ppe_cgs.cgs_target added problem.ppe_trusted) in
            (* F.fprintf "\n adding completion list " *)
            add_non_duplicates completionlist problem.completionGt
        ) in  *)
    let problem = {problem with ppe_trusted = problem.ppe_trusted@added} in
    let (completion,_) = completion_for_group problem.ppe_cgs problem.ppe_cgs.cgs_target problem.ppe_trusted in 
    let problem = {problem with ppe_untrusted = (remove poly problem.ppe_untrusted)} in
    let problem = {problem with completionGt = completion} in 
    problem
