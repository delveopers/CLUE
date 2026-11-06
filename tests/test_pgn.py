import pytest
from engine.chess.pgn import iter_games, load_pgn_file, san_to_move, replay, PGNError
from engine.chess.fen import parse_fen, to_fen
from engine.chess.state import GameState
from chess import rules

FOOLS_MATE = '[Event "fool"]\n[Result "0-1"]\n\n1. f3 e5 2. g4 Qh4# 0-1\n'
SCHOLARS_MATE = '[Event "scholar"]\n[Result "1-0"]\n\n1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7# 1-0\n'

def final_state(game):
  state = None
  for state, _ in replay(game): pass
  return state

def test_fools_mate_resolves_and_ends_in_black_win():
  game = next(iter_games(FOOLS_MATE))
  assert len(game.moves) == 4
  assert game.result == -1
  assert rules.result(final_state(game)) == rules.BLACK_WIN

def test_scholars_mate_final_position():
  game = next(iter_games(SCHOLARS_MATE))
  assert game.result == 1
  assert to_fen(final_state(game)) == 'r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4'

def test_castling_for_both_sides_and_unfinished_result():
  game = next(iter_games('1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. O-O Nf6 5. d3 O-O *'))
  assert game.moves[6].is_castle() and game.moves[9].is_castle()
  assert game.result is None

def test_zero_style_castling_notation():
  game = next(iter_games('1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. 0-0 Nf6 *'))
  assert game.moves[6].is_castle()

def test_en_passant_capture_resolves():
  game = next(iter_games('1. e4 a6 2. e5 d5 3. exd6 *'))
  assert game.moves[4].is_en_passant()

def test_promotion_and_underpromotion():
  header = '[FEN "7k/P7/8/8/8/8/8/4K3 w - - 0 1"]\n\n'
  queen = next(iter_games(header + '1. a8=Q+ *'))
  knight = next(iter_games(header + '1. a8=N *'))
  assert queen.moves[0].promotion == 5
  assert knight.moves[0].promotion == 2

def test_knight_disambiguation_by_file():
  state = parse_fen('4k3/8/8/8/8/2N1N3/8/4K3 w - - 0 1')
  assert san_to_move(state, 'Ncd5').from_col == 2
  assert san_to_move(state, 'Ned5').from_col == 4
  with pytest.raises(PGNError):
    san_to_move(state, 'Nd5')

def test_knight_disambiguation_by_rank():
  state = parse_fen('7k/8/8/2N5/8/8/8/2N1K3 w - - 0 1')
  assert san_to_move(state, 'N1d3').from_row == 7
  assert san_to_move(state, 'N5d3').from_row == 3
  with pytest.raises(PGNError):
    san_to_move(state, 'Nd3')

def test_comments_variations_and_nags_are_stripped():
  text = '1. e4 {best by test} e5 (1... c5 2. Nf3 (2. c3) 2... d6) 2. Nf3 $1 Nc6 ; trailing comment\n3. Bb5 1/2-1/2'
  game = next(iter_games(text))
  assert len(game.moves) == 5
  assert game.result == 0

def test_lichess_style_clock_comments():
  game = next(iter_games('1. e4 { [%clk 0:03:00] } e5 { [%clk 0:03:00] } 2. Nf3 { [%clk 0:02:58] } 1-0'))
  assert len(game.moves) == 3

def test_annotation_symbols_are_stripped():
  game = next(iter_games('1. e4! e5?! 2. Nf3!! Nc6?? *'))
  assert len(game.moves) == 4

def test_multiple_games_are_split_correctly():
  games = list(iter_games(FOOLS_MATE + '\n' + SCHOLARS_MATE))
  assert [len(g.moves) for g in games] == [4, 7]
  assert [g.result for g in games] == [-1, 1]

def test_illegal_move_game_is_skipped_by_default():
  bad = '[Event "bad"]\n\n1. e4 e5 2. Qxh7 *\n'
  games = list(iter_games(bad + '\n' + FOOLS_MATE))
  assert len(games) == 1
  assert games[0].headers['Event'] == 'fool'

def test_illegal_move_game_raises_when_strict():
  with pytest.raises(PGNError):
    list(iter_games('1. e4 e5 2. Qxh7 *', skip_invalid=False))

def test_unparseable_token_rejected():
  with pytest.raises(PGNError):
    san_to_move(GameState.initial(), 'Zz9')

def test_fen_header_sets_start_position():
  game = next(iter_games('[FEN "7k/P7/8/8/8/8/8/4K3 w - - 0 1"]\n\n1. a8=Q+ *'))
  assert game.start_fen == '7k/P7/8/8/8/8/8/4K3 w - - 0 1'
  assert to_fen(final_state(game)).startswith('Q6k/')

def test_invalid_fen_header_is_rejected():
  with pytest.raises(PGNError):
    list(iter_games('[FEN "garbage"]\n\n1. e4 *', skip_invalid=False))

def test_unsupported_variant_is_rejected():
  with pytest.raises(PGNError):
    list(iter_games('[Variant "Chess960"]\n\n1. e4 e5 *', skip_invalid=False))

def test_result_falls_back_to_header_when_movetext_has_none():
  game = next(iter_games('[Result "1/2-1/2"]\n\n1. e4 e5'))
  assert game.result == 0

def test_replay_yields_each_position_before_its_move():
  game = next(iter_games(SCHOLARS_MATE))
  seen = 0
  for state, move in replay(game):
    assert move in rules.legal_moves(state)
    assert state.side_to_move == (1 if seen % 2 == 0 else -1)
    seen += 1
  assert seen == len(game.moves)

def test_load_pgn_file_streams_games(tmp_path):
  path = tmp_path / 'games.pgn'
  path.write_text(FOOLS_MATE + '\n' + SCHOLARS_MATE, encoding='utf-8')
  games = list(load_pgn_file(path))
  assert len(games) == 2

OPERA_GAME = '[Event "Opera Game"]\n[Result "1-0"]\n\n1. e4 e5 2. Nf3 d6 3. d4 Bg4 4. dxe5 Bxf3 5. Qxf3 dxe5 6. Bc4 Nf6 7. Qb3 Qe7 8. Nc3 c6 9. Bg5 b5 10. Nxb5 cxb5 11. Bxb5+ Nbd7 12. O-O-O Rd8 13. Rxd7 Rxd7 14. Rd1 Qe6 15. Bxd7+ Nxd7 16. Qb8+ Nxb8 17. Rd8# 1-0\n'

def test_opera_game_real_world_game_ends_in_white_checkmate():
  game = next(iter_games(OPERA_GAME))
  assert len(game.moves) == 33
  assert game.result == 1
  assert rules.result(final_state(game)) == rules.WHITE_WIN