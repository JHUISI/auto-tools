
module MenhirBasics = struct
  
  exception Error
  
  type token = 
    | ZP
    | VARU of (
# 46 "src/PPE/PPEParser.mly"
       (string)
# 12 "src/PPE/PPEParser.ml"
  )
    | UNTRUSTED
    | UNFIXED
    | TRUSTED
    | TO
    | STAR
    | RPAR
    | RBRACK
    | PLUS
    | ORDER
    | NAT of (
# 57 "src/PPE/PPEParser.mly"
       (int)
# 26 "src/PPE/PPEParser.ml"
  )
    | MINUS
    | LPAR
    | LBRACK
    | ISOS
    | INT of (
# 58 "src/PPE/PPEParser.mly"
       (int)
# 35 "src/PPE/PPEParser.ml"
  )
    | IN
    | GID of (
# 47 "src/PPE/PPEParser.mly"
       (string)
# 41 "src/PPE/PPEParser.ml"
  )
    | FIXED
    | FID of (
# 48 "src/PPE/PPEParser.mly"
       (int)
# 47 "src/PPE/PPEParser.ml"
  )
    | EXP
    | EQUALS
    | EOF
    | EMAPS
    | DOT
    | DIVIDES
    | COMMA
  
end

include MenhirBasics

let _eRR =
  MenhirBasics.Error

type _menhir_env = {
  _menhir_lexer: Lexing.lexbuf -> token;
  _menhir_lexbuf: Lexing.lexbuf;
  _menhir_token: token;
  mutable _menhir_error: bool
}

and _menhir_state = 
  | MenhirState74
  | MenhirState69
  | MenhirState61
  | MenhirState59
  | MenhirState57
  | MenhirState50
  | MenhirState41
  | MenhirState38
  | MenhirState30
  | MenhirState28
  | MenhirState26
  | MenhirState23
  | MenhirState16
  | MenhirState14
  | MenhirState9
  | MenhirState5
  | MenhirState4
  | MenhirState2
  | MenhirState0

# 1 "src/PPE/PPEParser.mly"
  
  open Util
  open PPEInput

  type temp = 
  { 
    fid       : recipe;
    pol       : rpoly;
    denom     : rpoly;
  }


# 105 "src/PPE/PPEParser.ml"

let rec _menhir_goto_separated_nonempty_list_COMMA_polywithid_ : _menhir_env -> 'ttv_tail -> _menhir_state -> (temp list) -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s _v ->
    let _menhir_stack = (_menhir_stack, _menhir_s, _v) in
    match _menhir_s with
    | MenhirState26 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | RBRACK ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let _menhir_env = _menhir_discard _menhir_env in
            let _tok = _menhir_env._menhir_token in
            (match _tok with
            | IN ->
                let _menhir_stack = Obj.magic _menhir_stack in
                let _menhir_env = _menhir_discard _menhir_env in
                let _tok = _menhir_env._menhir_token in
                (match _tok with
                | GID _v ->
                    let _menhir_stack = Obj.magic _menhir_stack in
                    let _menhir_stack = (_menhir_stack, _v) in
                    let _menhir_env = _menhir_discard _menhir_env in
                    let _tok = _menhir_env._menhir_token in
                    (match _tok with
                    | DOT ->
                        let _menhir_stack = Obj.magic _menhir_stack in
                        let _menhir_env = _menhir_discard _menhir_env in
                        let _menhir_stack = Obj.magic _menhir_stack in
                        let (((_menhir_stack, _menhir_s), _, (pss : (temp list))), (gid : (
# 47 "src/PPE/PPEParser.mly"
       (string)
# 139 "src/PPE/PPEParser.ml"
                        ))) = _menhir_stack in
                        let _7 = () in
                        let _5 = () in
                        let _4 = () in
                        let _2 = () in
                        let _1 = () in
                        let _v : (PPEInput.cmd) = 
# 118 "src/PPE/PPEParser.mly"
  ( AddUntrusted(L.map (fun ps -> { ge_id = ps.fid; ge_rpoly = ps.pol; ge_rdenom = ps.denom; ge_group = Some gid }) pss) )
# 149 "src/PPE/PPEParser.ml"
                         in
                        _menhir_goto_cmd _menhir_env _menhir_stack _menhir_s _v
                    | _ ->
                        assert (not _menhir_env._menhir_error);
                        _menhir_env._menhir_error <- true;
                        let _menhir_stack = Obj.magic _menhir_stack in
                        let ((_menhir_stack, _menhir_s, _), _) = _menhir_stack in
                        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
                | _ ->
                    assert (not _menhir_env._menhir_error);
                    _menhir_env._menhir_error <- true;
                    let _menhir_stack = Obj.magic _menhir_stack in
                    let (_menhir_stack, _menhir_s, _) = _menhir_stack in
                    _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
            | _ ->
                assert (not _menhir_env._menhir_error);
                _menhir_env._menhir_error <- true;
                let _menhir_stack = Obj.magic _menhir_stack in
                let (_menhir_stack, _menhir_s, _) = _menhir_stack in
                _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | MenhirState38 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_stack = Obj.magic _menhir_stack in
        let ((_menhir_stack, _menhir_s, (x : (temp))), _, (xs : (temp list))) = _menhir_stack in
        let _2 = () in
        let _v : (temp list) = 
# 231 "/Users/satya/.opam/autoppe/lib/menhir/standard.mly"
    ( x :: xs )
# 184 "src/PPE/PPEParser.ml"
         in
        _menhir_goto_separated_nonempty_list_COMMA_polywithid_ _menhir_env _menhir_stack _menhir_s _v
    | MenhirState41 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | RBRACK ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let _menhir_env = _menhir_discard _menhir_env in
            let _tok = _menhir_env._menhir_token in
            (match _tok with
            | IN ->
                let _menhir_stack = Obj.magic _menhir_stack in
                let _menhir_env = _menhir_discard _menhir_env in
                let _tok = _menhir_env._menhir_token in
                (match _tok with
                | GID _v ->
                    let _menhir_stack = Obj.magic _menhir_stack in
                    let _menhir_stack = (_menhir_stack, _v) in
                    let _menhir_env = _menhir_discard _menhir_env in
                    let _tok = _menhir_env._menhir_token in
                    (match _tok with
                    | DOT ->
                        let _menhir_stack = Obj.magic _menhir_stack in
                        let _menhir_env = _menhir_discard _menhir_env in
                        let _menhir_stack = Obj.magic _menhir_stack in
                        let (((_menhir_stack, _menhir_s), _, (pss : (temp list))), (gid : (
# 47 "src/PPE/PPEParser.mly"
       (string)
# 215 "src/PPE/PPEParser.ml"
                        ))) = _menhir_stack in
                        let _7 = () in
                        let _5 = () in
                        let _4 = () in
                        let _2 = () in
                        let _1 = () in
                        let _v : (PPEInput.cmd) = 
# 120 "src/PPE/PPEParser.mly"
  ( AddTrusted(L.map (fun ps -> { ge_id = ps.fid; ge_rpoly = ps.pol; ge_rdenom = ps.denom; ge_group = Some gid }) pss) )
# 225 "src/PPE/PPEParser.ml"
                         in
                        _menhir_goto_cmd _menhir_env _menhir_stack _menhir_s _v
                    | _ ->
                        assert (not _menhir_env._menhir_error);
                        _menhir_env._menhir_error <- true;
                        let _menhir_stack = Obj.magic _menhir_stack in
                        let ((_menhir_stack, _menhir_s, _), _) = _menhir_stack in
                        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
                | _ ->
                    assert (not _menhir_env._menhir_error);
                    _menhir_env._menhir_error <- true;
                    let _menhir_stack = Obj.magic _menhir_stack in
                    let (_menhir_stack, _menhir_s, _) = _menhir_stack in
                    _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
            | _ ->
                assert (not _menhir_env._menhir_error);
                _menhir_env._menhir_error <- true;
                let _menhir_stack = Obj.magic _menhir_stack in
                let (_menhir_stack, _menhir_s, _) = _menhir_stack in
                _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | _ ->
        _menhir_fail ()

and _menhir_goto_polywithid : _menhir_env -> 'ttv_tail -> _menhir_state -> (temp) -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s _v ->
    let _menhir_stack = (_menhir_stack, _menhir_s, _v) in
    let _menhir_stack = Obj.magic _menhir_stack in
    assert (not _menhir_env._menhir_error);
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | COMMA ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_env = _menhir_discard _menhir_env in
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | FID _v ->
            _menhir_run27 _menhir_env (Obj.magic _menhir_stack) MenhirState38 _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState38)
    | RBRACK ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, (x : (temp))) = _menhir_stack in
        let _v : (temp list) = 
# 229 "/Users/satya/.opam/autoppe/lib/menhir/standard.mly"
    ( [ x ] )
# 279 "src/PPE/PPEParser.ml"
         in
        _menhir_goto_separated_nonempty_list_COMMA_polywithid_ _menhir_env _menhir_stack _menhir_s _v
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s

and _menhir_goto_separated_nonempty_list_COMMA_poly_ : _menhir_env -> 'ttv_tail -> _menhir_state -> (PPEInput.rpoly list) -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s _v ->
    let _menhir_stack = (_menhir_stack, _menhir_s, _v) in
    match _menhir_s with
    | MenhirState2 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | RBRACK ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let _menhir_env = _menhir_discard _menhir_env in
            let _tok = _menhir_env._menhir_token in
            (match _tok with
            | DOT ->
                let _menhir_stack = Obj.magic _menhir_stack in
                let _menhir_env = _menhir_discard _menhir_env in
                let _menhir_stack = Obj.magic _menhir_stack in
                let ((_menhir_stack, _menhir_s), _, (pss : (PPEInput.rpoly list))) = _menhir_stack in
                let _5 = () in
                let _4 = () in
                let _2 = () in
                let _1 = () in
                let _v : (PPEInput.cmd) = 
# 122 "src/PPE/PPEParser.mly"
  ( AddZp(L.map (fun ps -> { ge_id = Param(-1); ge_rpoly = ps; ge_rdenom = RP.from_int 1; ge_group = None }) pss) )
# 315 "src/PPE/PPEParser.ml"
                 in
                _menhir_goto_cmd _menhir_env _menhir_stack _menhir_s _v
            | _ ->
                assert (not _menhir_env._menhir_error);
                _menhir_env._menhir_error <- true;
                let _menhir_stack = Obj.magic _menhir_stack in
                let (_menhir_stack, _menhir_s, _) = _menhir_stack in
                _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | MenhirState23 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_stack = Obj.magic _menhir_stack in
        let ((_menhir_stack, _menhir_s, (x : (PPEInput.rpoly))), _, (xs : (PPEInput.rpoly list))) = _menhir_stack in
        let _2 = () in
        let _v : (PPEInput.rpoly list) = 
# 231 "/Users/satya/.opam/autoppe/lib/menhir/standard.mly"
    ( x :: xs )
# 338 "src/PPE/PPEParser.ml"
         in
        _menhir_goto_separated_nonempty_list_COMMA_poly_ _menhir_env _menhir_stack _menhir_s _v
    | _ ->
        _menhir_fail ()

and _menhir_run9 : _menhir_env -> 'ttv_tail * _menhir_state * (PPEInput.rpoly) -> 'ttv_return =
  fun _menhir_env _menhir_stack ->
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | INT _v ->
        _menhir_run6 _menhir_env (Obj.magic _menhir_stack) MenhirState9 _v
    | LPAR ->
        _menhir_run5 _menhir_env (Obj.magic _menhir_stack) MenhirState9
    | MINUS ->
        _menhir_run4 _menhir_env (Obj.magic _menhir_stack) MenhirState9
    | VARU _v ->
        _menhir_run3 _menhir_env (Obj.magic _menhir_stack) MenhirState9 _v
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState9

and _menhir_run14 : _menhir_env -> 'ttv_tail * _menhir_state * (PPEInput.rpoly) -> 'ttv_return =
  fun _menhir_env _menhir_stack ->
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | INT _v ->
        _menhir_run6 _menhir_env (Obj.magic _menhir_stack) MenhirState14 _v
    | LPAR ->
        _menhir_run5 _menhir_env (Obj.magic _menhir_stack) MenhirState14
    | MINUS ->
        _menhir_run4 _menhir_env (Obj.magic _menhir_stack) MenhirState14
    | VARU _v ->
        _menhir_run3 _menhir_env (Obj.magic _menhir_stack) MenhirState14 _v
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState14

and _menhir_run16 : _menhir_env -> 'ttv_tail * _menhir_state * (PPEInput.rpoly) -> 'ttv_return =
  fun _menhir_env _menhir_stack ->
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | INT _v ->
        _menhir_run6 _menhir_env (Obj.magic _menhir_stack) MenhirState16 _v
    | LPAR ->
        _menhir_run5 _menhir_env (Obj.magic _menhir_stack) MenhirState16
    | MINUS ->
        _menhir_run4 _menhir_env (Obj.magic _menhir_stack) MenhirState16
    | VARU _v ->
        _menhir_run3 _menhir_env (Obj.magic _menhir_stack) MenhirState16 _v
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState16

and _menhir_run11 : _menhir_env -> 'ttv_tail * _menhir_state * (PPEInput.rpoly) -> 'ttv_return =
  fun _menhir_env _menhir_stack ->
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | INT _v ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_env = _menhir_discard _menhir_env in
        let _menhir_stack = Obj.magic _menhir_stack in
        let (i : (
# 58 "src/PPE/PPEParser.mly"
       (int)
# 410 "src/PPE/PPEParser.ml"
        )) = _v in
        let (_menhir_stack, _menhir_s, (f : (PPEInput.rpoly))) = _menhir_stack in
        let _2 = () in
        let _v : (PPEInput.rpoly) = 
# 85 "src/PPE/PPEParser.mly"
                            ( RP.ring_exp f i )
# 417 "src/PPE/PPEParser.ml"
         in
        _menhir_goto_poly _menhir_env _menhir_stack _menhir_s _v
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s

and _menhir_goto_separated_nonempty_list_COMMA_emap_ : _menhir_env -> 'ttv_tail -> _menhir_state -> (PPEInput.emap list) -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s _v ->
    let _menhir_stack = (_menhir_stack, _menhir_s, _v) in
    match _menhir_s with
    | MenhirState59 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | DOT ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let _menhir_env = _menhir_discard _menhir_env in
            let _menhir_stack = Obj.magic _menhir_stack in
            let ((_menhir_stack, _menhir_s), _, (emaps : (PPEInput.emap list))) = _menhir_stack in
            let _3 = () in
            let _1 = () in
            let _v : (PPEInput.cmd) = 
# 112 "src/PPE/PPEParser.mly"
  ( AddMaps emaps )
# 446 "src/PPE/PPEParser.ml"
             in
            _menhir_goto_cmd _menhir_env _menhir_stack _menhir_s _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | MenhirState69 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_stack = Obj.magic _menhir_stack in
        let ((_menhir_stack, _menhir_s, (x : (PPEInput.emap))), _, (xs : (PPEInput.emap list))) = _menhir_stack in
        let _2 = () in
        let _v : (PPEInput.emap list) = 
# 231 "/Users/satya/.opam/autoppe/lib/menhir/standard.mly"
    ( x :: xs )
# 463 "src/PPE/PPEParser.ml"
         in
        _menhir_goto_separated_nonempty_list_COMMA_emap_ _menhir_env _menhir_stack _menhir_s _v
    | _ ->
        _menhir_fail ()

and _menhir_fail : unit -> 'a =
  fun () ->
    Printf.fprintf Pervasives.stderr "Internal failure -- please contact the parser generator's developers.\n%!";
    assert false

and _menhir_goto_poly : _menhir_env -> 'ttv_tail -> _menhir_state -> (PPEInput.rpoly) -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s _v ->
    let _menhir_stack = (_menhir_stack, _menhir_s, _v) in
    match _menhir_s with
    | MenhirState5 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | EXP ->
            _menhir_run11 _menhir_env (Obj.magic _menhir_stack)
        | MINUS ->
            _menhir_run16 _menhir_env (Obj.magic _menhir_stack)
        | PLUS ->
            _menhir_run14 _menhir_env (Obj.magic _menhir_stack)
        | RPAR ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let _menhir_env = _menhir_discard _menhir_env in
            let _menhir_stack = Obj.magic _menhir_stack in
            let ((_menhir_stack, _menhir_s), _, (f : (PPEInput.rpoly))) = _menhir_stack in
            let _3 = () in
            let _1 = () in
            let _v : (PPEInput.rpoly) = 
# 88 "src/PPE/PPEParser.mly"
                            ( f )
# 499 "src/PPE/PPEParser.ml"
             in
            _menhir_goto_poly _menhir_env _menhir_stack _menhir_s _v
        | STAR ->
            _menhir_run9 _menhir_env (Obj.magic _menhir_stack)
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | MenhirState9 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | EXP ->
            _menhir_run11 _menhir_env (Obj.magic _menhir_stack)
        | COMMA | DIVIDES | MINUS | PLUS | RBRACK | RPAR | STAR ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let ((_menhir_stack, _menhir_s, (f : (PPEInput.rpoly))), _, (g : (PPEInput.rpoly))) = _menhir_stack in
            let _2 = () in
            let _v : (PPEInput.rpoly) = 
# 82 "src/PPE/PPEParser.mly"
                            ( RP.mult f g )
# 524 "src/PPE/PPEParser.ml"
             in
            _menhir_goto_poly _menhir_env _menhir_stack _menhir_s _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | MenhirState14 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | EXP ->
            _menhir_run11 _menhir_env (Obj.magic _menhir_stack)
        | STAR ->
            _menhir_run9 _menhir_env (Obj.magic _menhir_stack)
        | COMMA | DIVIDES | MINUS | PLUS | RBRACK | RPAR ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let ((_menhir_stack, _menhir_s, (f : (PPEInput.rpoly))), _, (g : (PPEInput.rpoly))) = _menhir_stack in
            let _2 = () in
            let _v : (PPEInput.rpoly) = 
# 81 "src/PPE/PPEParser.mly"
                            ( RP.add f g )
# 549 "src/PPE/PPEParser.ml"
             in
            _menhir_goto_poly _menhir_env _menhir_stack _menhir_s _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | MenhirState16 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | EXP ->
            _menhir_run11 _menhir_env (Obj.magic _menhir_stack)
        | STAR ->
            _menhir_run9 _menhir_env (Obj.magic _menhir_stack)
        | COMMA | DIVIDES | MINUS | PLUS | RBRACK | RPAR ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let ((_menhir_stack, _menhir_s, (f : (PPEInput.rpoly))), _, (g : (PPEInput.rpoly))) = _menhir_stack in
            let _2 = () in
            let _v : (PPEInput.rpoly) = 
# 83 "src/PPE/PPEParser.mly"
                            ( RP.minus f g )
# 574 "src/PPE/PPEParser.ml"
             in
            _menhir_goto_poly _menhir_env _menhir_stack _menhir_s _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | MenhirState4 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | EXP ->
            _menhir_run11 _menhir_env (Obj.magic _menhir_stack)
        | STAR ->
            _menhir_run9 _menhir_env (Obj.magic _menhir_stack)
        | COMMA | DIVIDES | MINUS | PLUS | RBRACK | RPAR ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let ((_menhir_stack, _menhir_s), _, (f : (PPEInput.rpoly))) = _menhir_stack in
            let _1 = () in
            let _v : (PPEInput.rpoly) = 
# 87 "src/PPE/PPEParser.mly"
                            ( RP.opp f )
# 599 "src/PPE/PPEParser.ml"
             in
            _menhir_goto_poly _menhir_env _menhir_stack _menhir_s _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | MenhirState23 | MenhirState2 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | COMMA ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let _menhir_env = _menhir_discard _menhir_env in
            let _tok = _menhir_env._menhir_token in
            (match _tok with
            | INT _v ->
                _menhir_run6 _menhir_env (Obj.magic _menhir_stack) MenhirState23 _v
            | LPAR ->
                _menhir_run5 _menhir_env (Obj.magic _menhir_stack) MenhirState23
            | MINUS ->
                _menhir_run4 _menhir_env (Obj.magic _menhir_stack) MenhirState23
            | VARU _v ->
                _menhir_run3 _menhir_env (Obj.magic _menhir_stack) MenhirState23 _v
            | _ ->
                assert (not _menhir_env._menhir_error);
                _menhir_env._menhir_error <- true;
                _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState23)
        | EXP ->
            _menhir_run11 _menhir_env (Obj.magic _menhir_stack)
        | MINUS ->
            _menhir_run16 _menhir_env (Obj.magic _menhir_stack)
        | PLUS ->
            _menhir_run14 _menhir_env (Obj.magic _menhir_stack)
        | STAR ->
            _menhir_run9 _menhir_env (Obj.magic _menhir_stack)
        | RBRACK ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, (x : (PPEInput.rpoly))) = _menhir_stack in
            let _v : (PPEInput.rpoly list) = 
# 229 "/Users/satya/.opam/autoppe/lib/menhir/standard.mly"
    ( [ x ] )
# 644 "src/PPE/PPEParser.ml"
             in
            _menhir_goto_separated_nonempty_list_COMMA_poly_ _menhir_env _menhir_stack _menhir_s _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | MenhirState28 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | DIVIDES ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let _menhir_env = _menhir_discard _menhir_env in
            let _tok = _menhir_env._menhir_token in
            (match _tok with
            | INT _v ->
                _menhir_run6 _menhir_env (Obj.magic _menhir_stack) MenhirState30 _v
            | LPAR ->
                _menhir_run5 _menhir_env (Obj.magic _menhir_stack) MenhirState30
            | MINUS ->
                _menhir_run4 _menhir_env (Obj.magic _menhir_stack) MenhirState30
            | VARU _v ->
                _menhir_run3 _menhir_env (Obj.magic _menhir_stack) MenhirState30 _v
            | _ ->
                assert (not _menhir_env._menhir_error);
                _menhir_env._menhir_error <- true;
                _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState30)
        | EXP ->
            _menhir_run11 _menhir_env (Obj.magic _menhir_stack)
        | MINUS ->
            _menhir_run16 _menhir_env (Obj.magic _menhir_stack)
        | PLUS ->
            _menhir_run14 _menhir_env (Obj.magic _menhir_stack)
        | STAR ->
            _menhir_run9 _menhir_env (Obj.magic _menhir_stack)
        | COMMA | RBRACK ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let ((_menhir_stack, _menhir_s, (s : (
# 48 "src/PPE/PPEParser.mly"
       (int)
# 688 "src/PPE/PPEParser.ml"
            ))), _, (f : (PPEInput.rpoly))) = _menhir_stack in
            let _2 = () in
            let _v : (temp) = 
# 106 "src/PPE/PPEParser.mly"
                              ( {fid = Param(s); pol = f; denom = RP.from_int  1} )
# 694 "src/PPE/PPEParser.ml"
             in
            _menhir_goto_polywithid _menhir_env _menhir_stack _menhir_s _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | MenhirState30 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | EXP ->
            _menhir_run11 _menhir_env (Obj.magic _menhir_stack)
        | MINUS ->
            _menhir_run16 _menhir_env (Obj.magic _menhir_stack)
        | PLUS ->
            _menhir_run14 _menhir_env (Obj.magic _menhir_stack)
        | STAR ->
            _menhir_run9 _menhir_env (Obj.magic _menhir_stack)
        | COMMA | RBRACK ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let (((_menhir_stack, _menhir_s, (s : (
# 48 "src/PPE/PPEParser.mly"
       (int)
# 721 "src/PPE/PPEParser.ml"
            ))), _, (f : (PPEInput.rpoly))), _, (g : (PPEInput.rpoly))) = _menhir_stack in
            let _4 = () in
            let _2 = () in
            let _v : (temp) = 
# 107 "src/PPE/PPEParser.mly"
                                                 ( {fid = Param(s); pol = f; denom = g} )
# 728 "src/PPE/PPEParser.ml"
             in
            _menhir_goto_polywithid _menhir_env _menhir_stack _menhir_s _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | _ ->
        _menhir_fail ()

and _menhir_goto_separated_nonempty_list_COMMA_iso_ : _menhir_env -> 'ttv_tail -> _menhir_state -> (PPEInput.iso list) -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s _v ->
    let _menhir_stack = (_menhir_stack, _menhir_s, _v) in
    match _menhir_s with
    | MenhirState50 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | DOT ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let _menhir_env = _menhir_discard _menhir_env in
            let _menhir_stack = Obj.magic _menhir_stack in
            let ((_menhir_stack, _menhir_s), _, (isos : (PPEInput.iso list))) = _menhir_stack in
            let _3 = () in
            let _1 = () in
            let _v : (PPEInput.cmd) = 
# 114 "src/PPE/PPEParser.mly"
  ( AddIsos isos )
# 759 "src/PPE/PPEParser.ml"
             in
            _menhir_goto_cmd _menhir_env _menhir_stack _menhir_s _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | MenhirState57 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_stack = Obj.magic _menhir_stack in
        let ((_menhir_stack, _menhir_s, (x : (PPEInput.iso))), _, (xs : (PPEInput.iso list))) = _menhir_stack in
        let _2 = () in
        let _v : (PPEInput.iso list) = 
# 231 "/Users/satya/.opam/autoppe/lib/menhir/standard.mly"
    ( x :: xs )
# 776 "src/PPE/PPEParser.ml"
         in
        _menhir_goto_separated_nonempty_list_COMMA_iso_ _menhir_env _menhir_stack _menhir_s _v
    | _ ->
        _menhir_fail ()

and _menhir_goto_separated_nonempty_list_STAR_GID_ : _menhir_env -> 'ttv_tail -> _menhir_state -> (PPEInput.group_id list) -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s _v ->
    let _menhir_stack = (_menhir_stack, _menhir_s, _v) in
    match _menhir_s with
    | MenhirState61 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_stack = Obj.magic _menhir_stack in
        let ((_menhir_stack, _menhir_s, (x : (
# 47 "src/PPE/PPEParser.mly"
       (string)
# 792 "src/PPE/PPEParser.ml"
        ))), _, (xs : (PPEInput.group_id list))) = _menhir_stack in
        let _2 = () in
        let _v : (PPEInput.group_id list) = 
# 231 "/Users/satya/.opam/autoppe/lib/menhir/standard.mly"
    ( x :: xs )
# 798 "src/PPE/PPEParser.ml"
         in
        _menhir_goto_separated_nonempty_list_STAR_GID_ _menhir_env _menhir_stack _menhir_s _v
    | MenhirState69 | MenhirState59 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | TO ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let _menhir_env = _menhir_discard _menhir_env in
            let _tok = _menhir_env._menhir_token in
            (match _tok with
            | GID _v ->
                let _menhir_stack = Obj.magic _menhir_stack in
                let _menhir_env = _menhir_discard _menhir_env in
                let _menhir_stack = Obj.magic _menhir_stack in
                let (codom : (
# 47 "src/PPE/PPEParser.mly"
       (string)
# 818 "src/PPE/PPEParser.ml"
                )) = _v in
                let (_menhir_stack, _menhir_s, (dom : (PPEInput.group_id list))) = _menhir_stack in
                let _2 = () in
                let _v : (PPEInput.emap) = 
# 102 "src/PPE/PPEParser.mly"
  ( { em_dom = dom; em_codom = codom } )
# 825 "src/PPE/PPEParser.ml"
                 in
                let _menhir_stack = (_menhir_stack, _menhir_s, _v) in
                let _menhir_stack = Obj.magic _menhir_stack in
                assert (not _menhir_env._menhir_error);
                let _tok = _menhir_env._menhir_token in
                (match _tok with
                | COMMA ->
                    let _menhir_stack = Obj.magic _menhir_stack in
                    let _menhir_env = _menhir_discard _menhir_env in
                    let _tok = _menhir_env._menhir_token in
                    (match _tok with
                    | GID _v ->
                        _menhir_run60 _menhir_env (Obj.magic _menhir_stack) MenhirState69 _v
                    | _ ->
                        assert (not _menhir_env._menhir_error);
                        _menhir_env._menhir_error <- true;
                        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState69)
                | DOT ->
                    let _menhir_stack = Obj.magic _menhir_stack in
                    let (_menhir_stack, _menhir_s, (x : (PPEInput.emap))) = _menhir_stack in
                    let _v : (PPEInput.emap list) = 
# 229 "/Users/satya/.opam/autoppe/lib/menhir/standard.mly"
    ( [ x ] )
# 849 "src/PPE/PPEParser.ml"
                     in
                    _menhir_goto_separated_nonempty_list_COMMA_emap_ _menhir_env _menhir_stack _menhir_s _v
                | _ ->
                    assert (not _menhir_env._menhir_error);
                    _menhir_env._menhir_error <- true;
                    let _menhir_stack = Obj.magic _menhir_stack in
                    let (_menhir_stack, _menhir_s, _) = _menhir_stack in
                    _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
            | _ ->
                assert (not _menhir_env._menhir_error);
                _menhir_env._menhir_error <- true;
                let _menhir_stack = Obj.magic _menhir_stack in
                let (_menhir_stack, _menhir_s, _) = _menhir_stack in
                _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | _ ->
        _menhir_fail ()

and _menhir_goto_list_cmd_ : _menhir_env -> 'ttv_tail -> _menhir_state -> (PPEInput.cmd list) -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s _v ->
    let _menhir_stack = (_menhir_stack, _menhir_s, _v) in
    match _menhir_s with
    | MenhirState0 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        assert (not _menhir_env._menhir_error);
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | EOF ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, (cs : (PPEInput.cmd list))) = _menhir_stack in
            let _2 = () in
            let _v : (
# 70 "src/PPE/PPEParser.mly"
       (PPEInput.cmd list)
# 890 "src/PPE/PPEParser.ml"
            ) = 
# 128 "src/PPE/PPEParser.mly"
                             ( cs )
# 894 "src/PPE/PPEParser.ml"
             in
            let _menhir_stack = Obj.magic _menhir_stack in
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_1 : (
# 70 "src/PPE/PPEParser.mly"
       (PPEInput.cmd list)
# 901 "src/PPE/PPEParser.ml"
            )) = _v in
            Obj.magic _1
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | MenhirState74 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_stack = Obj.magic _menhir_stack in
        let ((_menhir_stack, _menhir_s, (x : (PPEInput.cmd))), _, (xs : (PPEInput.cmd list))) = _menhir_stack in
        let _v : (PPEInput.cmd list) = 
# 201 "/Users/satya/.opam/autoppe/lib/menhir/standard.mly"
    ( x :: xs )
# 917 "src/PPE/PPEParser.ml"
         in
        _menhir_goto_list_cmd_ _menhir_env _menhir_stack _menhir_s _v
    | _ ->
        _menhir_fail ()

and _menhir_run3 : _menhir_env -> 'ttv_tail -> _menhir_state -> (
# 46 "src/PPE/PPEParser.mly"
       (string)
# 926 "src/PPE/PPEParser.ml"
) -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s _v ->
    let _menhir_env = _menhir_discard _menhir_env in
    let _menhir_stack = Obj.magic _menhir_stack in
    let (v : (
# 46 "src/PPE/PPEParser.mly"
       (string)
# 934 "src/PPE/PPEParser.ml"
    )) = _v in
    let _v : (PPEInput.RP.t) = 
# 93 "src/PPE/PPEParser.mly"
            ( RP.var v )
# 939 "src/PPE/PPEParser.ml"
     in
    let _menhir_stack = Obj.magic _menhir_stack in
    let _menhir_stack = Obj.magic _menhir_stack in
    let (v : (PPEInput.RP.t)) = _v in
    let _v : (PPEInput.rpoly) = 
# 80 "src/PPE/PPEParser.mly"
                            ( v )
# 947 "src/PPE/PPEParser.ml"
     in
    _menhir_goto_poly _menhir_env _menhir_stack _menhir_s _v

and _menhir_run4 : _menhir_env -> 'ttv_tail -> _menhir_state -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s ->
    let _menhir_stack = (_menhir_stack, _menhir_s) in
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | INT _v ->
        _menhir_run6 _menhir_env (Obj.magic _menhir_stack) MenhirState4 _v
    | LPAR ->
        _menhir_run5 _menhir_env (Obj.magic _menhir_stack) MenhirState4
    | MINUS ->
        _menhir_run4 _menhir_env (Obj.magic _menhir_stack) MenhirState4
    | VARU _v ->
        _menhir_run3 _menhir_env (Obj.magic _menhir_stack) MenhirState4 _v
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState4

and _menhir_run5 : _menhir_env -> 'ttv_tail -> _menhir_state -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s ->
    let _menhir_stack = (_menhir_stack, _menhir_s) in
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | INT _v ->
        _menhir_run6 _menhir_env (Obj.magic _menhir_stack) MenhirState5 _v
    | LPAR ->
        _menhir_run5 _menhir_env (Obj.magic _menhir_stack) MenhirState5
    | MINUS ->
        _menhir_run4 _menhir_env (Obj.magic _menhir_stack) MenhirState5
    | VARU _v ->
        _menhir_run3 _menhir_env (Obj.magic _menhir_stack) MenhirState5 _v
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState5

and _menhir_run6 : _menhir_env -> 'ttv_tail -> _menhir_state -> (
# 58 "src/PPE/PPEParser.mly"
       (int)
# 992 "src/PPE/PPEParser.ml"
) -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s _v ->
    let _menhir_env = _menhir_discard _menhir_env in
    let _menhir_stack = Obj.magic _menhir_stack in
    let (i : (
# 58 "src/PPE/PPEParser.mly"
       (int)
# 1000 "src/PPE/PPEParser.ml"
    )) = _v in
    let _v : (PPEInput.rpoly) = 
# 89 "src/PPE/PPEParser.mly"
                            ( RP.from_int i )
# 1005 "src/PPE/PPEParser.ml"
     in
    _menhir_goto_poly _menhir_env _menhir_stack _menhir_s _v

and _menhir_run27 : _menhir_env -> 'ttv_tail -> _menhir_state -> (
# 48 "src/PPE/PPEParser.mly"
       (int)
# 1012 "src/PPE/PPEParser.ml"
) -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s _v ->
    let _menhir_stack = (_menhir_stack, _menhir_s, _v) in
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | EQUALS ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_env = _menhir_discard _menhir_env in
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | INT _v ->
            _menhir_run6 _menhir_env (Obj.magic _menhir_stack) MenhirState28 _v
        | LPAR ->
            _menhir_run5 _menhir_env (Obj.magic _menhir_stack) MenhirState28
        | MINUS ->
            _menhir_run4 _menhir_env (Obj.magic _menhir_stack) MenhirState28
        | VARU _v ->
            _menhir_run3 _menhir_env (Obj.magic _menhir_stack) MenhirState28 _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState28)
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s

and _menhir_goto_cmd : _menhir_env -> 'ttv_tail -> _menhir_state -> (PPEInput.cmd) -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s _v ->
    let _menhir_stack = (_menhir_stack, _menhir_s, _v) in
    let _menhir_stack = Obj.magic _menhir_stack in
    assert (not _menhir_env._menhir_error);
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | EMAPS ->
        _menhir_run59 _menhir_env (Obj.magic _menhir_stack) MenhirState74
    | ISOS ->
        _menhir_run50 _menhir_env (Obj.magic _menhir_stack) MenhirState74
    | ORDER ->
        _menhir_run47 _menhir_env (Obj.magic _menhir_stack) MenhirState74
    | TRUSTED ->
        _menhir_run40 _menhir_env (Obj.magic _menhir_stack) MenhirState74
    | UNTRUSTED ->
        _menhir_run25 _menhir_env (Obj.magic _menhir_stack) MenhirState74
    | ZP ->
        _menhir_run1 _menhir_env (Obj.magic _menhir_stack) MenhirState74
    | EOF ->
        _menhir_reduce10 _menhir_env (Obj.magic _menhir_stack) MenhirState74
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState74

and _menhir_run51 : _menhir_env -> 'ttv_tail -> _menhir_state -> (
# 47 "src/PPE/PPEParser.mly"
       (string)
# 1072 "src/PPE/PPEParser.ml"
) -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s _v ->
    let _menhir_stack = (_menhir_stack, _menhir_s, _v) in
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | TO ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_env = _menhir_discard _menhir_env in
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | GID _v ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let _menhir_env = _menhir_discard _menhir_env in
            let _menhir_stack = Obj.magic _menhir_stack in
            let (codom : (
# 47 "src/PPE/PPEParser.mly"
       (string)
# 1091 "src/PPE/PPEParser.ml"
            )) = _v in
            let (_menhir_stack, _menhir_s, (dom : (
# 47 "src/PPE/PPEParser.mly"
       (string)
# 1096 "src/PPE/PPEParser.ml"
            ))) = _menhir_stack in
            let _2 = () in
            let _v : (PPEInput.iso) = 
# 97 "src/PPE/PPEParser.mly"
                             ( { iso_dom = dom; iso_codom = codom } )
# 1102 "src/PPE/PPEParser.ml"
             in
            let _menhir_stack = (_menhir_stack, _menhir_s, _v) in
            let _menhir_stack = Obj.magic _menhir_stack in
            assert (not _menhir_env._menhir_error);
            let _tok = _menhir_env._menhir_token in
            (match _tok with
            | COMMA ->
                let _menhir_stack = Obj.magic _menhir_stack in
                let _menhir_env = _menhir_discard _menhir_env in
                let _tok = _menhir_env._menhir_token in
                (match _tok with
                | GID _v ->
                    _menhir_run51 _menhir_env (Obj.magic _menhir_stack) MenhirState57 _v
                | _ ->
                    assert (not _menhir_env._menhir_error);
                    _menhir_env._menhir_error <- true;
                    _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState57)
            | DOT ->
                let _menhir_stack = Obj.magic _menhir_stack in
                let (_menhir_stack, _menhir_s, (x : (PPEInput.iso))) = _menhir_stack in
                let _v : (PPEInput.iso list) = 
# 229 "/Users/satya/.opam/autoppe/lib/menhir/standard.mly"
    ( [ x ] )
# 1126 "src/PPE/PPEParser.ml"
                 in
                _menhir_goto_separated_nonempty_list_COMMA_iso_ _menhir_env _menhir_stack _menhir_s _v
            | _ ->
                assert (not _menhir_env._menhir_error);
                _menhir_env._menhir_error <- true;
                let _menhir_stack = Obj.magic _menhir_stack in
                let (_menhir_stack, _menhir_s, _) = _menhir_stack in
                _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let (_menhir_stack, _menhir_s, _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s

and _menhir_run60 : _menhir_env -> 'ttv_tail -> _menhir_state -> (
# 47 "src/PPE/PPEParser.mly"
       (string)
# 1151 "src/PPE/PPEParser.ml"
) -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s _v ->
    let _menhir_stack = (_menhir_stack, _menhir_s, _v) in
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | STAR ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_env = _menhir_discard _menhir_env in
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | GID _v ->
            _menhir_run60 _menhir_env (Obj.magic _menhir_stack) MenhirState61 _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState61)
    | TO ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, (x : (
# 47 "src/PPE/PPEParser.mly"
       (string)
# 1174 "src/PPE/PPEParser.ml"
        ))) = _menhir_stack in
        let _v : (PPEInput.group_id list) = 
# 229 "/Users/satya/.opam/autoppe/lib/menhir/standard.mly"
    ( [ x ] )
# 1179 "src/PPE/PPEParser.ml"
         in
        _menhir_goto_separated_nonempty_list_STAR_GID_ _menhir_env _menhir_stack _menhir_s _v
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s

and _menhir_errorcase : _menhir_env -> 'ttv_tail -> _menhir_state -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s ->
    match _menhir_s with
    | MenhirState74 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState69 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState61 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState59 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState57 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState50 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState41 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState38 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState30 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState28 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState26 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState23 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState16 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState14 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState9 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s, _) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState5 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState4 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState2 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s
    | MenhirState0 ->
        let _menhir_stack = Obj.magic _menhir_stack in
        raise _eRR

and _menhir_reduce10 : _menhir_env -> 'ttv_tail -> _menhir_state -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s ->
    let _v : (PPEInput.cmd list) = 
# 199 "/Users/satya/.opam/autoppe/lib/menhir/standard.mly"
    ( [] )
# 1273 "src/PPE/PPEParser.ml"
     in
    _menhir_goto_list_cmd_ _menhir_env _menhir_stack _menhir_s _v

and _menhir_run1 : _menhir_env -> 'ttv_tail -> _menhir_state -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s ->
    let _menhir_stack = (_menhir_stack, _menhir_s) in
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | LBRACK ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_env = _menhir_discard _menhir_env in
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | INT _v ->
            _menhir_run6 _menhir_env (Obj.magic _menhir_stack) MenhirState2 _v
        | LPAR ->
            _menhir_run5 _menhir_env (Obj.magic _menhir_stack) MenhirState2
        | MINUS ->
            _menhir_run4 _menhir_env (Obj.magic _menhir_stack) MenhirState2
        | VARU _v ->
            _menhir_run3 _menhir_env (Obj.magic _menhir_stack) MenhirState2 _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState2)
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s

and _menhir_run25 : _menhir_env -> 'ttv_tail -> _menhir_state -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s ->
    let _menhir_stack = (_menhir_stack, _menhir_s) in
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | LBRACK ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_env = _menhir_discard _menhir_env in
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | FID _v ->
            _menhir_run27 _menhir_env (Obj.magic _menhir_stack) MenhirState26 _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState26)
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s

and _menhir_run40 : _menhir_env -> 'ttv_tail -> _menhir_state -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s ->
    let _menhir_stack = (_menhir_stack, _menhir_s) in
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | LBRACK ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_env = _menhir_discard _menhir_env in
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | FID _v ->
            _menhir_run27 _menhir_env (Obj.magic _menhir_stack) MenhirState41 _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState41)
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s

and _menhir_run47 : _menhir_env -> 'ttv_tail -> _menhir_state -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s ->
    let _menhir_stack = (_menhir_stack, _menhir_s) in
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | INT _v ->
        let _menhir_stack = Obj.magic _menhir_stack in
        let _menhir_stack = (_menhir_stack, _v) in
        let _menhir_env = _menhir_discard _menhir_env in
        let _tok = _menhir_env._menhir_token in
        (match _tok with
        | DOT ->
            let _menhir_stack = Obj.magic _menhir_stack in
            let _menhir_env = _menhir_discard _menhir_env in
            let _menhir_stack = Obj.magic _menhir_stack in
            let ((_menhir_stack, _menhir_s), (i : (
# 58 "src/PPE/PPEParser.mly"
       (int)
# 1374 "src/PPE/PPEParser.ml"
            ))) = _menhir_stack in
            let _3 = () in
            let _1 = () in
            let _v : (PPEInput.cmd) = 
# 116 "src/PPE/PPEParser.mly"
  ( SetPrimeNum i )
# 1381 "src/PPE/PPEParser.ml"
             in
            _menhir_goto_cmd _menhir_env _menhir_stack _menhir_s _v
        | _ ->
            assert (not _menhir_env._menhir_error);
            _menhir_env._menhir_error <- true;
            let _menhir_stack = Obj.magic _menhir_stack in
            let ((_menhir_stack, _menhir_s), _) = _menhir_stack in
            _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s)
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        let _menhir_stack = Obj.magic _menhir_stack in
        let (_menhir_stack, _menhir_s) = _menhir_stack in
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) _menhir_s

and _menhir_run50 : _menhir_env -> 'ttv_tail -> _menhir_state -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s ->
    let _menhir_stack = (_menhir_stack, _menhir_s) in
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | GID _v ->
        _menhir_run51 _menhir_env (Obj.magic _menhir_stack) MenhirState50 _v
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState50

and _menhir_run59 : _menhir_env -> 'ttv_tail -> _menhir_state -> 'ttv_return =
  fun _menhir_env _menhir_stack _menhir_s ->
    let _menhir_stack = (_menhir_stack, _menhir_s) in
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | GID _v ->
        _menhir_run60 _menhir_env (Obj.magic _menhir_stack) MenhirState59 _v
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState59

and _menhir_discard : _menhir_env -> _menhir_env =
  fun _menhir_env ->
    let lexer = _menhir_env._menhir_lexer in
    let lexbuf = _menhir_env._menhir_lexbuf in
    let _tok = lexer lexbuf in
    {
      _menhir_lexer = lexer;
      _menhir_lexbuf = lexbuf;
      _menhir_token = _tok;
      _menhir_error = false;
    }

and cmds_t : (Lexing.lexbuf -> token) -> Lexing.lexbuf -> (
# 70 "src/PPE/PPEParser.mly"
       (PPEInput.cmd list)
# 1438 "src/PPE/PPEParser.ml"
) =
  fun lexer lexbuf ->
    let _menhir_env = let _tok = Obj.magic () in
    {
      _menhir_lexer = lexer;
      _menhir_lexbuf = lexbuf;
      _menhir_token = _tok;
      _menhir_error = false;
    } in
    Obj.magic (let _menhir_stack = ((), _menhir_env._menhir_lexbuf.Lexing.lex_curr_p) in
    let _menhir_env = _menhir_discard _menhir_env in
    let _tok = _menhir_env._menhir_token in
    match _tok with
    | EMAPS ->
        _menhir_run59 _menhir_env (Obj.magic _menhir_stack) MenhirState0
    | ISOS ->
        _menhir_run50 _menhir_env (Obj.magic _menhir_stack) MenhirState0
    | ORDER ->
        _menhir_run47 _menhir_env (Obj.magic _menhir_stack) MenhirState0
    | TRUSTED ->
        _menhir_run40 _menhir_env (Obj.magic _menhir_stack) MenhirState0
    | UNTRUSTED ->
        _menhir_run25 _menhir_env (Obj.magic _menhir_stack) MenhirState0
    | ZP ->
        _menhir_run1 _menhir_env (Obj.magic _menhir_stack) MenhirState0
    | EOF ->
        _menhir_reduce10 _menhir_env (Obj.magic _menhir_stack) MenhirState0
    | _ ->
        assert (not _menhir_env._menhir_error);
        _menhir_env._menhir_error <- true;
        _menhir_errorcase _menhir_env (Obj.magic _menhir_stack) MenhirState0)

# 233 "/Users/satya/.opam/autoppe/lib/menhir/standard.mly"
  

# 1474 "src/PPE/PPEParser.ml"
