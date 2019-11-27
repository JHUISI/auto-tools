type 'a stream

type 'a nondet

val ret : 'a -> 'a nondet
val mempty : 'a nondet
val mplus : 'a nondet -> 'a nondet -> 'a nondet
val bind : 'a nondet -> ('a -> 'b nondet) -> 'b nondet
val guard : bool -> unit nondet
val run : int -> 'a nondet -> 'a list
val iter : int -> 'a nondet -> ('a -> unit) -> unit

val sequence : ('a nondet) list -> ('a list) nondet
val mapM : ('a -> 'b nondet) -> 'a list -> ('b list) nondet
val foreachM : 'a list -> ('a -> 'b nondet) -> ('b list) nondet
val mconcat : 'a list -> 'a nondet
val msum : ('a nondet) list -> 'a nondet

val (>>=) : 'a nondet -> ('a -> 'b nondet) -> 'b nondet

val (>>) : 'a nondet -> 'b nondet -> 'b nondet

val pick_set : int -> 'a nondet -> ('a list) nondet
val pick_set_exact : int -> 'a nondet -> ('a list) nondet
val cart : 'a nondet -> 'b nondet -> ('a * 'b) nondet
val prod : 'a nondet -> ('a * 'a) nondet
val ncart : 'a nondet list -> ('a list) nondet
val nprod : 'a nondet -> int -> ('a list) nondet
