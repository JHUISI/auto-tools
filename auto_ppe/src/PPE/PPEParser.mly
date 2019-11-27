%{
  open Util
  open PPEInput

  type temp = 
  { 
    fid       : recipe;
    pol       : rpoly;
  }

%}

/*s Parser for non-parametric assumptions */

/************************************************************************/
/* \hd{General tokens} */

%token EOF
%token DOT
%token COMMA
%token IN
%token TO

%token LBRACK
%token RBRACK
%token LPAR
%token RPAR

/************************************************************************/
/* \hd{Tokens for Commands} */

%token EMAPS
%token ORDER
%token ISOS
%token FIXED
%token UNFIXED
%token TRUSTED
%token UNTRUSTED
%token ZP

/************************************************************************/
/* \hd{Tokens for Input} */


%token <string> VARU /* uppercase identifier */
%token <string> GID  /* group identifier */
%token <int> FID  /* challenge polynomial identifier */

%token EXP
%token STAR
%token PLUS
%token MINUS
%token EQUALS

%token <int> NAT
%token <int> INT

/************************************************************************/
/* \hd{Priority and associativity} */

/* \ic{Multiplication has the highest precedence.} */
%left PLUS MINUS
%left STAR

/************************************************************************/
/* \hd{Start symbols} */

%type  <PPEInput.cmd list> cmds_t

%start cmds_t
%%

/************************************************************************/
/* \hd{Commands} */

/******* Not parsing (poly) properly.  (x+y)*z is parsed as x + y * z ********/
poly :
| v = variable              { v }
| f = poly; PLUS; g = poly  { RP.add f g }
| f = poly; STAR; g = poly  { RP.mult f g }
| f = poly; MINUS; g = poly { RP.minus f g }

| f = poly; EXP; i = INT    { RP.ring_exp f i }

| MINUS; f = poly           { RP.opp f }
| LPAR; f = poly; RPAR      { f }
| i = INT                   { RP.from_int i }
;

variable :
| v = VARU  { RP.var v }
;

iso :
| dom = GID; TO; codom = GID { { iso_dom = dom; iso_codom = codom } }
;

emap :
| dom = separated_nonempty_list(STAR,GID); TO; codom = GID
  { { em_dom = dom; em_codom = codom } }
;

polywithid :
| s = FID; EQUALS; f = poly   { {fid = Param(s); pol = f} }
;

cmd :
| EMAPS; emaps = separated_nonempty_list(COMMA,emap); DOT
  { AddMaps emaps }
| ISOS; isos = separated_nonempty_list(COMMA,iso); DOT
  { AddIsos isos }
| ORDER; i = INT; DOT
  { SetPrimeNum i }
| FIXED; LBRACK; pss=separated_nonempty_list(COMMA, variable); RBRACK; DOT
  { AddFixed(L.map (fun v -> {ge_id = Param(-1); ge_rpoly = v; ge_group = None}) pss) }
| UNFIXED; LBRACK; pss=separated_nonempty_list(COMMA, variable); RBRACK; DOT 
  { AddUnfixed(L.map (fun v -> {ge_id = Param(-1); ge_rpoly = v; ge_group = None}) pss) }
| UNTRUSTED; LBRACK; pss=separated_nonempty_list(COMMA, polywithid); RBRACK; IN; gid = GID; DOT
  { AddUntrusted(L.map (fun ps -> { ge_id = ps.fid; ge_rpoly = ps.pol; ge_group = Some gid }) pss) }
| TRUSTED; LBRACK; pss=separated_nonempty_list(COMMA, polywithid); RBRACK; IN; gid = GID; DOT
  { AddTrusted(L.map (fun ps -> { ge_id = ps.fid; ge_rpoly = ps.pol; ge_group = Some gid }) pss) }
| ZP; LBRACK; pss=separated_nonempty_list(COMMA, poly); RBRACK; DOT
  { AddZp(L.map (fun ps -> { ge_id = Param(-1); ge_rpoly = ps; ge_group = None }) pss) }
;

/************************************************************************/
/* \hd{Versions that consume all input} */

cmds_t : cs = list(cmd); EOF { cs };
