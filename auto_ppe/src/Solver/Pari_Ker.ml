(* This file is distributed under the MIT License (see LICENSE). *)

open Ctypes
open Foreign

module US = Unsigned.Size_t
module UL = Unsigned.ULong
module L  = List

(* ************************************************************************ *)
(* Ocaml matrices *)

let iter_matrix f cs =
  let i = ref 0 in
  List.iter
    (fun c ->
       let j = ref 0 in
       List.iter (fun e -> f !i !j e; incr j) c;
       incr i)
    cs

(* ************************************************************************ *)
(* Types *)

let cmatrix = ptr (ptr long)

(* ************************************************************************ *)
(* Function bindings *)

let pari_init_c = foreign "pari_init" (size_t @-> ulong @-> returning void)

let new_matrix = foreign "new_matrix" (int @-> int @-> returning cmatrix)

let free_matrix = foreign "free_matrix" (cmatrix @-> int @-> returning void)
    
let kernel_c = foreign "kernel"
  (cmatrix @-> int @-> int @-> ptr int @-> ptr int @-> returning cmatrix)

(* ************************************************************************ *)
(* Ocaml functions  *)

let cmatrix_of_matrix cs =
  match cs with
  | []    ->
    failwith "cmatrix_of_matrix: empty matrix given"
  | c::_  ->
    let ncols = L.length cs in
    let nrows = L.length c in
    let cm = new_matrix ncols nrows in
    iter_matrix
      (fun i j e ->
         let col_c = !@ (cm +@ i) in
         col_c +@ j <-@ Signed.Long.of_int64 (Big_int.int64_of_big_int e))
      cs;
    (cm, ncols, nrows)

let kernel_non_empty cs =
  let (m, ncols, nrows) = cmatrix_of_matrix cs in
  let kncols_ptr = allocate int 0 in
  let knrows_ptr = allocate int 0 in
  let k = kernel_c m ncols nrows kncols_ptr knrows_ptr in
  free_matrix m ncols;
  let kncols = !@ kncols_ptr in
  if kncols = 0 then (
    (* Format.printf "kernel is empty\n"; *)
    []
  ) else (
    let knrows = !@ knrows_ptr in
    (* Format.printf "kernel is nonempty: %i %i\n%!" kncols knrows; *)
    let cs = ref [] in
    for i = kncols - 1 downto 0 do
      let es = ref [] in
      let c = !@ (k  +@ i) in
      for j = knrows - 1 downto 0 do
        let e = Signed.Long.to_int (!@ (c +@ j)) in
        (* Format.printf "i=%i, j=%i: %i\n%!" i j e; *)
        es := e::!es
      done;
      cs := !es::!cs
    done;
    !cs
  )

let kernel rs =
  match rs with
  | [] -> []
  | _  -> kernel_non_empty rs

let pari_init () = pari_init_c (US.of_int 10000000) (UL.of_int 2)

(* ************************************************************************ *)
(* Test program *)

(*
let t () =
  pari_init_c (US.of_int 10000000) (UL.of_int 2);
  let m = [ [1;0;0]; [0;1;0]; [1;1;0] ] in
  for _i = 1 to 1 do
    match kernel m with
    | None ->
      Format.printf "kernel is empty"
    | Some cs ->
       iter_matrix
         (fun i j e -> Format.printf "i=%i, j=%i: %i\n%!" i j e)
         cs
   done
*)
