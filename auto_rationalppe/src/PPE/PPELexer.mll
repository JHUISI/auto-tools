(*s Lexer for non-parametric assumptions *)
{
  (*i*)
  open PPEParser

  module S = String
  (*i*)

  exception Error of string

  let unterminated_comment () =
    raise (Error "unterminated comment")
}

let blank = [' ' '\t' '\r' '\n']
let newline = '\n'
let idchars = ['a'-'z' 'A'-'Z' '\'' '_' '0'-'9']

rule lex = parse
  | blank+  { lex lexbuf }
  | "(*"    { comment lexbuf; lex lexbuf }
  | newline { Lexing.new_line lexbuf; lex lexbuf }
  | eof     { EOF }
  | "."     { DOT }
  | "("     { LPAR }
  | ")"     { RPAR }
  | "+"     { PLUS }
  | "->"    { TO }
  | "-"     { MINUS }
  | "*"     { STAR }
  | "["     { LBRACK }
  | "]"     { RBRACK }
  | ","     { COMMA }
  | "^"     { EXP }
  | "="     { EQUALS }
  | "/"     { DIVIDES }
  | "trusted_polys"    { TRUSTED }
  | "untrusted_polys"  { UNTRUSTED }
  | "fixed_vars"       { FIXED }
  | "unfixed_vars"     { UNFIXED }
  | "in"               { IN }
  | "maps"             { EMAPS }
  | "isos"             { ISOS }
  | "order"            { ORDER }
  | "Zp_vars"          { ZP }

  | '-'?['0'-'9']['0'-'9']* as s { INT(int_of_string(s)) }
  | ['0'-'9']['0'-'9']* as s { NAT(int_of_string(s)) }
  | ['F']['0'-'9']['0'-'9']* as s { FID(int_of_string (S.sub s 1 (S.length s - 1))) }
  | ['a'-'z' 'A'-'F' 'H'-'Z']idchars* as s { VARU s }
  | ['G']idchars* as s { GID (S.sub s 1 (S.length s - 1)) }

and comment = parse
  | "*)"        { () }
  | "(*"        { comment lexbuf; comment lexbuf }
  | newline     { Lexing.new_line lexbuf; comment lexbuf }
  | eof         { unterminated_comment () }
  | _           { comment lexbuf }
