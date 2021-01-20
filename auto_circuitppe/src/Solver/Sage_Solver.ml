(* This file is distributed under the MIT License (see LICENSE). *)

(*s Sage solver for non-parametric and interactive problems.
    Calls a Python script that uses the Sage library
    and communicates using JSON over standard input and output.
*)

(*i*)
open Util
open Big_int

module YS = Yojson.Safe
(*i*)

let sage_script = "./scripts/ggt_Sage.py"

type st_sage = {
  mutable sts_closed : bool;
  sts_cin    : in_channel;
  sts_cout   : out_channel;
}

let start_sage () =
  let (c_in, c_out) = Unix.open_process sage_script in
  { sts_cin = c_in; sts_cout = c_out; sts_closed = false }

let eval_sage sts cmd =
  if sts.sts_closed then failwith "sage process already closed";
  let (c_in, c_out) = sts.sts_cin, sts.sts_cout in
  (*i print_endline (">>> sent "^cmd); i*)
  output_string c_out cmd;
  flush c_out;
  (*i print_endline (">>> wait "); i*)
  let res = input_line c_in in
  (*i print_endline (">>> got "^res); i*)
  res


let stop_sage sts =
  if sts.sts_closed then failwith "sage process already closed";
  let (c_in, c_out) = sts.sts_cin, sts.sts_cout in
  let cmd = YS.to_string (`Assoc [ ("cmd",`String "exit") ])^"\n" in
  output_string c_out cmd;
  flush c_out;
  let o = input_line c_in in
  if o <> "end" then failwith "close: end expected";
  ignore (Unix.close_process (c_in,c_out))

let call_Sage ?sts cmd =
  match sts with
  | None ->
    let sts = start_sage () in
    let res = eval_sage sts cmd in
    stop_sage sts;
    res
  | Some sts ->
    eval_sage sts cmd

let vec_to_json v = `List (L.map (fun i -> `Int (int_of_big_int i)) v)

let mat_to_json m = `List (L.map (fun v -> vec_to_json v) m)

let lin_solve ?sts m b =
  let mr = mat_to_json m in
  let br = vec_to_json b in
  let req = `Assoc [ ("cmd",`String "linSolve"); ("M",mr); ("b",br) ] in
  let sres = call_Sage ?sts (YS.to_string req^"\n") in
  let mres = YS.from_string sres in
  if get_assoc "ok" mres |> get_bool
    then
      begin match get_assoc "res" mres |> get_string with
      | "sol"     -> Some(get_assoc "sol" mres |> get_vec)
      | "nosol"   -> None
      | _         -> failwith "lin_solve: Sage wrapper returned unknown 'res' value"
      end
    else
      failwith
        ("lin_solve: Sage wrapper returned an error: "^
         (get_assoc "error" mres |> get_string))

let compare_kernel ?sts lm rm =
  let lmj = mat_to_json lm in
  let rmj = mat_to_json rm in
  let req = `Assoc [ ("cmd",`String "compareKernel"); ("LM",lmj); ("RM",rmj) ] in
  let sres = call_Sage ?sts (YS.to_string req^"\n") in
  let mres = YS.from_string sres in
  if get_assoc "ok" mres |> get_bool
    then (
      let lk      = get_assoc "LK" mres      |> get_matrix in
      let rk      = get_assoc "RK" mres      |> get_matrix in
      let exc_ub  = get_assoc "exc_ub" mres  |> get_int in
      let attacks =
        get_assoc "attacks" mres |> get_list (get_pair get_bool (get_list get_int))
      in
      (lk, rk, exc_ub, attacks)
    ) else (
      failwith
        ("compare_kernel: Sage wrapper returned an error: "^
         (get_assoc "error" mres |> get_string))
    )

let compute_kernel ?sts m =
  let mj = mat_to_json m in
  let req = `Assoc [ ("cmd",`String "computeKernel"); ("M", mj) ] in
  let sres = call_Sage ?sts:sts (YS.to_string req^"\n") in
  let mres = YS.from_string sres in
  if get_assoc "ok" mres |> get_bool
    then get_assoc "K" mres |> get_matrix
    else (
      failwith
        ("compare_kernel: Sage wrapper returned an error: "^
         (get_assoc "error" mres |> get_string))
    )

let is_contradictory ?sts zero_constrs nzero_constrs vars =
  let req = 
    `Assoc [ ("cmd",`String "checkSat")
           ; ("zero",zero_constrs)
           ; ("nzero",nzero_constrs)
           ; ("vars", vars)]
  in
  let sres = call_Sage ?sts (YS.to_string req^"\n") in
  let mres = YS.from_string sres in
  if get_assoc "ok" mres |> get_bool
    then (
      get_assoc "contradictory" mres |> get_bool
    ) else (
      failwith
        ("compare_kernel: Sage wrapper returned an error: "^
         (get_assoc "error" mres |> get_string))
    )
