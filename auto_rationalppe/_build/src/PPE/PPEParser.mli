
(* The type of tokens. *)

type token = 
  | ZP
  | VARU of (string)
  | UNTRUSTED
  | UNFIXED
  | TRUSTED
  | TO
  | STAR
  | RPAR
  | RBRACK
  | PLUS
  | ORDER
  | NAT of (int)
  | MINUS
  | LPAR
  | LBRACK
  | ISOS
  | INT of (int)
  | IN
  | GID of (string)
  | FIXED
  | FID of (int)
  | EXP
  | EQUALS
  | EOF
  | EMAPS
  | DOT
  | DIVIDES
  | COMMA

(* This exception is raised by the monolithic API functions. *)

exception Error

(* The monolithic API. *)

val cmds_t: (Lexing.lexbuf -> token) -> Lexing.lexbuf -> (PPEInput.cmd list)
