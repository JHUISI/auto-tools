(* This file is distributed under the MIT License (see LICENSE). *)

(*s Main function of the ggt tool. *)

(*i*)
open Util

module S = String
(*i*)

let main =
  if Array.length Sys.argv <> 2 then
    output_string stderr (F.sprintf "usage: %s <inputfile>\n" Sys.argv.(0))
  else
    let scmds = Util.input_file Sys.argv.(1) in
      let open PPEAnalyze in
      begin try
        let res = PPEAnalyze.analyze_from_string scmds in 
        pp_result_info Format.std_formatter res
        (* F.printf "%a\n" pp_result res *)
      with
        PPEInput.InvalidInput err ->
          F.printf "Invalid input: %s\n" err
      end