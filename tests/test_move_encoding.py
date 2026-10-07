import random
from engine.chess.state import GameState
from engine.chess.move import Move
from engine.chess.fen import parse_fen
from engine.chess.rules import legal_moves
from engine.encoding.move_encoder import move_to_index, index_to_move, ACTION_SPACE_SIZE

KIWIPETE_FEN = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1'

def _mirror_state(state):
  mirrored = GameState()
  for r in range(8):
    for c in range(8):
      mirrored.board.state[r][c] = -state.board.state[7 - r][c]
  mirrored.side_to_move = -state.side_to_move
  mirrored.white_kingside, mirrored.black_kingside = state.black_kingside, state.white_kingside
  mirrored.white_queenside, mirrored.black_queenside = state.black_queenside, state.white_queenside
  mirrored.en_passant_square = None if state.en_passant_square is None else (7 - state.en_passant_square[0], state.en_passant_square[1])
  return mirrored

def _mirror_move(move):
  return Move(7 - move.from_row, move.from_col, 7 - move.to_row, move.to_col, promotion=move.promotion, flag=move.flag)

def test_action_space_size():
  assert ACTION_SPACE_SIZE == 8 * 8 * 73

def test_round_trip_across_random_game():
  random.seed(5)
  state = GameState.initial()
  checked = 0
  for _ in range(60):
    moves = legal_moves(state)
    if not moves:
      state = GameState.initial()
      continue
    for move in moves:
      index = move_to_index(move, state)
      assert 0 <= index < ACTION_SPACE_SIZE
      assert index_to_move(index, state) == move
      checked += 1
    state.make_move(random.choice(moves))
  assert checked > 0

def test_round_trip_including_castling_kiwipete():
  state = parse_fen(KIWIPETE_FEN)
  for move in legal_moves(state):
    assert index_to_move(move_to_index(move, state), state) == move

def test_round_trip_black_to_move_castling():
  state = parse_fen('r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1')
  castles = [m for m in legal_moves(state) if m.is_castle()]
  assert len(castles) == 2
  for move in castles:
    assert index_to_move(move_to_index(move, state), state) == move

def test_round_trip_underpromotions():
  state = GameState()
  for r in range(8):
    for c in range(8): state.board.state[r][c] = 0
  state.board.state[1][0], state.board.state[7][4], state.board.state[0][4] = 1, 6, -6
  for move in [m for m in legal_moves(state) if m.is_promotion()]:
    assert index_to_move(move_to_index(move, state), state) == move

def test_round_trip_en_passant():
  state = GameState()
  for r in range(8):
    for c in range(8): state.board.state[r][c] = 0
  state.board.state[6][4], state.board.state[4][3] = 1, -1
  state.board.state[7][4], state.board.state[0][4] = 6, -6
  double_step = next(m for m in legal_moves(state) if m.from_row == 6 and m.to_row == 4)
  state.make_move(double_step)
  ep_capture = next(m for m in legal_moves(state) if m.is_en_passant())
  assert index_to_move(move_to_index(ep_capture, state), state) == ep_capture

def test_bogus_index_returns_none():
  state = GameState.initial()
  assert index_to_move(999999, state) is None

def test_color_mirrored_move_has_identical_index_to_original():
  state = GameState.initial()
  moves = legal_moves(state)
  mirrored_state = _mirror_state(state)

  for move in moves:
    mirrored_move = _mirror_move(move)
    assert move_to_index(move, state) == move_to_index(mirrored_move, mirrored_state)

def test_color_mirrored_castling_has_identical_index():
  state = parse_fen('r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1')
  mirrored_state = _mirror_state(state)
  castles = [m for m in legal_moves(state) if m.is_castle()]

  for move in castles:
    mirrored_move = _mirror_move(move)
    assert move_to_index(move, state) == move_to_index(mirrored_move, mirrored_state)