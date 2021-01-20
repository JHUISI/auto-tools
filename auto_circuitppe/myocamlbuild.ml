open Ocamlbuild_plugin

let () =
  dispatch 
    ( function 
    | After_rules -> pdep ["link"] "linkdep" (fun param -> [param])
    | _           -> ()
    )
