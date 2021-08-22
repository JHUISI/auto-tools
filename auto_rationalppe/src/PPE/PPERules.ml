
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
                        (* let result = RP.substitutezero poly f.ge_rpoly in *)
                        (* F.fprintf Format.std_formatter "\nzeropoly = %a, f = %a, result = %a" RP.pp poly RP.pp f.ge_rpoly RP.pp result; *)
                        {f with ge_rpoly = (RP.substitutezero poly f.ge_rpoly); ge_rdenom = (RP.substitutezero poly f.ge_rdenom)}
                        ) problem.ppe_trusted} in 
    let problem = {problem with ppe_untrusted = L.map (fun f -> 
                        (* let result = RP.substitutezero poly f.ge_rpoly in *)
                        (* F.fprintf Format.std_formatter "\nzeropoly = %a, f = %a, result = %a" RP.pp poly RP.pp f.ge_rpoly RP.pp result; *)
                        {f with ge_rpoly = (RP.substitutezero poly f.ge_rpoly); ge_rdenom = (RP.substitutezero poly f.ge_rdenom)}
                    ) problem.ppe_untrusted}
    in 

    (* let problem = {problem with ppe_trusted = L.map (fun f -> {f with ge_rpoly = RP.substitutezero poly f.ge_rpoly}) problem.ppe_trusted} in  *)
    (* let problem = {problem with ppe_untrusted = L.map (fun f -> {f with ge_rpoly = RP.substitutezero poly f.ge_rpoly}) problem.ppe_untrusted} in  *)

(*     let fixedlist = RP.vars_of_list (L.map (fun ge -> ge.ge_rpoly) problem.ppe_trusted) in
    let problem = {problem with ppe_fixed = L.map (fun var -> {ge_id=Param(-1); ge_group=None; ge_rpoly=RP.var var}) fixedlist} in  *)
    let success = not (L.exists (fun f -> RP.equal f.ge_rdenom RP.zero) (problem.ppe_trusted@problem.ppe_untrusted)) in
    if not success then
        (false, problem)
    else
        let (completion,_) = completion_for_group problem.ppe_cgs problem.ppe_cgs.cgs_target problem.ppe_trusted in 
        let (normcompletion, commondnm) = normalize completion in 
        let problem = {problem with completionGt = completion; normcompletionGt = normcompletion; commondenom = commondnm} in 
        (true, problem)



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

let get_result_vector res left_side_count = 
    (*For each vector in result, including the number of non-zero values in the vector*)
    let res = L.map ( fun vec ->  (L.fold_left (fun acc ele -> if ele = 0 then acc else acc + 1) 0 (last_elements vec left_side_count), vec)  ) res in 
    (*Get the vector with smallest number of non-zero values *)
    let (acc, vec) = L.fold_left ( fun (min, minvec) (count, vec) ->  if (min = -1) || (min > count) then (count, vec) 
                                                                    else (min, minvec)
                                ) (-1,[]) res in 
    vec


(*     if L.exists (fun ele -> not (RP.equal lst.ge_rdenom RP.one) ) lst
        L.mapi (fun i ele -> ) lst

    else
        lst
 *)    

(* let rule1sourcegroup (sts:st_sage) problem k = 
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
 *)

let comparewithzero (sts:st_sage) leftelement rightelements = 
(*     F.fprintf Format.std_formatter "\nRight elements before: ";
    L.iter(fun f-> F.fprintf Format.std_formatter ",   %a/%a " RP.pp f.ge_rpoly RP.pp f.ge_rdenom) rightelements;
 *)    let (l, rightelements) = optimize [leftelement] rightelements in 
(*     F.fprintf Format.std_formatter "\nEntered comparewithzero %a/%a" RP.pp leftelement.ge_rpoly RP.pp leftelement.ge_rdenom;
    L.iter(fun f-> F.fprintf Format.std_formatter ",   %a/%a " RP.pp f.ge_rpoly RP.pp f.ge_rdenom) rightelements;
 *)    if (L.length l) = 0 then
    (
        (* F.fprintf Format.std_formatter "\nRule not applied at optimization phase\n"; *)
        (false, EMPTY)
    )
    else if (L.length rightelements) = 0 then
    (
        (* F.fprintf Format.std_formatter "\nRule applied at optimization phase\n";     *)
        (true, NOT(PPE(leftelement.ge_id, Identity)))
        (* let ckt = PPE(leftelement.ge_id, Identity) in
        F.fprintf Format.std_formatter "\n...."; 
        print_problem problem;
        F.fprintf Format.std_formatter "\nrule 1 applied to %a = %a.     C := %a" pp_fid untrusted_poly.ge_id RP.pp untrusted_poly.ge_rpoly pp_circuit ckt;
        F.fprintf Format.std_formatter "\n...."; 
        (true, ckt, transferpoly problem k) *)
    )
    else
        let time = Unix.gettimeofday() in
        let (basis, matrix) = get_vector_repr (leftelement::rightelements) in
        let matrix = L.tl matrix in
        (* F.fprintf Format.std_formatter "\nTook %fs time to compute basis. Size of trusted set = %d. Size of reduced completion list = %d. No. of monomials = %d. Solving equation of form x.M = v where x is the required coefficient vector and dimensions of M = %d*%d.\n" (Unix.gettimeofday() -. time) (L.length !trusted) (L.length compt) (L.length (L.nth matrix 0)) (L.length matrix) (L.length (L.nth matrix 0)); *) 
        let vec = rp_to_vector basis leftelement.ge_rpoly in
        let time  = Unix.gettimeofday() in
        let res = Sage_Solver.lin_solve ~sts:sts matrix vec in
        F.fprintf Format.std_formatter "\nCompare with Identity. Took %fs time to solve\n" (Unix.gettimeofday() -. time); 
        match res with
        | Some(x) -> 
            (* F.fprintf Format.std_formatter "\nRule1 after res"; *)
            let rightlist = ref [] in 
            let l = L.length x in
            for i = 0 to (l-1) do
                let exp = (L.nth x i) in
                if exp <> 0 then
                (
                   rightlist := Exp((L.nth rightelements i).ge_id, exp)::!rightlist; 
                )
            done;
            if (L.length !rightlist = 0) then
                (false, EMPTY)
            else 
                let rightside = Multiply(!rightlist) in 
                (* let rightside = Multiply(!rightlist) in  *)
                let ckt = NOT(PPE(rightside,Identity)) in 
                (true, ckt)


let rule1 (sts:st_sage) problem k = 
    (* F.fprintf Format.std_formatter "\nEntered Rule 1"; *)
    let untrusted_ele = (L.nth problem.ppe_untrusted k) in
    let vars_in_trusted = RP.vars_of_list ((L.map (fun ge -> ge.ge_rpoly) problem.ppe_trusted)@(L.map (fun ge -> ge.ge_rdenom) problem.ppe_trusted)) in
    let vars_in_given = (RP.vars untrusted_ele.ge_rpoly)@(RP.vars untrusted_ele.ge_rdenom) in
    if (L.exists (fun var -> not (L.mem var vars_in_trusted)) vars_in_given) then
        (false, EMPTY, problem)
    else
    (
        F.fprintf Format.std_formatter "\nChecking for rule 1. Untrusted poly = %a/%a." RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom;
        print_newline();
        (* F.fprintf Format.std_formatter "\nEntered rule 11."; *)
        (* let (success, ckt, pi) = rule1sourcegroup sts problem k in 
        if success then 
            (success, ckt, pi)
        else *)
            let compt = problem.completionGt in 
            (* F.fprintf Format.std_formatter "\nCompletion GT\n";
            L.iter (fun f -> F.fprintf Format.std_formatter "%a/%a, " RP.pp f.ge_rpoly RP.pp f.ge_rdenom) compt;
 *)
            (* let (normalizedcompt, commondenom) = normalize compt in *)
            let normalizedcompt = problem.normcompletionGt in 
            let commondenom = problem.commondenom in 

(*             F.fprintf Format.std_formatter "\nnormalized Completion GT\n";
            L.iter (fun f -> F.fprintf Format.std_formatter "%a/%a, " RP.pp f.ge_rpoly RP.pp f.ge_rdenom) normalizedcompt;
 *) 
            let time = Unix.gettimeofday() in 
            let leftelements = {untrusted_ele with ge_rpoly = (RP.mult untrusted_ele.ge_rpoly commondenom); ge_rdenom = RP.one} in
            let rightelements = L.map (fun element -> {element with ge_rpoly = RP.mult element.ge_rpoly untrusted_ele.ge_rdenom; ge_rdenom = RP.one}) normalizedcompt in

(*             F.fprintf Format.std_formatter "\nCommon denominator %a\n" RP.pp commondenom;
            F.fprintf Format.std_formatter "Before Left elements\n";
            F.fprintf Format.std_formatter "%a " RP.pp leftelements.ge_rpoly;
            F.fprintf Format.std_formatter "\nBefore Right elements\n";
            L.iter (fun f -> F.fprintf Format.std_formatter "%a, " RP.pp f.ge_rpoly) rightelements;
 *)
            let (l, rightelements) = optimize [leftelements] rightelements in 
            (* F.fprintf Format.std_formatter "\nRule1 Took %f sec to optimize" (Unix.gettimeofday() -. time); *)
            
(*             F.fprintf Format.std_formatter "Left elements\n";
            F.fprintf Format.std_formatter "%a " RP.pp leftelements.ge_rpoly;
            F.fprintf Format.std_formatter "\nRight elements\n";
            L.iter (fun f -> F.fprintf Format.std_formatter "%a, " RP.pp f.ge_rpoly) rightelements;
 *)
            if (L.length l) = 0 then
            (
                (* F.fprintf Format.std_formatter "\nRule not applied at optimization phase\n"; *)
                (false, EMPTY, problem)
            )
            else if (L.length rightelements) = 0 then
            (
                let ckt = PPE(untrusted_ele.ge_id, Identity) in
                F.fprintf Format.std_formatter "\n...."; 
                print_problem problem;
                F.fprintf Format.std_formatter "\nRule 1 applied to %a = %a/%a.     C := %a" pp_fid untrusted_ele.ge_id RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom pp_circuit ckt;
                F.fprintf Format.std_formatter "\n...."; 
                (true, ckt, transferpoly problem k)
            )
            else
            (
(*                 F.fprintf Format.std_formatter "\n Completion list: ";
                L.iter (fun f -> F.fprintf Format.std_formatter "\n%a/%a in %a G%s" RP.pp f.ge_rpoly RP.pp f.ge_rdenom pp_recipe f.ge_id (extract_group f.ge_group)) compt;
 *)                let time = Unix.gettimeofday() in
                let (basis, matrix) = get_vector_repr (leftelements::rightelements) in
                let matrix = L.tl matrix in
                (* F.fprintf Format.std_formatter "\nTook %fs time to compute basis. Size of trusted set = %d. Size of reduced completion list = %d. No. of monomials = %d. Solving equation of form x.M = v where x is the required coefficient vector and dimensions of M = %d*%d.\n" (Unix.gettimeofday() -. time) (L.length !trusted) (L.length compt) (L.length (L.nth matrix 0)) (L.length matrix) (L.length (L.nth matrix 0)); *) 
                let vec = rp_to_vector basis leftelements.ge_rpoly in
                let time  = Unix.gettimeofday() in
                let res = Sage_Solver.lin_solve ~sts:sts matrix vec in
                F.fprintf Format.std_formatter "\nChecking for Rule 1. Took %fs time to solve\n" (Unix.gettimeofday() -. time); 
                print_newline();
                match res with
                | Some(x) -> 
                    F.fprintf Format.std_formatter "\nRule 1 after res";
                    let rightlist = ref [] in 
                    let l = L.length x in
                    for i = 0 to (l-1) do
                        let exp = (L.nth x i) in
                        if exp <> 0 then
                        (
                           rightlist := Exp((L.nth rightelements i).ge_id, exp)::!rightlist; 
                        )
                    done;
                    let e = L.nth problem.ppe_cgs.cgs_emaps 0 in
                    let leftside = if extract_group untrusted_ele.ge_group = problem.ppe_cgs.cgs_target then 
                                        untrusted_ele.ge_id
                                    else
                                        Emap(e, [untrusted_ele.ge_id; Param(0)])
                                    in 
                    let rightside = if (L.length !rightlist = 0) then Identity  else Multiply(!rightlist) in 
                    (* let rightside = Multiply(!rightlist) in  *)
                    let ckt = PPE(leftside, rightside) in 
                    
                    print_newline();
                    if RP.equal untrusted_ele.ge_rdenom RP.one then
                    (
                        let time = Unix.gettimeofday() in
                        let pi = transferpoly problem k in 
                        F.fprintf Format.std_formatter "\nTransferring poly took %fs" (Unix.gettimeofday() -. time); 
                        print_problem problem;
                        F.fprintf Format.std_formatter "\nRule 1 applied to %a = %a/%a.     C := %a" pp_fid untrusted_ele.ge_id RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom pp_circuit ckt;
                        print_newline(); 
                        (true, ckt, pi)
                    )
                    else 
                    (
                        let time  = Unix.gettimeofday() in
                        F.fprintf Format.std_formatter "\nRule 1 after else";
                        let (compsrc,_) = completion_for_group problem.ppe_cgs (extract_group untrusted_ele.ge_group) problem.ppe_trusted in 
                        let compsrc = L.filter (fun f -> not (L.length f.ge_rpoly = 0)) compsrc in 
                        let (normalizedcompsrc, srccommondenom) = normalize compsrc in
                        let denom = {untrusted_ele with ge_rpoly = RP.mult untrusted_ele.ge_rdenom srccommondenom; ge_rdenom = RP.one} in
                        let rightelements = L.map (fun element -> {element with ge_rdenom = RP.one}) normalizedcompsrc in
                        F.fprintf Format.std_formatter "\nTook %fs time to compute compsrc" (Unix.gettimeofday() -. time);
                        print_newline();

                        let (success, denomckt) = comparewithzero sts denom rightelements in 
                        if success then
                        (
                            let pi = transferpoly problem k in 
                            F.fprintf Format.std_formatter "\n...."; 
                            print_problem problem;
                            F.fprintf Format.std_formatter "\nRule 1 applied s to %a = %a/%a.     C := %a" pp_fid untrusted_ele.ge_id RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom pp_circuit (AND(ckt, denomckt));
                            print_newline();    
                            (true, AND(ckt, denomckt), pi)
                            
                        )
                        else
                        (
                            let denom = {untrusted_ele with ge_rpoly = RP.mult untrusted_ele.ge_rdenom commondenom; ge_rdenom = RP.one} in
                            let rightelements = L.map (fun element -> {element with ge_rdenom = RP.one}) normalizedcompt in
                            let (success, denomckt) = comparewithzero sts denom rightelements in 
                            
                            if success then
                            (
                                let pi = transferpoly problem k in 
                                F.fprintf Format.std_formatter "\n...."; 
                                print_problem problem;
                                F.fprintf Format.std_formatter "\nRule 1 applied t o %a = %a/%a.     C := %a" pp_fid untrusted_ele.ge_id RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom pp_circuit (AND(ckt, denomckt));
                                F.fprintf Format.std_formatter "\n...."; 
                                (true, AND(ckt, denomckt), pi)
                            )
                            else                       
                                (false, EMPTY, problem)
                        )
                    )                
               | None -> (false, EMPTY, problem)
                    (* (F.fprintf Format.std_formatter "Rule not applied\n"; 
                          changed
                    ) *)
            )
    )
    
















let rule2 sts problem k = 
    (* F.fprintf Format.std_formatter "\nEntered Rule 3"; *)
    let untrusted_ele = (L.nth problem.ppe_untrusted k) in
    let vars_in_trusted = RP.vars_of_list ((L.map (fun ge -> ge.ge_rpoly) problem.ppe_trusted)@(L.map (fun ge -> ge.ge_rdenom) problem.ppe_trusted)) in
    let vars_in_given = RP.vars (untrusted_ele.ge_rpoly@untrusted_ele.ge_rdenom) in

    if (L.exists (fun var -> not (L.mem var vars_in_trusted)) vars_in_given) || (extract_group untrusted_ele.ge_group = problem.ppe_cgs.cgs_target) then 
        (false, EMPTY, EMPTY, problem, problem, false)
    else
    (
        F.fprintf Format.std_formatter "\nChecking for rule 2. Untrusted poly = %a/%a." RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom;
        print_newline();
        let other_group = try L.find (fun g -> (g <> problem.ppe_cgs.cgs_target) && (g <> extract_group untrusted_ele.ge_group)) (Ss.elements problem.ppe_cgs.cgs_gids)
                          with Not_found -> extract_group untrusted_ele.ge_group in 
        let compt = problem.completionGt in 
        let (compo,_) = completion_for_group problem.ppe_cgs other_group problem.ppe_trusted in 
        (* let compt = L.filter (fun f -> not (L.length f.ge_rpoly = 0)) compt (*Filtering out zero polynomials to avoid trivial PPEs*) *)
        let compo = L.filter (fun f -> not (L.length f.ge_rpoly = 0)) compo in 
        (* let ftimescompo = L.map (fun h -> {ge_id = h.ge_id; ge_group = None; ge_rpoly = RP.mult h.ge_rpoly untrusted_poly.ge_rpoly}) compo in *)
        let (normalizedcompo, leftcommondenom) = normalize compo in
        let normalizedcompt = problem.normcompletionGt in 
        let rightcommondenom = problem.commondenom in 
        (* let (normalizedcompt, rightcommondenom) = normalize compt in *)

        let leftelements = L.mapi (fun index h -> {ge_id = Param(index); ge_group = None; ge_rpoly = RP.mult (RP.mult h.ge_rpoly untrusted_ele.ge_rpoly) rightcommondenom; ge_rdenom = RP.one}) normalizedcompo in (*This is a hack. storing ge_id as Param(index in compo)*)
        (* let ftimescompo = L.mapi (fun index h -> {ge_id = Param(index); ge_group = None; ge_rpoly = RP.mult h.ge_rpoly untrusted_poly.ge_rpoly}) compo in (*This is a hack. storing ge_id as Param(index in compo)*) *)
        let rightelements = L.mapi (fun index h -> {h with ge_rpoly = RP.mult (RP.mult h.ge_rpoly untrusted_ele.ge_rdenom) leftcommondenom; ge_rdenom = RP.one}) normalizedcompt in

        let time = Unix.gettimeofday() in 
(*         F.fprintf Format.std_formatter "Before Left elements\n";
        L.iter (fun f -> F.fprintf Format.std_formatter "%a, " RP.pp f.ge_rpoly) leftelements;
        F.fprintf Format.std_formatter "\nBefore Right elements\n";
        L.iter (fun f -> F.fprintf Format.std_formatter "%a, " RP.pp f.ge_rpoly) rightelements;
 *)
        let (leftelements, rightelements) = optimize leftelements rightelements in 
        (* F.fprintf Format.std_formatter "\nChecking for Rule 3. Took %fs time to optimize" (Unix.gettimeofday() -. time);  *)

(*         F.fprintf Format.std_formatter "Left elements\n";
        L.iter (fun f -> F.fprintf Format.std_formatter "%a, " RP.pp f.ge_rpoly) leftelements;
        F.fprintf Format.std_formatter "\nRight elements\n";
        L.iter (fun f -> F.fprintf Format.std_formatter "%a, " RP.pp f.ge_rpoly) rightelements;
 *)
        if L.length leftelements = 0 then
            (false, EMPTY, EMPTY, problem, problem, false)
        else
        (
(*             F.fprintf Format.std_formatter "\n Completion list: ";
            L.iter (fun f -> F.fprintf Format.std_formatter "\n%a/%a %a in G%s" RP.pp f.ge_rpoly RP.pp f.ge_rdenom pp_recipe f.ge_id (extract_group f.ge_group)) compt;
 *)
            let l1 = L.length leftelements in
            let l2 = L.length rightelements in
            let time = Unix.gettimeofday() in
            let polys = leftelements@rightelements in
            let (basis, matrix) = get_vector_repr polys in  
             F.fprintf Format.std_formatter "\nChecking for Rule 2. Took %fs to compute basis. Size of reduced f.(completion list of G1) U (completion list of GT) = %d. No. of monomials = %d. 
              Solving equation of form x.M = 0, where x is the required coefficient vector and dimensions of M = %d*%d" (Unix.gettimeofday() -. time) (L.length polys) (L.length (L.nth matrix 0)) (L.length matrix) (L.length (L.nth matrix 0));
            print_newline();
            let time = Unix.gettimeofday() in 
            let res = Sage_Solver.compute_kernel ~sts:sts matrix in
            F.fprintf Format.std_formatter "Checking for Rule 2. Took %fs time to solve" (Unix.gettimeofday() -. time); 
            print_newline();
            if L.length res <> 0 && L.exists (fun vec -> if_valid_result leftelements normalizedcompo vec l1) res then 
            (
                let leftlist = ref [] in 
                let poly = ref [] in 
                let res = get_result_vector (L.filter (fun vec -> if_valid_result leftelements normalizedcompo vec l1) res) l1 in 
                (* let res = get_result_vector (L.filter (fun vec -> if_not_zeros vec l1) res) l1 in  *)
                for i = 0 to (l1-1) do
                    let exp = (L.nth res i) in
                    if exp <> 0 then
                    (
                        let index = extract_fid (L.nth leftelements i).ge_id in
                        leftlist := Exp((L.nth compo index).ge_id, exp)::!leftlist;
                        poly := RP.add !poly (RP.mult (RP.const (IntRing.from_int exp)) (L.nth normalizedcompo index).ge_rpoly);  
                    )
                done;
                let e = L.nth problem.ppe_cgs.cgs_emaps 0 in
                let leftside = Emap(e, [untrusted_ele.ge_id; Multiply(!leftlist)]) in 
                
                let rightlist = ref [] in
                for i = 0 to (l2-1) do
                  let exp = (L.nth res (l1+i)) in
                  if exp <> 0 then 
                  (
                        rightlist := Exp((L.nth rightelements i).ge_id, -exp)::!rightlist;
                  )
                done;
                (* let poly = {ge_id=None; ge_group=None; ge_rpoly=poly} in *)
                let rightside = if (L.length !rightlist = 0) then Identity  else Multiply(!rightlist) in 
                let ckt = PPE(leftside, rightside) in 
                let isidentity = PPE(Multiply(!leftlist), Identity) in 

                
                if RP.equal untrusted_ele.ge_rdenom RP.one then
                (
                    let pi1 = transferpoly problem k in 
                    let (substitutesucess, pi2) = updateforzero problem !poly in
                    F.fprintf Format.std_formatter "\nsubstitutezero %a. Substitute success = %b\n" RP.pp !poly substitutesucess;
                    print_newline();

                    F.fprintf Format.std_formatter "\n...."; 
                    print_problem problem;
                    F.fprintf Format.std_formatter "\nRule 2 applied on %a = %a/%a. isidentity := %a      C := %a" pp_fid  untrusted_ele.ge_id RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom pp_circuit isidentity pp_circuit ckt;
                    F.fprintf Format.std_formatter "\n...."; 
                    (true, isidentity, ckt, pi1, pi2, substitutesucess)
                )
                else 
                (
                    let denom = {untrusted_ele with ge_rpoly = RP.mult untrusted_ele.ge_rdenom leftcommondenom; ge_rdenom = RP.one} in
                    let rightelements = L.map (fun element -> {element with ge_rdenom = RP.one}) normalizedcompo in 
                    let (success, denomckt) = comparewithzero sts denom rightelements in 
                    if success then
                    ( 
                        let pi1 = transferpoly problem k in 
                        let (substitutesucess, pi2) = updateforzero problem !poly in
                        F.fprintf Format.std_formatter "\nsubstitutezero %a. Substitute success = %b\n" RP.pp !poly substitutesucess;
                        print_newline();

                        F.fprintf Format.std_formatter "\n....";
                        print_problem problem;
(*                         print_problem pi1;
                        print_problem pi2; *)
                        F.fprintf Format.std_formatter "\nRule 2 applied on %a = %a/%a. isidentity := %a      C := %a" pp_fid  untrusted_ele.ge_id RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom pp_circuit isidentity pp_circuit (AND(ckt, denomckt));
                        F.fprintf Format.std_formatter "\n....";
                        (true, isidentity, AND(ckt, denomckt), pi1, pi2, substitutesucess)
                    )
                    else
                    (
                        let (compsrc,_) = completion_for_group problem.ppe_cgs (extract_group untrusted_ele.ge_group) problem.ppe_trusted in 
                        let compsrc = L.filter (fun f -> not (L.length f.ge_rpoly = 0)) compsrc in 
                        let (normalizedcompsrc, srccommondenom) = normalize compsrc in
                        let denom = {untrusted_ele with ge_rpoly = RP.mult untrusted_ele.ge_rdenom srccommondenom; ge_rdenom = RP.one} in
                        let rightelements = L.map (fun element -> {element with ge_rdenom = RP.one}) normalizedcompsrc in
                        
                        let (success, denomckt) = comparewithzero sts denom rightelements in 
                        if success then
                        (
                            let pi1 = transferpoly problem k in 
                            let (substitutesucess, pi2) = updateforzero problem !poly in
                            F.fprintf Format.std_formatter "\nsubstitutezero %a. Substitute success = %b\n" RP.pp !poly substitutesucess;
                            print_newline();
                            F.fprintf Format.std_formatter "\n....";
                            print_problem problem;
    (*                         print_problem pi1;
                            print_problem pi2; *)
                            F.fprintf Format.std_formatter "\nRule 2 applied on %a = %a/%a. isidentity := %a      C := %a" pp_fid  untrusted_ele.ge_id RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom pp_circuit isidentity pp_circuit (AND(ckt, denomckt));
                            F.fprintf Format.std_formatter "\n....";
                            (true, isidentity, AND(ckt, denomckt), pi1, pi2, substitutesucess)
                        )
                        else
                        (
                            
                            let denom = {untrusted_ele with ge_rpoly = RP.mult untrusted_ele.ge_rdenom rightcommondenom; ge_rdenom = RP.one} in
                            let rightelements = L.map (fun element -> {element with ge_rdenom = RP.one}) normalizedcompt in
                            let (success, denomckt) = comparewithzero sts denom rightelements in 
                            if success then
                            (
                                let pi1 = transferpoly problem k in 
                                let (substitutesucess, pi2) = updateforzero problem !poly in
                                F.fprintf Format.std_formatter "\nsubstitutezero %a. Substitute success = %b\n" RP.pp !poly substitutesucess;
                                print_newline();
                                F.fprintf Format.std_formatter "\n....";
                                print_problem problem;
    (*                         print_problem pi1;
                                print_problem pi2; *)
                                F.fprintf Format.std_formatter "\nRule 2 applied on %a = %a/%a. isidentity := %a      C := %a" pp_fid  untrusted_ele.ge_id RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom pp_circuit isidentity pp_circuit (AND(ckt, denomckt));
                                F.fprintf Format.std_formatter "\n....";
                                (true, isidentity, AND(ckt, denomckt), pi1, pi2, substitutesucess)
                            )
                            else 
                                (false, EMPTY, EMPTY, problem, problem, false)
                        )
                    )
                )
            )
            else
            (
                (false, EMPTY, EMPTY, problem, problem, false)
            )
        )
    )
























(* 
let rule3 sts problem k = 
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
 *)



let isidentityppe sts poly completion = 
    if L.length poly = 0 then
        (false, EMPTY)
    else
        let poly = L.nth poly 0 in     
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


(*checks if coefficient of var in untrusted_poly contains only vars_in_trusted *)
let isfixedcoefficient untrusted_poly var vars_in_trusted = 
    let (coeff_poly, remainder_poly) = RP.coeff_remainder_poly untrusted_poly var in
    let vars_in_coeff = RP.vars coeff_poly in
    let coeff_vars_not_in_trusted = L.filter (fun var -> not (L.mem var vars_in_trusted)) vars_in_coeff in
    if L.length coeff_vars_not_in_trusted = 0 then true else false



let rule3 sts problem k = 
    (*numerator has an new variable. Denominator only has trusted variables*)
    let untrusted_ele = (L.nth problem.ppe_untrusted k) in
    F.fprintf Format.std_formatter "\nEntered rule3 for polynomial %a/%a" RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom;
    let vars_in_trusted = RP.vars_of_list ((L.map (fun ge -> ge.ge_rpoly) problem.ppe_trusted)@(L.map (fun ge -> ge.ge_rdenom) problem.ppe_trusted)) in
    let vars_in_given_num = RP.vars untrusted_ele.ge_rpoly in
    let vars_in_given_denom = RP.vars untrusted_ele.ge_rdenom in

    if (L.exists (fun var -> not (L.mem var vars_in_trusted)) vars_in_given_denom) then
        (false, EMPTY, EMPTY, problem, problem, false)
    else 
        let new_vars = L.filter (fun var -> not (L.mem var vars_in_trusted)) vars_in_given_num in
        if L.length new_vars = 0 then 
            (false, EMPTY, EMPTY, problem, problem, false)
        else
            let valid_vars = L.filter (fun var -> RP.has_power untrusted_ele.ge_rpoly var [1;3;5;7;11;13;17;19]) new_vars in
            let valid_vars = L.filter (fun var -> isfixedcoefficient untrusted_ele.ge_rpoly var vars_in_trusted) valid_vars in 
            if L.length valid_vars = 0 then
                (false, EMPTY, EMPTY, problem, problem, false)
            else
            (
                F.fprintf Format.std_formatter "\nChecking for rule 3. Untrusted poly = %a/%a." RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom;
                print_newline();
                let new_var = (L.nth valid_vars 0) in
                (* F.fprintf Format.std_formatter "\nProcessing untrusted polynomial F%d = %a by rule2\n" (extract_fid untrusted_poly.ge_id) RP.pp untrusted_poly.ge_rpoly; *)
                let (coeff_poly, remainder_poly) = RP.coeff_remainder_poly untrusted_ele.ge_rpoly new_var in 
                (* let source_group = L.find (fun g -> (g <> problem.ppe_cgs.cgs_target)) (Ss.elements problem.ppe_cgs.cgs_gids) in 
                let (completionSrc,_) = completion_for_group problem.ppe_cgs source_group problem.ppe_trusted in 
                let (normalizedcompletionSrc, completionSrcDenom) = normalize completionSrc in 

                     let (success, isidentity) = isidentityppe sts coeff_poly_ge completionSrc in 
                let (success, isidentity) = if success then 
                                                (success, isidentity)
                                            else  *)

                let time = Unix.gettimeofday() in
                let normalizedcompt = problem.normcompletionGt in
                let normalizedcomptdenom = problem.commondenom in 
                let coeff_poly_ge = {ge_group = None; ge_id = Param(-1); ge_rpoly = RP.mult coeff_poly normalizedcomptdenom; ge_rdenom = RP.one} in
                let denom_poly_ge = {ge_group = None; ge_id = Param(-1); ge_rpoly = RP.mult untrusted_ele.ge_rdenom normalizedcomptdenom; ge_rdenom = RP.one} in
            
                let (success1, isidentity) = if (RP.is_consts coeff_poly) then (true, REJECT) else
                (
                    let (l, rightelements) = optimize [coeff_poly_ge] normalizedcompt in 
                    (isidentityppe sts l rightelements) 
                ) in 
                let (success2, isdenomidentity) = if ((RP.is_consts untrusted_ele.ge_rdenom) && (not (RP.equal untrusted_ele.ge_rdenom RP.zero))) then (true, REJECT) else
                (
                    let (l, rightelements) = optimize [denom_poly_ge] normalizedcompt in 
                    (isidentityppe sts l rightelements)
                ) in

                F.fprintf Format.std_formatter "\nComputed Rule 3 circuits. Took %fs" (Unix.gettimeofday() -. time);
                print_newline();

                if (success1 && success2) then
                ( 
                    let time = Unix.gettimeofday() in 
                    let pi1 = transferpoly problem k in 
                    F.fprintf Format.std_formatter "\nRule3a Transferpoly took %fs" (Unix.gettimeofday() -. time);

                    let time = Unix.gettimeofday() in 
                    let (substitutesuccess, pi2) = if RP.is_consts coeff_poly then (false, problem) else updateforzero problem coeff_poly in 
                    F.fprintf Format.std_formatter "\n...."; 
                    print_problem problem;
                    F.fprintf Format.std_formatter "\nRule 3a applied on %a = %a/%a and variable %s. isidentity := %a, C := %a. Took %fs" pp_fid  untrusted_ele.ge_id RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom new_var pp_circuit isidentity pp_circuit (NOT(isdenomidentity)) (Unix.gettimeofday() -. time);
                    (* F.fprintf Format.std_formatter "\n....";  *)
                    print_newline();
                    if isdenomidentity = REJECT then (true, isidentity, ACCEPT, pi1, pi2, substitutesuccess) 
                    else (true, isidentity, NOT(isdenomidentity), pi1, pi2, substitutesuccess)
                )
                else 
                    (false, EMPTY, EMPTY, problem, problem, false)
            )




let rule4 sts problem k = 
    (*denominator has an new variable. numerator only has trusted variables*)
    let untrusted_ele = (L.nth problem.ppe_untrusted k) in

    let vars_in_trusted = RP.vars_of_list ((L.map (fun ge -> ge.ge_rpoly) problem.ppe_trusted)@(L.map (fun ge -> ge.ge_rdenom) problem.ppe_trusted)) in
    let vars_in_given_num = RP.vars untrusted_ele.ge_rpoly in
    let vars_in_given_denom = RP.vars untrusted_ele.ge_rdenom in

    if (L.exists (fun var -> not (L.mem var vars_in_trusted)) vars_in_given_num) then
        (false, EMPTY, EMPTY, problem, problem, false)
    else 
        let new_vars = L.filter (fun var -> not (L.mem var vars_in_trusted)) vars_in_given_denom in
        if L.length new_vars = 0 then 
            (false, EMPTY, EMPTY, problem, problem, false)
        else
            let valid_vars = L.filter (fun var -> RP.has_power untrusted_ele.ge_rdenom var [1;3;5;7;11;13;17;19]) new_vars in
            let valid_vars = L.filter (fun var -> isfixedcoefficient untrusted_ele.ge_rdenom var vars_in_trusted) valid_vars in 
            if L.length valid_vars = 0 then
                (false, EMPTY, EMPTY, problem, problem, false)
            else
            (
                F.fprintf Format.std_formatter "\nChecking for rule 4. Untrusted poly = %a/%a." RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom;

                let new_var = (L.nth valid_vars 0) in
                (* F.fprintf Format.std_formatter "\nProcessing untrusted polynomial F%d = %a by rule2\n" (extract_fid untrusted_poly.ge_id) RP.pp untrusted_poly.ge_rpoly; *)
                let (coeff_poly, remainder_poly) = RP.coeff_remainder_poly untrusted_ele.ge_rdenom new_var in
                (* let (normalizedcompt, normalizedcomptdenom) = normalize problem.completionGt in *)
                let normalizedcompt = problem.normcompletionGt in
                let normalizedcomptdenom = problem.commondenom in 

                let coeff_poly_ge = {ge_group = None; ge_id = Param(-1); ge_rpoly = RP.mult coeff_poly normalizedcomptdenom; ge_rdenom = RP.one} in
                let num_poly_ge = {ge_group = None; ge_id = Param(-1); ge_rpoly = RP.mult untrusted_ele.ge_rpoly normalizedcomptdenom; ge_rdenom = RP.one} in
    
            
                let (success1, isidentity) = if (RP.is_consts coeff_poly) then (true, REJECT) else 
                    (
                        let (l, rightelements) = optimize [coeff_poly_ge] normalizedcompt in 
                        (isidentityppe sts l rightelements)
                    ) in
                let (success2, isnumidentity) = if ((RP.is_consts untrusted_ele.ge_rpoly) && (not (RP.equal untrusted_ele.ge_rdenom RP.zero))) then (true, REJECT) 
                    else 
                    (
                        let (l, rightelements) = optimize [num_poly_ge] normalizedcompt in 
                        (isidentityppe sts l rightelements) 
                    ) in
(*                 let (success1, isidentity) = isidentityppe sts coeff_poly_ge normalizedcompt in
                let (success2, isnumidentity) = isidentityppe sts num_poly_ge normalizedcompt in
 *)
                if (success1 && success2) then
                (
                    let pi1 = transferpoly problem k in
                    let (substitutesuccess, pi2) = updateforzero problem coeff_poly in
                    let c = PPE(untrusted_ele.ge_id, Identity) in
                    let ckt = if isnumidentity = REJECT then ACCEPT else OR(NOT(isnumidentity), AND(isnumidentity,c)) in 

                    F.fprintf Format.std_formatter "\n...."; 
                    print_problem problem;
                    F.fprintf Format.std_formatter "\nRule 3b applied on %a = %a/%a and variable %s. isidentity := %a, C := %a" pp_fid untrusted_ele.ge_id RP.pp untrusted_ele.ge_rpoly RP.pp untrusted_ele.ge_rdenom new_var pp_circuit isidentity pp_circuit ckt;
                    F.fprintf Format.std_formatter "\n...."; 
                    
                    (true, isidentity, ckt, pi1, pi2, substitutesuccess) 
                )
                else 
                    (false, EMPTY, EMPTY, problem, problem, false)
            )