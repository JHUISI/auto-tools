

open Util
open PPEInput
open LPoly
open PPECompletion
open PPEHelper
open Sage_Solver
(* open PPEAnalyze  *)

(* let st = start_sage () in
let sts = ref st;; *)
(* let res = eval_sage sts cmd in *)



let get_vector_repr pss =
  let mbasis =
    conc_map (fun ps -> RP.mons ps.ge_rpoly) pss |>
      sorted_nub compare
  in
  let vps = L.map (fun ps -> (rp_to_vector mbasis) ps.ge_rpoly) pss in
  (mbasis, vps)



let updateforzero problem poly = 
    let problem = {problem with ppe_trusted = L.map (fun f -> 
                        let result = RP.substitutezero poly f.ge_rpoly in
                        (* F.fprintf Format.std_formatter "\nzeropoly = %a, f = %a, result = %a" RP.pp poly RP.pp f.ge_rpoly RP.pp result; *)
                        {f with ge_rpoly = result}
                        ) problem.ppe_trusted} in 
    let problem = {problem with ppe_untrusted = L.map (fun f -> 
                        let result = RP.substitutezero poly f.ge_rpoly in
                        (* F.fprintf Format.std_formatter "\nzeropoly = %a, f = %a, result = %a" RP.pp poly RP.pp f.ge_rpoly RP.pp result; *)
                        {f with ge_rpoly = result}
                        ) problem.ppe_untrusted} in     

    (* let problem = {problem with ppe_trusted = L.map (fun f -> {f with ge_rpoly = RP.substitutezero poly f.ge_rpoly}) problem.ppe_trusted} in  *)
    (* let problem = {problem with ppe_untrusted = L.map (fun f -> {f with ge_rpoly = RP.substitutezero poly f.ge_rpoly}) problem.ppe_untrusted} in  *)

(*     let fixedlist = RP.vars_of_list (L.map (fun ge -> ge.ge_rpoly) problem.ppe_trusted) in
    let problem = {problem with ppe_fixed = L.map (fun var -> {ge_id=Param(-1); ge_group=None; ge_rpoly=RP.var var}) fixedlist} in  *)
    let (completion,_) = completion_for_group problem.ppe_cgs problem.ppe_cgs.cgs_target problem.ppe_trusted in 
    let problem = {problem with completionGt = completion} in 
    problem 


let rule1sourcegroup (sts:st_sage) problem k = 
    (* F.fprintf Format.std_formatter "\nEntered Rule 1s"; *)
    let untrusted_poly = (L.nth problem.ppe_untrusted k) in
    if (extract_group untrusted_poly.ge_group) <> problem.ppe_cgs.cgs_target then
    (
        let (comp,_) = completion_for_group problem.ppe_cgs (extract_group untrusted_poly.ge_group) problem.ppe_trusted in 
        
        let time = Unix.gettimeofday() in 
        let (l, comp) = optimize [untrusted_poly] comp in
        (* F.fprintf Format.std_formatter "\nRule1s Took %f sec to optimize" (Unix.gettimeofday() -. time); *)
        if (L.length l) = 0 then
        (
            (* F.fprintf Format.std_formatter "\nRule not applied at optimization phase\n"; print_newline(); *)
            (false, EMPTY, problem)
        )
        else if (L.length comp) = 0 then
        (
            let ckt = PPE(untrusted_poly.ge_id, Identity) in
            F.fprintf Format.std_formatter "\n...."; 
            print_problem problem;
            F.fprintf Format.std_formatter "\nrule 1 applied to %a = %a.     C := %a" pp_fid untrusted_poly.ge_id RP.pp untrusted_poly.ge_rpoly pp_circuit ckt;
            F.fprintf Format.std_formatter "\n...."; 
            (true, ckt, transferpoly problem k)
        )
        else
                let (basis, matrix) = get_vector_repr (untrusted_poly::comp) in
                (* F.fprintf Format.std_formatter "\nEntered Rule1s else"; *)

                let matrix = L.tl matrix in
                let vec = rp_to_vector basis untrusted_poly.ge_rpoly in
                let res = Sage_Solver.lin_solve ~sts:sts matrix vec in 
                match res with 
                | Some(x) -> 
                    (* F.fprintf Format.std_formatter "\nRule1s after res"; *)

                    let rightlist = ref [] in 
                    let l = L.length x in
                    for i = 0 to (l-1) do
                        let exp = (L.nth x i) in
                        if exp <> 0 then
                        (
                           rightlist := Exp((L.nth comp i).ge_id, exp)::!rightlist; 
                        )
                    done;
                    let e = L.nth problem.ppe_cgs.cgs_emaps 0 in
                    let leftside = untrusted_poly.ge_id in 
                    let rightside = if (L.length !rightlist = 0) then Identity  else Multiply(!rightlist) in 
                    let ckt = PPE(leftside, rightside) in 
                    let pi = transferpoly problem k in 

                    F.fprintf Format.std_formatter "\n...."; 
                    print_problem problem;
                    F.fprintf Format.std_formatter "\nrule 1 applied to %a = %a.     C := %a" pp_fid untrusted_poly.ge_id RP.pp untrusted_poly.ge_rpoly pp_circuit ckt;
                    F.fprintf Format.std_formatter "\n...."; 

                    (true, ckt, pi)
                | None -> (false, EMPTY, problem)
    )
    else 
        (false, EMPTY, problem)

let rule1 (sts:st_sage) problem k = 
    (* F.fprintf Format.std_formatter "\nEntered Rule 1"; *)
    let untrusted_poly = (L.nth problem.ppe_untrusted k) in
    let vars_in_trusted = RP.vars_of_list (L.map (fun ge -> ge.ge_rpoly) problem.ppe_trusted) in
    let vars_in_given = RP.vars untrusted_poly.ge_rpoly in
    if (L.exists (fun var -> not (L.mem var vars_in_trusted)) vars_in_given) then
        (false, EMPTY, problem)

    else
    (     
        let (success, ckt, pi) = rule1sourcegroup sts problem k in 
        if success then 
            (success, ckt, pi)
        else
            let compt = problem.completionGt in

            let time = Unix.gettimeofday() in 
            let (l, compt) = optimize [untrusted_poly] compt in
            (* F.fprintf Format.std_formatter "\nRule1 Took %f sec to optimize" (Unix.gettimeofday() -. time); *)
            if (L.length l) = 0 then
            (
                (* F.fprintf Format.std_formatter "\nRule not applied at optimization phase\n"; *)
                (false, EMPTY, problem)
            )
            else if (L.length compt) = 0 then
            (
                let ckt = PPE(untrusted_poly.ge_id, Identity) in
                F.fprintf Format.std_formatter "\n...."; 
                print_problem problem;
                F.fprintf Format.std_formatter "\nrule 1 applied to %a = %a.     C := %a" pp_fid untrusted_poly.ge_id RP.pp untrusted_poly.ge_rpoly pp_circuit ckt;
                F.fprintf Format.std_formatter "\n...."; 
                (true, ckt, transferpoly problem k)
            )
            else
                let time = Unix.gettimeofday() in 
                let (basis, matrix) = get_vector_repr (untrusted_poly::compt) in
                let matrix = L.tl matrix in
                (* F.fprintf Format.std_formatter "\nTook %fs time to compute basis. Size of trusted set = %d. Size of reduced completion list = %d. No. of monomials = %d. Solving equation of form x.M = v where x is the required coefficient vector and dimensions of M = %d*%d.\n" (Unix.gettimeofday() -. time) (L.length !trusted) (L.length compt) (L.length (L.nth matrix 0)) (L.length matrix) (L.length (L.nth matrix 0)); *) 
                let vec = rp_to_vector basis untrusted_poly.ge_rpoly in
                let time  = Unix.gettimeofday() in 
                let res = Sage_Solver.lin_solve ~sts:sts matrix vec in 
                F.fprintf Format.std_formatter "\nChecking for Rule 1. Took %fs time to solve\n" (Unix.gettimeofday() -. time); 
                match res with
                | Some(x) -> 
                    (* F.fprintf Format.std_formatter "\nRule1 after res"; *)
                    let rightlist = ref [] in 
                    let l = L.length x in
                    for i = 0 to (l-1) do
                        let exp = (L.nth x i) in
                        if exp <> 0 then
                        (
                           rightlist := Exp((L.nth compt i).ge_id, exp)::!rightlist; 
                        )
                    done;
                    let e = L.nth problem.ppe_cgs.cgs_emaps 0 in
                    let leftside = if extract_group untrusted_poly.ge_group = problem.ppe_cgs.cgs_target then 
                                        untrusted_poly.ge_id
                                    else
                                        Emap(e, [untrusted_poly.ge_id; Param(0)])
                                    in 
                    let rightside = if (L.length !rightlist = 0) then Identity  else Multiply(!rightlist) in 
                    (* let rightside = Multiply(!rightlist) in  *)
                    let ckt = PPE(leftside, rightside) in 
                    let pi = transferpoly problem k in 

                    F.fprintf Format.std_formatter "\n...."; 
                    print_problem problem;
                    F.fprintf Format.std_formatter "\nrule 1 applied to %a = %a.     C := %a" pp_fid untrusted_poly.ge_id RP.pp untrusted_poly.ge_rpoly pp_circuit ckt;
                    F.fprintf Format.std_formatter "\n...."; 

                    (true, ckt, pi)
               | None -> (false, EMPTY, problem)
                    (* (F.fprintf Format.std_formatter "Rule not applied\n"; 
                          changed
                    ) *)
    )   
    


let rule2 sts problem k = 
    (* F.fprintf Format.std_formatter "\nEntered Rule 2"; *)
    let untrusted_poly = (L.nth problem.ppe_untrusted k) in
    let vars_in_trusted = RP.vars_of_list (L.map (fun ge -> ge.ge_rpoly) problem.ppe_trusted) in
    let vars_in_given = RP.vars untrusted_poly.ge_rpoly in
    let new_vars = L.filter (fun var -> not (L.mem var vars_in_trusted)) vars_in_given in
    if L.length new_vars <> 1 then 
        (false, problem)
    else
    (
        (* F.fprintf Format.std_formatter "\nProcessing untrusted polynomial F%d = %a by rule2\n" (extract_fid untrusted_poly.ge_id) RP.pp untrusted_poly.ge_rpoly; *)
        let new_var = (L.nth new_vars 0) in
        if (RP.has_power untrusted_poly.ge_rpoly new_var [1;3;5;7;11;13;17;19]) && (RP.is_consts (RP.coeff_poly untrusted_poly.ge_rpoly new_var)) then 
        (
            F.fprintf Format.std_formatter "\n...."; 
            print_problem problem;
            F.fprintf Format.std_formatter "\nrule 2 applied to %a = %a." pp_fid untrusted_poly.ge_id RP.pp untrusted_poly.ge_rpoly;
            F.fprintf Format.std_formatter "\n...."; 
            
            (* let problem = {problem with ppe_fixed = {ge_id = Param(-1); ge_group = None; ge_rpoly = RP.var new_var}::problem.ppe_fixed} in  *)
            let pi = transferpoly problem k in 
            (true, pi)
        )
        else
        (
            (* F.fprintf Format.std_formatter "Rule not applied\n"; *)
            (false, problem)
        )
    )

let first_elements vec count = 
    let vec = L.filter (fun (iter, _) -> iter < count) (L.mapi (fun iter ele ->  (iter, ele)) vec) in 
    L.map (fun (iter, ele) -> ele) vec 

let last_elements vec count = 
    let vec = L.filter (fun (iter, _) -> iter >= count) (L.mapi (fun iter ele ->  (iter, ele)) vec) in 
    L.map (fun (iter, ele) -> ele) vec 


(* pp_int_matrix res; *)
let if_valid_result ftimescompo compo vec count = 
    let poly = ref [] in
    for i = 0 to (count-1) do
        let exp = (L.nth vec i) in
            if exp <> 0 then
            (
                let index = extract_fid (L.nth ftimescompo i).ge_id in
                poly := RP.add !poly (RP.mult (RP.const (IntRing.from_int exp)) (L.nth compo index).ge_rpoly);  
            )
    done;
    if L.exists (fun ele -> not (ele = 0)) (first_elements vec count) (*Checks if first count number of elements in vec are zeros*)
        && (L.length !poly != 0)     (*Checking if the polynomial multiplied with untrusted_poly is zero*)
    then true
    else false


(*  *)
let get_result_vector res left_side_count = 
    (*For each vector in result, including the number of non-zero values in the vector*)
    let res = L.map ( fun vec ->  (L.fold_left (fun acc ele -> if ele = 0 then acc else acc + 1) 0 (last_elements vec left_side_count), vec)  ) res in 
    (*Get the vector with smallest number of non-zero values *)
    let (acc, vec) = L.fold_left ( fun (min, minvec) (count, vec) ->  if (min = -1) || (min > count) then (count, vec) 
                                                                    else (min, minvec)
                                ) (-1,[]) res in 
    vec

let rule3 sts problem k = 
    (* F.fprintf Format.std_formatter "\nEntered Rule 3"; *)
    let untrusted_poly = (L.nth problem.ppe_untrusted k) in
    let vars_in_trusted = RP.vars_of_list (L.map (fun ge -> ge.ge_rpoly) problem.ppe_trusted) in
    let vars_in_given = RP.vars untrusted_poly.ge_rpoly in
    if (L.exists (fun var -> not (L.mem var vars_in_trusted)) vars_in_given) || (extract_group untrusted_poly.ge_group = problem.ppe_cgs.cgs_target) then 
        (false, EMPTY, EMPTY, problem, problem)
    else
        let other_group = try L.find (fun g -> (g <> problem.ppe_cgs.cgs_target) && (g <> extract_group untrusted_poly.ge_group)) (Ss.elements problem.ppe_cgs.cgs_gids)
                          with Not_found -> extract_group untrusted_poly.ge_group in
        let compt = problem.completionGt in
        let (compo,_) = completion_for_group problem.ppe_cgs other_group problem.ppe_trusted in 
        (* let compt = L.filter (fun f -> not (L.length f.ge_rpoly = 0)) compt (*Filtering out zero polynomials to avoid trivial PPEs*) *)
        let compo = L.filter (fun f -> not (L.length f.ge_rpoly = 0)) compo in
        (* let ftimescompo = L.map (fun h -> {ge_id = h.ge_id; ge_group = None; ge_rpoly = RP.mult h.ge_rpoly untrusted_poly.ge_rpoly}) compo in *)
        let ftimescompo = L.mapi (fun index h -> {ge_id = Param(index); ge_group = None; ge_rpoly = RP.mult h.ge_rpoly untrusted_poly.ge_rpoly}) compo in (*This is a hack. storing ge_id as Param(index in compo)*)

        let time = Unix.gettimeofday() in 
        let (ftimescompo, compt) = optimize ftimescompo compt in
        (* F.fprintf Format.std_formatter "\nChecking for Rule 3. Took %fs time to optimize" (Unix.gettimeofday() -. time);  *)

        if L.length ftimescompo = 0 then
            (false, EMPTY, EMPTY, problem, problem)
        else
            let l1 = L.length ftimescompo in
            let l2 = L.length compt in
            let time = Unix.gettimeofday() in
            let polys = ftimescompo@compt in
            let (basis, matrix) = get_vector_repr polys in  
             F.fprintf Format.std_formatter "\nChecking for Rule 3. Took %fs to compute basis. Size of reduced f.(completion list of G1) U (completion list of GT) = %d. No. of monomials = %d. 
              Solving equation of form x.M = 0, where x is the required coefficient vector and dimensions of M = %d*%d" (Unix.gettimeofday() -. time) (L.length polys) (L.length (L.nth matrix 0)) (L.length matrix) (L.length (L.nth matrix 0));
            print_newline();
            let time = Unix.gettimeofday() in 
            let res = Sage_Solver.compute_kernel ~sts:sts matrix in
            F.fprintf Format.std_formatter "Checking for Rule 3. Took %fs time to solve" (Unix.gettimeofday() -. time); 

            if L.length res <> 0 && L.exists (fun vec -> if_valid_result ftimescompo compo vec l1) res then 
            (
                let leftlist = ref [] in 
                let poly = ref [] in 
                let res = get_result_vector (L.filter (fun vec -> if_valid_result ftimescompo compo vec l1) res) l1 in 
                (* let res = get_result_vector (L.filter (fun vec -> if_not_zeros vec l1) res) l1 in  *)
                for i = 0 to (l1-1) do
                    let exp = (L.nth res i) in
                    if exp <> 0 then
                    (
                        let index = extract_fid (L.nth ftimescompo i).ge_id in
                        leftlist := Exp((L.nth compo index).ge_id, exp)::!leftlist;
                        poly := RP.add !poly (RP.mult (RP.const (IntRing.from_int exp)) (L.nth compo index).ge_rpoly);  
                    )
                done;
                let e = L.nth problem.ppe_cgs.cgs_emaps 0 in
                let leftside = Emap(e, [untrusted_poly.ge_id; Multiply(!leftlist)]) in 
                
                let rightlist = ref [] in
                for i = 0 to (l2-1) do
                  let exp = (L.nth res (l1+i)) in
                  if exp <> 0 then 
                  (
                        rightlist := Exp((L.nth compt i).ge_id, -exp)::!rightlist;
                  )
                done;
                (* let poly = {ge_id=None; ge_group=None; ge_rpoly=poly} in *)
                let rightside = if (L.length !rightlist = 0) then Identity  else Multiply(!rightlist) in 
                let ckt = PPE(leftside, rightside) in 
                let isidentity = PPE(Multiply(!leftlist), Identity) in 
                let pi1 = transferpoly problem k in 
                let pi2 = updateforzero problem !poly in
                (* F.fprintf Format.std_formatter "substitutezero %a\n" RP.pp !poly; *)

                F.fprintf Format.std_formatter "\n...."; 
                print_problem problem;
                F.fprintf Format.std_formatter "\nrule 3 applied on %a = %a. isidentity := %a      C := %a" pp_fid  untrusted_poly.ge_id RP.pp untrusted_poly.ge_rpoly pp_circuit isidentity pp_circuit ckt;
                F.fprintf Format.std_formatter "\n...."; 
                
                (true, isidentity, ckt, pi1, pi2)
            )
            else
            (
                (false, EMPTY, EMPTY, problem, problem)
            )





let isidentityppe sts poly completion = 
    let (basis, matrix) = get_vector_repr (poly::completion) in 
    let matrix = L.tl matrix in 
            (* F.fprintf Format.std_formatter "\nTook %fs time to compute basis. Size of trusted set = %d. Size of reduced completion list = %d. No. of monomials = %d. Solving equation of form x.M = v where x is the required coefficient vector and dimensions of M = %d*%d.\n" (Unix.gettimeofday() -. time) (L.length !trusted) (L.length compt) (L.length (L.nth matrix 0)) (L.length matrix) (L.length (L.nth matrix 0)); *)     
    let vec = rp_to_vector basis poly.ge_rpoly in 
    let time  = Unix.gettimeofday() in 
    let res = Sage_Solver.lin_solve ~sts:sts matrix vec in 
            (* F.fprintf Format.std_formatter "Took %fs time to solve\n" (Unix.gettimeofday() -. time);  *)
    match res with
    | Some(x) -> 
        let leftsidelist = ref [] in 
        let l = L.length x in
        for i = 0 to (l-1) do
            let exp = (L.nth x i) in
            if exp <> 0 then
            (
                leftsidelist := Exp((L.nth completion i).ge_id, exp)::!leftsidelist; 
            )
        done;
        let isidentity = PPE(Multiply(!leftsidelist), Identity) in 
        (true, isidentity)
    | None -> (false, EMPTY)
(* 

let rule4 sts problem k = 
    (* F.fprintf Format.std_formatter "\nEntered Rule 4"; *)
    let untrusted_poly = (L.nth problem.ppe_untrusted k) in
    let vars_in_trusted = RP.vars_of_list (L.map (fun ge -> ge.ge_rpoly) problem.ppe_trusted) in
    let vars_in_given = RP.vars untrusted_poly.ge_rpoly in
    let new_vars = L.filter (fun var -> not (L.mem var vars_in_trusted)) vars_in_given in
    if L.length new_vars <> 1 then 
        (false, EMPTY, problem, problem)
    else
        let new_var = (L.nth new_vars 0) in
        if not (RP.has_power untrusted_poly.ge_rpoly new_var [1;3;5;7;11;13;17;19]) then 
            (false, EMPTY, problem, problem)
        else
        (
            (* F.fprintf Format.std_formatter "\nProcessing untrusted polynomial F%d = %a by rule2\n" (extract_fid untrusted_poly.ge_id) RP.pp untrusted_poly.ge_rpoly; *)
            let (coeff_poly, remainder_poly) = RP.coeff_remainder_poly untrusted_poly.ge_rpoly new_var in 
            let coeff_poly_ge = {ge_group = None; ge_id = Param(-1); ge_rpoly = coeff_poly} in

            let source_group = L.find (fun g -> (g <> problem.ppe_cgs.cgs_target)) (Ss.elements problem.ppe_cgs.cgs_gids) in
            let (completionSrc,_) = completion_for_group problem.ppe_cgs source_group problem.ppe_trusted in 
            let (success, isidentity) = isidentityppe sts coeff_poly_ge completionSrc in 
            let (success, isidentity) = if success then 
                                                (success, isidentity)
                                        else 
                                        isidentityppe sts coeff_poly_ge problem.completionGt in 
            if success then 
                let pi1 = transferpoly problem k in 
                let pi2 = updateforzero problem coeff_poly in 

                F.fprintf Format.std_formatter "\n...."; 
                print_problem problem;
                F.fprintf Format.std_formatter "\nrule 4 applied on %a = %a and variable %s. isidentity := %a" pp_fid untrusted_poly.ge_id RP.pp untrusted_poly.ge_rpoly new_var pp_circuit isidentity;
                F.fprintf Format.std_formatter "\n...."; 
                
                (true, isidentity, pi1, pi2) 
            else 
                (false, EMPTY, problem, problem)


 (*            let (basis, matrix) = get_vector_repr (coeff_poly_ge::problem.completionGt) in 
            let matrix = L.tl matrix in 
            (* F.fprintf Format.std_formatter "\nTook %fs time to compute basis. Size of trusted set = %d. Size of reduced completion list = %d. No. of monomials = %d. Solving equation of form x.M = v where x is the required coefficient vector and dimensions of M = %d*%d.\n" (Unix.gettimeofday() -. time) (L.length !trusted) (L.length compt) (L.length (L.nth matrix 0)) (L.length matrix) (L.length (L.nth matrix 0)); *)     
            let vec = rp_to_vector basis coeff_poly in 
            (* pp_coeff_vector vec; *)
            (* F.fprintf Format.std_formatter "\nResult\n"; *)
            let time  = Unix.gettimeofday() in 
            let res = Sage_Solver.lin_solve ?sts:sts matrix vec in 
            (* F.fprintf Format.std_formatter "Took %fs time to solve\n" (Unix.gettimeofday() -. time);  *)
            match res with
                | Some(x) -> 
                                    (* F.fprintf Format.std_formatter "\nRule4 after res"; *)

                    let leftsidelist = ref [] in 
                    let l = L.length x in
                    let first = ref true in
                    for i = 0 to (l-1) do
                        let exp = (L.nth x i) in
                        if exp <> 0 then
                        (
                            leftsidelist := Exp((L.nth problem.completionGt i).ge_id, exp)::!leftsidelist; 
                        )
                    done;
                    let isidentity = PPE(Multiply(!leftsidelist), Identity) in 
                  let pi1 = transferpoly problem k in 
                    let pi2 = updateforzero problem coeff_poly in 

                    F.fprintf Format.std_formatter "\n...."; 
                    print_problem problem;
                    F.fprintf Format.std_formatter "\nrule 4 applied on F%d = %a and variable %s. isidentity := %a" (extract_fid untrusted_poly.ge_id) RP.pp untrusted_poly.ge_rpoly new_var pp_circuit isidentity;
                    F.fprintf Format.std_formatter "\n...."; 
                    
                    (true, isidentity, pi1, pi2) 
                | None -> (false, EMPTY, problem, problem) *)
        )
   *)



(* 
let rule5 sts problem k = 
    (* F.fprintf Format.std_formatter "\nEntered Rule 5"; *)
    let untrusted_poly = (L.nth problem.ppe_untrusted k) in
    let vars_in_trusted = RP.vars_of_list (L.map (fun ge -> ge.ge_rpoly) problem.ppe_trusted) in
    let vars_in_given = RP.vars untrusted_poly.ge_rpoly in
    let new_vars = L.filter (fun var -> not (L.mem var vars_in_trusted)) vars_in_given in
    if L.length new_vars <> 2 then 
        (false, EMPTY, EMPTY, problem, problem)
    else
        let var1 = (L.nth new_vars 0) in
        let var2 = (L.nth new_vars 1) in 
        if (not (RP.has_power untrusted_poly.ge_rpoly var1 [1;3;5])) || (not (RP.has_power untrusted_poly.ge_rpoly var2 [1;3;5])) then 
            (false, EMPTY, EMPTY, problem, problem)
        else
        (
            (* F.fprintf Format.std_formatter "\nProcessing untrusted polynomial F%d = %a by rule2\n" (extract_fid untrusted_poly.ge_id) RP.pp untrusted_poly.ge_rpoly; *)
            let coeff_poly1 = RP.coeff_poly untrusted_poly.ge_rpoly var1 in 
            let coeff_poly2 = RP.coeff_poly untrusted_poly.ge_rpoly var2 in 
            
            let coeff_poly1_ge = {ge_group = None; ge_id = Param(-1); ge_rpoly = coeff_poly1} in
            let coeff_poly2_ge = {ge_group = None; ge_id = Param(-1); ge_rpoly = coeff_poly2} in

            let source_group = L.find (fun g -> (g <> problem.ppe_cgs.cgs_target)) (Ss.elements problem.ppe_cgs.cgs_gids) in
            let (completionSrc,_) = completion_for_group problem.ppe_cgs source_group problem.ppe_trusted in 

            let (success1, isidentity1) = isidentityppe sts coeff_poly1_ge completionSrc in 
            let (success2, isidentity2) = isidentityppe sts coeff_poly2_ge completionSrc in 

            let (success1, isidentity1) = if success1 then 
                                            (success1, isidentity1)
                                        else 
                                            isidentityppe sts coeff_poly1_ge problem.completionGt in 

            let (success2, isidentity2) = if success2 then 
                                            (success2, isidentity2)
                                        else 
                                            isidentityppe sts coeff_poly2_ge problem.completionGt in 


            if success1 && success2 then
                let pi1 = transferpoly problem k in 
                let pi2 = updateforzero problem coeff_poly1 in 
                let pi2 = updateforzero pi2 coeff_poly2 in 

                F.fprintf Format.std_formatter "\n...."; 
                print_problem problem;
                F.fprintf Format.std_formatter "\nrule 5 applied on %a = %a and variables %s, %s.  isidentity1 := %a      isidentity2 := %a   " pp_fid  untrusted_poly.ge_id RP.pp untrusted_poly.ge_rpoly var1 var2 pp_circuit isidentity1 pp_circuit isidentity2;
                F.fprintf Format.std_formatter "\n...."; 
                
                (true, isidentity1, isidentity2, pi1, pi2) 
            else 
                (false, EMPTY, EMPTY, problem, problem)
        )
 *)

(*checks if coefficient of var in untrusted_poly contains only vars_in_trusted *)
let isfixedcoefficient untrusted_poly var vars_in_trusted = 
    let (coeff_poly, remainder_poly) = RP.coeff_remainder_poly untrusted_poly var in
    let vars_in_coeff = RP.vars coeff_poly in
    let coeff_vars_not_in_trusted = L.filter (fun var -> not (L.mem var vars_in_trusted)) vars_in_coeff in
    if L.length coeff_vars_not_in_trusted = 0 then true else false

let rule4 sts problem k = 
    let untrusted_poly = (L.nth problem.ppe_untrusted k) in
    let vars_in_trusted = RP.vars_of_list (L.map (fun ge -> ge.ge_rpoly) problem.ppe_trusted) in
    let vars_in_given = RP.vars untrusted_poly.ge_rpoly in
    let new_vars = L.filter (fun var -> not (L.mem var vars_in_trusted)) vars_in_given in
    if L.length new_vars = 0 then 
        (false, EMPTY, problem, problem)
    else
        let valid_vars = L.filter (fun var -> RP.has_power untrusted_poly.ge_rpoly var [1;3;5;7;11;13;17;19]) new_vars in
        if L.length valid_vars = 0 then
            (false, EMPTY, problem, problem)
        else
        (
            let valid_vars = L.filter (fun var -> isfixedcoefficient untrusted_poly.ge_rpoly var vars_in_trusted) valid_vars in 
            if L.length valid_vars = 0 then
                (false, EMPTY, problem, problem)
            else
                let new_var = (L.nth valid_vars 0) in
                (* F.fprintf Format.std_formatter "\nProcessing untrusted polynomial F%d = %a by rule2\n" (extract_fid untrusted_poly.ge_id) RP.pp untrusted_poly.ge_rpoly; *)
                let (coeff_poly, remainder_poly) = RP.coeff_remainder_poly untrusted_poly.ge_rpoly new_var in 
                let coeff_poly_ge = {ge_group = None; ge_id = Param(-1); ge_rpoly = coeff_poly} in

                let source_group = L.find (fun g -> (g <> problem.ppe_cgs.cgs_target)) (Ss.elements problem.ppe_cgs.cgs_gids) in
                let (completionSrc,_) = completion_for_group problem.ppe_cgs source_group problem.ppe_trusted in 
                let (success, isidentity) = isidentityppe sts coeff_poly_ge completionSrc in 
                let (success, isidentity) = if success then 
                                                    (success, isidentity)
                                            else 
                                            isidentityppe sts coeff_poly_ge problem.completionGt in 
                if success then 
                    let pi1 = transferpoly problem k in 
                    let pi2 = updateforzero problem coeff_poly in 

                    F.fprintf Format.std_formatter "\n...."; 
                    print_problem problem;
                    F.fprintf Format.std_formatter "\nrule 4 applied on %a = %a and variable %s. isidentity := %a" pp_fid  untrusted_poly.ge_id RP.pp untrusted_poly.ge_rpoly new_var pp_circuit isidentity;
                    F.fprintf Format.std_formatter "\n...."; 
                    
                    (true, isidentity, pi1, pi2) 
                else 
                    (false, EMPTY, problem, problem)
        )


