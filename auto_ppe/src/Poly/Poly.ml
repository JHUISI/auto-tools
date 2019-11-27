(* This file is distributed under the MIT License (see LICENSE). *)

(*s Use [Var] and [Ring] types to define [MakePoly] functor.
    Also define [IntRing]. *)
(*i*)
open Util
open PolyInterfaces
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
  type monom = V.t list

  type term = monom * C.t

  type t = term list

  (*********************************************************************)
  (* \ic{\bf Equality and comparison} *)

  let mon_equal = list_equal V.equal

  let mon_compare = list_compare V.compare

  let equal =
    list_equal (fun (m1,c1) (m2,c2) -> C.equal c1 c2 && mon_equal m1 m2)

  let term_compare (m1,c1) (m2,c2) =
    let cmp = C.compare c1 c2 in
    if cmp <> 0 then - cmp else mon_compare m1 m2

  let compare = list_compare term_compare

  (*i*)
  (*********************************************************************)
  (* \ic{\bf Pretty printing} *)

  let pp_monom fmt m =
    match m with
    | [] -> F.fprintf fmt "1"
    | _  -> F.fprintf fmt "%a" (pp_list "*" V.pp) m

  let pp_term fmt (m,c) =
    if m = [] then F.fprintf fmt "%a" C.pp c
    else if C.equal c C.one then pp_monom fmt m
    else if C.use_parens then F.fprintf fmt "[%a]*%a" C.pp c pp_monom m
    else F.fprintf fmt "%a*%a" C.pp c pp_monom m

  let pp_ break fmt f =
    let f = L.sort term_compare f in
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

  (* \ic{The [norm] function ensures that:
     \begin{itemize}
     \item Each monomial is sorted.
     \item Each monomial with non-zero coefficient has exactly one entry.
     \item The list is sorted by the monomials (keys).
     \end{itemize} }*)
  let norm f =
    f |> L.map (fun (m,c) -> (L.sort V.compare m, c))
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

  let rec ring_exp f n =
    if n > 0 then mult f (ring_exp f (n-1)) 
    else if n = 0 then one
    else failwith "Negative exponent in polynomial"
  
  let var v = [([v],C.one)]
  
  let const c = [([],c)]

  let from_int i = const (C.from_int i)

  let lmult = L.fold_left (fun acc f -> mult acc f) one

  let ladd  = L.fold_left (fun acc f -> add acc f) zero

  let pow p i = lmult (replicate p i)

  let vars f =
    sorted_nub V.compare
      (conc_map (fun (m,_) -> sorted_nub V.compare m) f)

  let partition p f =
    let (t1s, t2s) = L.partition p f in
    (norm t1s, norm t2s)

  let eval env f =
    let eval_monom m = lmult (L.map (fun v -> env v) m) in
    let eval_term (m,c) = mult (const c) (eval_monom m) in
    ladd (L.map eval_term f)

  let eval_generic cconv vconv terms =
    let vars_to_poly vs = lmult (L.map vconv vs) in
    ladd (L.map (fun (vs, c) ->  mult (vars_to_poly vs) (cconv c)) terms)

  let to_terms f = f

  let from_terms f = norm f

  let is_const = function [([],_c)] -> true | _ -> false

  let is_var = function [([_x],c)] when C.equal c C.one -> true | _ -> false

  let mons (f : t) = sorted_nub (list_compare V.compare) (L.map fst f)
  let coeff f m = try L.assoc m f with Not_found -> C.zero

  let coeff_mult = C.mult

  let ( *@) = mult
  let ( +@) = add
  let ( -@) = minus

end
