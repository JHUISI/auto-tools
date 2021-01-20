(* This file is distributed under the MIT License (see LICENSE). *)

(*i*)
open Util
open PPEInput
open PPECompletion
open PPERules
open PPEHelper
open Sage_Solver
(* open LPoly *)


module S = String
let ppes = ref ([]:string list);; 
let ppe = ref "";;
let optimized_ppe = ref "";;
let optimized_ppes = ref ([]:string list);;
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


let rec repeat_vector element length = 
  if length = 1 then [element]
  else element::(repeat_vector element (length-1))


let add_non_duplicates lst1 lst2 = 
  L.fold_left (fun acc f -> if (L.exists (fun g -> (RP.equal f.ge_rpoly g.ge_rpoly) && (f.ge_group = g.ge_group)) acc) then acc
                              else f::acc) lst2 lst1



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


let rec rule1loop sts pi k = 
    if (L.length pi.ppe_untrusted) <= k then 
        (false, EMPTY, pi, k)
    else
        let (success, ckt, pi1) = rule1 sts pi k in
        if success then (success, ckt, pi1, k)
        else rule1loop sts pi (k+1)

let rec rule2loop sts pi k = 
    if (L.length pi.ppe_untrusted) <= k then 
        (false, pi, k)
    else 
        let (success, pi1) = rule2 sts pi k in
        if success then (success, pi1, k)
        else rule2loop sts pi (k+1)

let rec rule3loop sts pi k = 
    if (L.length pi.ppe_untrusted) <= k then 
        (false, EMPTY, EMPTY, pi, pi, k)
    else 
        let (success, isidentical, ckt, pi1, pi2) = rule3 sts pi k in
        if success then (success, isidentical, ckt, pi1, pi2, k)
        else rule3loop sts pi (k+1)

(* 
let rec rule4loop sts pi k = 
    if (L.length pi.ppe_untrusted) <= k then 
        (false, EMPTY, pi, pi, k)
    else
        let (success, isidentical, pi1, pi2) = rule4 sts pi k in
        if success then (success, isidentical, pi1, pi2, k)
        else rule4loop sts pi (k+1)

let rec rule5loop sts pi k = 
    if (L.length pi.ppe_untrusted) <= k then 
        (false, EMPTY, EMPTY, pi, pi, k)
    else
        let (success, isidentical1, isidentical2, pi1, pi2) = rule5 sts pi k in
        if success then (success, isidentical1, isidentical2, pi1, pi2, k)
        else rule5loop sts pi (k+1)
 *)
let rec rule4loop sts pi k = 
    if (L.length pi.ppe_untrusted) <= k then 
        (false, EMPTY, pi, pi, k)
    else
        let (success, isidentical, pi1, pi2) = rule4 sts pi k in
        if success then (success, isidentical, pi1, pi2, k)
        else rule4loop sts pi (k+1)

(* let rec rule5loop pi k = 
    if (L.length problem.ppe_untrusted) = k then (false, EMPTY, EMPTY, pi, pi)
    let (success, isidentical1, isidentical2, pi1, pi2) = rule5 pi k in
    if success then (success, isidentical1, isidentical2, pi1, pi2)
    else rule4loop pi k+1
in *)


let rec applyrule1loop sts problem k =
(
    let (success, ckt, pi, k2) = rule1loop sts problem k in 
    if success then
    (
        let (success, ckt2) = analyze sts pi in
        if success then 
            (true, AND(ckt, ckt2))
        else 
          applyrule1loop sts problem (k2+1)
    )
  else
    (false, EMPTY)
)

and applyrule2loop sts problem k = 
(
    let (success, pi, k2) = rule2loop sts problem k in 
    if success then 
    (
        let (success, ckt) = analyze sts pi in 
        if success then 
            (true, ckt)
        else
            applyrule2loop sts problem (k2+1)            
    )
    else 
        (false, EMPTY) 
)

and applyrule3loop sts problem k = 
    let (success, isidentical, ckt, pi1, pi2, k2) = rule3loop sts problem k in 
    if success then 
    (
        let (success1, ckt1) = analyze sts pi1 in
        if success1 then 
        (
            let (success2, ckt2) = analyze sts pi2 in
            if success2 then 
                (true, OR( AND(AND(NOT(isidentical), ckt),ckt1),  AND(isidentical, ckt2) ))
            else
                applyrule3loop sts problem (k2+1)
        )
        else
            applyrule3loop sts problem (k2+1)
    )
    else
        (false, EMPTY)
        
and applyrule4loop sts problem k = 
    let (success, isidentical, pi1, pi2, k2) = rule4loop sts problem k in 
    if success then 
    (
        let (success1, ckt1) = analyze sts pi1 in
        if success1 then 
        (
            let (success2, ckt2) = analyze sts pi2 in
            if success2 then 
                (true, OR( AND(NOT(isidentical),ckt1),  AND(isidentical, ckt2) ))
            else
                applyrule4loop sts problem (k2+1)
        )
        else
            applyrule4loop sts problem (k2+1) 
    )
    else 
        (false, EMPTY)

and analyze sts problem : (bool * circuit) = 
    (* F.fprintf Format.std_formatter "\nanalyze\n"; *)
    if (L.length problem.ppe_untrusted) = 0 then 
    (   
        (* F.fprintf Format.std_formatter "\n Success"; *)
        (* stop_sage sts;  *)
        (true, ACCEPT)
    )
    else
        let (success, ckt) = applyrule1loop sts problem 0 in 
        if success then
            (true, ckt)
        else
            let (success, ckt) = applyrule2loop sts problem 0 in 
            if success then
                (true, ckt)
            else
                let (success, ckt) = applyrule3loop sts problem 0 in 
                if success then
                    (true, ckt)
                else
                    let (success, ckt) = applyrule4loop sts problem 0 in 
                    if success then
                        (true, ckt)
                    else
                    (
                        F.fprintf Format.std_formatter "\nNone of the rules are applicable on following PPE problem ";
                        print_problem problem;
                        (false, EMPTY)
                    )

(* 


let rec analyze sts problem : (bool * circuit) = 
    (* F.fprintf Format.std_formatter "\nanalyze\n"; *)
    if (L.length problem.ppe_untrusted) = 0 then 
    (   
        (* F.fprintf Format.std_formatter "\n Success"; *)
        (* stop_sage sts;  *)
        (true, ACCEPT)
    )
    else
        let (success, ckt, pi) = rule1loop sts problem 0 in 
        if success then
        (
            let (success, ckt2) = analyze sts pi in
            if success then 
                (true, AND(ckt, ckt2))
            else 
                let tmp = stop_sage sts in
                (false, EMPTY)
        )
        else
            let (success, pi) = rule2loop sts problem 0 in 
            if success then 
            (
                let (success, ckt) = analyze sts pi in 
                if success then 
                    (true, ckt)
                else 
                    (false, EMPTY) 
            )
            else
                let (success, isidentical, ckt, pi1, pi2) = rule3loop sts problem 0 in 
                if success then 
                (
                    let (success1, ckt1) = analyze sts pi1 in
                    if success1 then 
                        let (success2, ckt2) = analyze sts pi2 in
                        if success2 then 
                            (true, OR( AND(AND(NOT(isidentical), ckt),ckt1),  AND(isidentical, ckt2) ))
                        else
                            (false, EMPTY)
                    else 
                        (false, EMPTY)
                )
                else
                    let (success, isidentical, pi1, pi2) = rule4loop sts problem 0 in 
                    if success then 
                    (
                        let (success1, ckt1) = analyze sts pi1 in
                        if success1 then
                            let (success2, ckt2) = analyze sts pi2 in
                            if success2 then 
                                (true, OR( AND(NOT(isidentical),ckt1),  AND(isidentical, ckt2) ))
                            else
                                (false, EMPTY)
                        else 
                            (false, EMPTY)
                    )
                    else 
                        (* let (success, isidentical1, isidentical2, pi1, pi2) = rule5loop problem 0 in 
                        if success then 
                        (
                            let (success1, ckt1) = analyze pi1 in
                            if success1 then
                                let (success2, ckt2) = analyze pi2 in
                                if success2 then 
                                    let c1 = AND (OR(NOT(isidentical1), NOT(isidentical2)), ckt1)  in 
                                    let c2 = AND (AND(isidentical1, isidentical2), ckt2) in
                                    (true, OR(c1, c2))
                                else
                                    (false, EMPTY)
                            else 
                                (false, EMPTY)
                        ) *)
                        let (success, isidentical, pi1, pi2) = rule6loop sts problem 0 in 
                        if success then 
                        (
                            let (success1, ckt1) = analyze sts pi1 in
                            if success1 then
                                let (success2, ckt2) = analyze sts pi2 in
                                if success2 then 
                                    (true, OR( AND(NOT(isidentical),ckt1),  AND(isidentical, ckt2) ))
                                else
                                    (false, EMPTY)
                            else 
                                (false, EMPTY)
                        )

                        else
                        (
                            F.fprintf Format.std_formatter "\nNone of the rules are applicable on following PPE problem ";
                            print_problem problem;
                            (false, EMPTY)
                        ) *)

let solve problem = 
    fid_counter := L.fold_left (fun acc f -> if (acc < (extract_fid f.ge_id)) then (extract_fid f.ge_id) else acc) 0 (problem.ppe_trusted@problem.ppe_untrusted); 
    fid_counter := !fid_counter+1;
    let added = L.fold_left (fun acc f -> acc @ (multiply_zp f problem.ppe_zp)) [] problem.ppe_trusted  in
    F.fprintf Format.std_formatter "\nAdding set : ";
    L.iter (fun f -> F.fprintf Format.std_formatter " %a in G%s, " RP.pp f.ge_rpoly (extract_group f.ge_group)) added;
    L.iter (fun f -> F.fprintf Format.std_formatter "\n%a = %a in G%s" pp_fid f.ge_id RP.pp f.ge_rpoly (extract_group f.ge_group);) (problem.ppe_trusted@problem.ppe_untrusted@added);
    let problem = {problem with ppe_trusted = problem.ppe_trusted@added } in
    let (completion,_) = completion_for_group problem.ppe_cgs problem.ppe_cgs.cgs_target problem.ppe_trusted in 
    let problem = {problem with completionGt = completion} in 
    let sts = start_sage () in
    analyze sts problem
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
  Printf.printf "\nExecution time : %fs\n" (Unix.gettimeofday() -. time);
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
  L.iter (fun f -> F.fprintf fmt " %a, " pp_fid f.ge_id) untrusted;
  F.fprintf fmt "\n\nPPEs : ";
  L.iter (fun s -> F.fprintf fmt "%s,   " s) !optimized_ppes;
  if (L.length untrusted) == 0 then
    F.fprintf fmt "\n\nOuptut : PPE Testable :)"
  else
    F.fprintf fmt "\n\nOutput : Unknown :(";
  F.fprintf fmt "\n";
