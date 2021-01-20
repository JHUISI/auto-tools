(*s Module types for variables, ring, and polynomials
    shared between [LPoly.ml] and [LPoly.mli]. *)

module type Var = sig
  type t
  val pp : Format.formatter -> t -> unit
  val equal : t -> t -> bool
  val compare : t -> t -> int
end

module type Ring = sig
  type t
  val pp : Format.formatter -> t -> unit
  val add : t -> t -> t
  val opp : t -> t
  val mult : t -> t -> t
  val ring_exp : t -> int -> t
  val one : t
  val zero : t
  val ladd : t list -> t
  val from_int : int -> t
  val equal : t -> t -> bool
  val compare : t -> t -> int
  val use_parens : bool
end

module type Poly = sig
(*   type t
  type var
  type coeff
  type monom
  type term *)
  type coeff
  type var
  type monom = (var * int) list
  type term = monom * coeff
  type t = term list

  val pp_monom : Format.formatter -> monom -> unit
  val pp_term : Format.formatter -> term -> unit
  val pp : Format.formatter -> t -> unit
  val pp_break : Format.formatter -> t -> unit
  val pp_coeff : Format.formatter -> coeff -> unit
  val add : t -> t -> t
  val opp : t -> t
  val minus : t -> t -> t
  val mult : t -> t -> t
  val ring_exp : t -> int -> t
  val var_exp : var -> int -> t
  val one : t
  val zero : t
  val lmult : t list -> t
  val ladd : t list -> t
  val pow : t -> int -> t
  val var : var -> t
  val const : coeff -> t
  val from_int : int -> t

  (* \ic{[eval env f] returns the polynomial [f] evaluated at
         the points [x := env x].} *)
  val eval : (var -> t) -> t -> t
  val eval_generic : ('c -> t) -> ('v -> t) -> (('v * int) list * 'c) list -> t
  val vars : t -> var list
  val vars_of_list : t list -> var list
  val is_proper_basis : t -> monom list -> bool
  (* \ic{[partition p f] returns a tuple [(t1s,t2s)]
         where [t1s] consists of the terms of [f] satisfying [p]
         and [t1s] consists of the terms of [f] not satisfying [p].} *)
  val partition : (((var * int) list * coeff) -> bool) -> t -> (t * t)
  val to_terms : t -> ((var * int) list * coeff) list
  val from_terms : ((var * int) list * coeff) list -> t
  val from_mon : monom -> t
  val is_const : t -> bool
  val is_consts : t -> bool
  val is_var : t -> bool
  val is_non_zero_coeff_in_sorted_poly : t -> monom -> bool
  val coeff_in_sorted_poly : t -> monom -> coeff
  val sort_based_on_monomials : t -> t
  val mons : t -> monom list
  val coeff : t -> monom -> coeff
  val is_non_zero_coeff : t -> monom -> bool
  val coeff_mult : coeff -> coeff -> coeff
  val print_comparisions : t -> unit
  val mon_exists : monom list -> monom -> bool
  (* In the tool we want to express a polynomial in terms of a monomial basis *)
  val to_vector : t -> monom list -> coeff list
  val get_key : monom -> (var option * var option * int)
  val div_mon : t -> monom -> t
  val ggt_mon : monom -> monom -> monom

  val has_power : t -> var -> int list -> bool
  val coeff_poly : t -> var -> t 
  val coeff_remainder_poly : t -> var -> (t * t)
  val substitutezero : t -> t -> t
  val ( *@) : t -> t -> t
  val (+@)  : t -> t -> t
  val (-@)  : t -> t -> t
  val equal : t -> t -> bool
  val mon_equal : monom -> monom -> bool
  val mon_compare : monom -> monom -> int
  val compare : t -> t -> int
end
