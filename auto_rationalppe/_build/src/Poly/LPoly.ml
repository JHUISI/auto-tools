(* This file is distributed under the MIT License (see LICENSE). *)

(*s Use [Var] and [Ring] types to define [MakePoly] functor.
    Also define [IntRing]. *)
(*i*)
open Util
open LPolyInterfaces
open Big_int
(*i*)

(* \hd{[Ring] instance for [int]} *)


module IntRing = struct
  type t = big_int
  let pp fmt i = F.fprintf fmt "%s" (string_of_big_int i)

  let add  = add_big_int
  let opp  = minus_big_int
  let mult = mult_big_int
  let one  = unit_big_int
  let zero = zero_big_int
  let rec ring_exp m n =
    if n > 0 then mult m (ring_exp m (n-1))
    else if n = 0 then one
    else failwith "Negative exponent in IntRing"
  let ladd cs = L.fold_left (fun acc c -> add c acc) zero cs
  let from_int i = big_int_of_int i
  let equal = eq_big_int
  let compare = compare_big_int
  let use_parens = false
end

(*********************************************************************)
(* \hd{Functor for Polynomials} *)

module MakePoly (V : Var) (C : Ring) = struct
  type coeff = C.t
  type var   = V.t

  (* \ic{%
     We represent polynomials as assoc lists from
     monomials to coefficents. See [norm] for invariants
     that we maintain.} *)
  type monom = (V.t * int) list

  type term = monom * C.t

  type t = term list

  (*********************************************************************)
  (* \ic{\bf Equality and comparison} *)

  let vexp_equal = pair_equal V.equal (=)

  let vexp_compare = pair_compare V.compare compare

  let mon_equal = list_equal vexp_equal

  let mon_compare = list_compare vexp_compare

  let equal =
    list_equal (fun (m1,c1) (m2,c2) -> C.equal c1 c2 && mon_equal m1 m2)

  let term_compare (m1,c1) (m2,c2) =
    let cmp = C.compare c1 c2 in
    if cmp <> 0 then - cmp else mon_compare m1 m2

  let monom_compare (m1, c1) (m2, c2) =
    mon_compare m1 m2

  let compare = list_compare term_compare
  let compare_based_on_monomials = list_compare monom_compare

  let comparetuple (num1, denom1) (num2, denom2) = 
    let cmp = compare num1 num2 in
    if cmp <= 0 then cmp
    else compare denom1 denom2

  (*i*)
  (*********************************************************************)
  (* \ic{\bf Pretty printing} *)

  let pp_vpow fmt (v,e) =
    if e = 1 then V.pp fmt v
    else F.fprintf fmt "%a^%i" V.pp v e 

  let pp_monom fmt m =
    match m with
    | [] -> F.fprintf fmt "1"
    | _  -> F.fprintf fmt "%a" (pp_list "*" pp_vpow) m

  let pp_term fmt (m,c) =
    if m = [] then F.fprintf fmt "%a" C.pp c
    else if C.equal c C.one then pp_monom fmt m
    else if C.use_parens then F.fprintf fmt "[%a]*%a" C.pp c pp_monom m
    else F.fprintf fmt "%a*%a" C.pp c pp_monom m

  let pp_ break fmt f =
    (* let f = L.sort term_compare f in *)
    let rec go fmt ts = match ts with
      | [] -> F.fprintf fmt ""
      | (m,c)::ts when C.compare c C.zero < 0->
        F.fprintf fmt " %s- %a%a" (if break then "\n" else "") pp_term (m,C.opp c) go ts
      | t::ts ->
        F.fprintf fmt " %s+ %a%a" (if break then "\n" else "") pp_term t go ts
    in
    match f with
    | []     -> F.fprintf fmt "0"
    | t::ts  ->
      F.fprintf fmt "%a%a" pp_term t go ts

  let pp = pp_ false

  let pp_break = pp_ true

  let pp_coeff = C.pp
  (*i*)

  (*********************************************************************)
  (* \ic{\bf Internal functions} *)

  let norm_monom (ves : (V.t * int) list) =
    let cmp_var (v1,_) (v2,_) = V.compare v1 v2 in
    let equal_var (v1,_) (v2,_) = V.equal v1 v2 in
    L.sort cmp_var ves
    |> group equal_var
    |> L.map (fun ves -> (fst (L.hd ves), sum (L.map snd ves)))
    |> L.filter (fun (_,e) -> e <> 0)
    |> L.sort vexp_compare

  (* \ic{The [norm] function ensures that:
     \begin{itemize}
     \item Vexp entries 
     \item Each monomial is sorted.
     \item Each monomial with non-zero coefficient has exactly one entry.
     \item The list is sorted by the monomials (keys).
     \end{itemize} }*)
  let norm (f : t) =
    f |> L.map (fun (m,c) -> (norm_monom m,c))
      |> L.sort (fun (m1,_) (m2,_) -> mon_compare m1 m2)
      |> group  (fun (m1,_) (m2,_) -> mon_equal m1 m2)
      |> L.map (fun ys -> (fst (L.hd ys), C.ladd (L.map snd ys)))
      |> L.filter (fun (_,c) -> not (C.equal c C.zero))

  let mult_term_poly (m,c) f =
    L.map (fun (m',c') -> (m @ m', C.mult c c')) f
    |> norm

  (*********************************************************************)
  (* \ic{\bf Ring operations on polynomials} *)

  let add f g = norm (f @ g)

  (* \ic{No [norm] required since the keys (monomials) are unchanged.} *)
  let opp f = L.map (fun (m,c) -> (m,C.opp c)) f 

  let mult f g = f |> conc_map (fun t -> mult_term_poly t g) |> norm
  
  let minus f g = add f (opp g)

  let one  = [([], C.one)]
  
  let zero : t = []

  let var_exp v n = [([(v,n)],C.one)]

  let rec ring_exp f n =
    if n > 0 then mult f (ring_exp f (n-1)) 
    else if n = 0 then one
    else failwith "Negative exponent in polynomial"
  
  let var v = [([(v,1)],C.one)]
  
  let const c = [([],c)]

  let from_int i = const (C.from_int i)

  let lmult = L.fold_left (fun acc f -> mult acc f) one

  let ladd  = L.fold_left (fun acc f -> add acc f) zero

  let lcm = mult

  let llcm = L.fold_left (fun acc f -> lcm acc f) one 

  let pow p i = lmult (replicate p i)
  
  let vars f =
    sorted_nub V.compare
      (conc_map (fun (m,_) -> sorted_nub V.compare (L.map fst m)) f)

  let vars_of_list f_list = 
    sorted_nub V.compare
      (conc_map 
        (fun f -> sorted_nub V.compare (conc_map (fun (m,_) -> sorted_nub V.compare (L.map fst m)) f))
      f_list)

  let is_proper_basis f basis =
    let (l, c) = try L.find 
                    (fun (f_monom, _) -> 
                        not(L.exists (fun basis_monom -> mon_equal basis_monom f_monom) basis)
                    ) f with Not_found -> ([],C.zero) in
                    
    if ((C.equal c C.zero) && (l = [])) then true
    else false
  
  let coeff_poly f var = 
  (* For a poly f = f_1 . h(var) + f_2, and variable var, outputs f_1 *)
    let filtered_monom = L.filter (fun (monom, c) -> (L.exists (fun (v, power) -> v = var) monom)) f in
    L.map (fun (monom, c) -> ((L.map (fun (v, power) -> (v,power)) (L.filter (fun (v, power) -> not(v = var)) monom)),c) ) filtered_monom

  let coeff_remainder_poly f var = 
  (* For a poly f = f_1 . h(var) + f_2, and variable var, outputs (f_1, f_2) *)
    let filtered_monom = L.filter (fun (monom, c) -> (L.exists (fun (v, power) -> v = var) monom)) f in
    let remaining_poly = L.filter (fun (monom, c) -> not (L.exists (fun (v, power) -> v = var) monom)) f in
    let coeff_poly = L.map (fun (monom, c) -> ((L.map (fun (v, power) -> (v,power)) (L.filter (fun (v, power) -> not(v = var)) monom)),c) ) filtered_monom in 
    (coeff_poly, remaining_poly)

  let has_power f var list_of_powers = 
    (* Outputs true if all the powers of var lie in list_of_powers *)
    not (L.exists ( fun (monom, c) -> 
                  not (C.equal c C.zero) &&
                  (L.exists (fun (v, power) -> ((v = var) && not (L.mem power list_of_powers))) monom) 
             ) f)

  let partition p f =
    let (t1s, t2s) = L.partition p f in
    (norm t1s, norm t2s)

  let inst_var env (v,e) =
    match e < 0, env v with
    | true, [([(v',e')],c)] when C.equal c C.one ->
      [([(v',e*e')],c)]
    | true, _ ->
      failwith "variables with negative exponent can only be instantiated with variables"
    | false, f ->
      ring_exp f e

  let eval env f =
    let eval_monom m = lmult (L.map (inst_var env) m) in
    let eval_term (m,c) = mult (const c) (eval_monom m) in
    ladd (L.map eval_term f)

  let eval_generic cconv vconv terms =
    let vars_to_poly ves = lmult (L.map (inst_var vconv) ves) in
    ladd (L.map (fun (ves, c) ->  mult (vars_to_poly ves) (cconv c)) terms)

  let to_terms f = f

  let from_terms f = norm f

  let from_mon m = from_terms [(m, C.one)]

  let is_const = function [([],_c)] -> true | _ -> false

  let is_var = function [([_x],c)] when C.equal c C.one -> true | _ -> false

  let is_consts f = not(L.exists (function ([],_c) -> false | _ -> true) f)

  let sort_based_on_monomials f = sorted_nub monom_compare f
  let rec sorted_assoc m f = match f with 
                             | [] -> raise Not_found
                             | (a,b)::l -> (let c = mon_compare a m in 
                                           if c < 0 then sorted_assoc m l
                                           else if c = 0 then b
                                           else raise Not_found) 
  let mons (f : t) = sorted_nub (list_compare vexp_compare) (L.map fst f)
  let coeff f m = try L.assoc m f with Not_found -> C.zero
  let is_non_zero_coeff f m = if (C.compare (coeff f m) C.zero <> 0) then true else false
  let coeff_in_sorted_poly f m = try sorted_assoc m f with Not_found -> C.zero
  let is_non_zero_coeff_in_sorted_poly f m = if (C.compare (coeff_in_sorted_poly f m) C.zero <> 0) then true else false
  let print_comparisions f = 
        L.iter (fun t1 -> L.iter (fun t2 -> F.fprintf Format.std_formatter "\n%a %a %d" pp_term t1 pp_term t2 (monom_compare t1 t2)) f) f
  
  let rec mon_exists mon_list mon = match mon_list with 
                             | [] -> false
                             | a::l -> (let c = mon_compare a mon in 
                                        if c < 0 then mon_exists l mon
                                        else if c = 0 then true
                                        else false) 

  let get_1 (c,_) = c
  let get_2 (_,c) = c

  (*Used for hash tables*)
  let get_key mon =
    let degree = L.fold_left (fun total_power (_,power) -> total_power + power) 0 mon in
    let first_var = try Some (get_1 (L.nth mon 1)) with Failure str -> None in
    let second_var = try Some (get_1 (L.nth mon 2)) with Failure str -> None in
    (first_var, second_var, degree)


  (* b is the monomial basis, i.e. a list of monomials *)
  let to_vector f b =
    let m = mons f in
    (* Make sure terms are ordered similarly as the monomials *)
    let _t = sorted_nub (fun x y -> list_compare vexp_compare (fst x) (fst y)) f in

    (* Loop over each basis element to find its coefficient *)
    let rec loop acc b =
      match b with
      | [] -> acc
      | x :: xs ->
        (* Find index of x in monomial list of f *)
        let i = index m x in
        if i < 0 then loop (C.zero :: acc) xs
        (* Return coefficient from corresponding element of t *)
        else loop (coeff f x :: acc) xs
    in
    L.rev (loop [] b)

  let div_mon f m =
    let m' = L.map (fun (v,i) -> (v, -i)) m in
    mult_term_poly (m', C.one) f


  (*Divides a monomial by (inputv, inputpower). If division is success, returns succes along with answer. Otherwise, returns false along with same monomial *)
  let divide_by_var mon (inputv, inputpower) = 
        let success = ref false in
        let result = L.fold_right (fun (v, power) acc -> 
                                    (* F.fprintf Format.std_formatter "\ninputv = %a  v = %a" pp_vpow (inputv,inputpower) pp_vpow (v,power); *)
                                    if (V.compare inputv v) == 0 && (power >= inputpower) then 
                                    (
                                        (* F.fprintf Format.std_formatter "\ncomparison success"; *)
                                        success := true;
                                        if power == inputpower then 
                                            acc 
                                        else
                                            [(inputv, power-inputpower)]@acc
                                    )
                                    else (v, power)::acc
              ) mon [] in
        (* F.fprintf Format.std_formatter "\ndividebyvar mon = %a %a %a" pp_monom mon pp_vpow (inputv,inputpower) pp_monom result; *)
        (* L.iter(fun (flag, mon, c) -> F.fprintf Format.std_formatter "\n%d %a %d" flag pp_monom mon c;);  *)
        (!success, result)

    (*Ignoring inputc of the input term. The function does not work property if inputc \neq 1 *)
  let coeff_of_term (inputmon, inputc) f = 
    (*Dividies each monom in f with inputmon*)
    let coeffs = L.map (fun (monom, c) ->   
                        (* Dividies monom with each (inputv,inpower) present in inputmon.  If output is (true, answer) then the division is successfull. 
                        If output is (false, answer) then inputmon contains a variable not in monom *)
                        let (flag, quotient_monom) = L.fold_left (fun (success, acc) (inputv, inputpower) -> if success then 
                                                                                                                divide_by_var acc (inputv, inputpower)
                                                                                                            else 
                                                                                                                (false, acc) 
                                    ) (true, monom) inputmon in
                        if (C.compare inputc (C.opp C.one) == 0) then
                            (flag, quotient_monom, C.opp c)
                        else
                            (flag, quotient_monom, c)
                    ) f in
    (* L.iter(fun (flag, mon, c) -> F.fprintf Format.std_formatter "\n%d %a %d" flag pp_monom mon c;);  *)
    L.map (fun (_, mon, c) -> (mon,c)) (L.filter (fun (flag,_,_) -> flag) coeffs)

   (*output terms in termvec1 that are also present in termvec2*)
  let filter_common_terms termvec1 termvec2 = 
    L.filter ( fun term -> L.exists (fun t -> if (term_compare term t) == 0 then true else false) termvec2  ) termvec1

  
  let substitutezero zeropoly f = 
    if L.length zeropoly == 0 then
        f 
    else 
        (*divide f be each monomial in zeropoly. Obtain the quotient poly.*)
        let quotients = L.map (fun inputterm -> coeff_of_term inputterm f) zeropoly in 

        (*out of the quotients obtained for each monomial in zeropoly, filter out the common quotient*)
        let common_quotients = L.fold_left (fun common_quotients quotients -> filter_common_terms common_quotients quotients) 
                                (L.nth quotients 0) quotients in
        (* F.fprintf Format.std_formatter "\nzeropoly = %a f = %a common_quotients = %a tosubtract = %a" pp zeropoly   pp f   pp common_quotients   pp (mult common_quotients zeropoly); *)
        (* L.iter (fun quotient -> F.fprintf Format.std_formatter "\nquotients = %a" pp quotient) quotients; *)
        minus f (mult common_quotients zeropoly)

  let ggt_mon m1 m2 =
    let m =
      L.map
        (fun (v,i) ->
           try
             let j = L.assoc v m2 in
             if      i < 0 && j < 0 then (v,max i j)
             else if i > 0 && j > 0 then (v, min i j)
             else                        (v, 0)
           with
             Not_found -> (v,0))
        m1
    in
    norm_monom m

  let coeff_mult = C.mult

  let ( *@) = mult
  let ( +@) = add
  let ( -@) = minus

end
