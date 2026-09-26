import numpy as np
from engine.chess.state import GameState
from engine.chess.fen import parse_fen
from engine.chess.rules import legal_moves
from engine.encoding.position_encoder import encode, NUM_PLANES

def test_encoding_shape_and_dtype():
  planes = encode(GameState.initial())
  assert planes.shape == (NUM_PLANES, 8, 8)
  assert planes.dtype == np.float32

def test_encoding_is_binary_valued():
  planes = encode(GameState.initial())
  assert set(np.unique(planes)).issubset({0.0, 1.0})

def test_white_pawn_plane_matches_starting_rank():
  planes = encode(GameState.initial())
  assert planes[0, 6, :].sum() == 8
  assert planes[0].sum() == 8

def test_black_pawn_plane_matches_starting_rank():
  planes = encode(GameState.initial())
  assert planes[6, 1, :].sum() == 8

def test_king_planes_point_to_correct_squares():
  planes = encode(GameState.initial())
  assert planes[5, 7, 4] == 1.0
  assert planes[11, 0, 4] == 1.0

def test_side_to_move_plane_reflects_white_to_move():
  planes = encode(GameState.initial())
  assert planes[12].sum() == 64

def test_side_to_move_plane_is_always_all_ones_now_that_perspective_is_canonical():
  state = GameState.initial()
  state.make_move(next(iter(legal_moves(state))))
  planes = encode(state)
  assert planes[12].sum() == 64

def test_castling_planes_all_set_initially():
  planes = encode(GameState.initial())
  assert planes[13].sum() == 64
  assert planes[14].sum() == 64
  assert planes[15].sum() == 64
  assert planes[16].sum() == 64

def test_castling_plane_clears_after_right_revoked():
  state = GameState(white_kingside=False)
  planes = encode(state)
  assert planes[13].sum() == 0
  assert planes[14].sum() == 64

def test_en_passant_plane_empty_initially():
  planes = encode(GameState.initial())
  assert planes[17].sum() == 0

def test_en_passant_plane_marks_correct_square_after_double_step():
  state = GameState.initial()
  double_step = next(m for m in legal_moves(state) if state.board.state[m.from_row][m.from_col] == 1 and abs(m.to_row - m.from_row) == 2)
  state.make_move(double_step)
  planes = encode(state)
  expected_row = 7 - state.en_passant_square[0]
  assert planes[17].sum() == 1.0
  assert planes[17, expected_row, state.en_passant_square[1]] == 1.0

def test_kiwipete_encoding_piece_count_matches_board():
  state = parse_fen('r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1')
  planes = encode(state)
  total_pieces = sum(1 for row in state.board.state for p in row if p != 0)
  assert planes[:12].sum() == total_pieces

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

def test_untouched_pawn_plane_is_at_canonical_row_six_for_either_side_to_move():
  white_to_move_planes = encode(GameState.initial())
  black_state = GameState.initial()
  black_state.make_move(next(iter(legal_moves(black_state))))
  black_to_move_planes = encode(black_state)
  assert white_to_move_planes[0, 6, :].sum() == 8
  assert black_to_move_planes[0, 6, :].sum() == 8

def test_opponent_king_plane_is_at_canonical_row_zero_for_either_side_to_move():
  white_to_move_planes = encode(GameState.initial())
  black_state = GameState.initial()
  black_state.make_move(next(iter(legal_moves(black_state))))
  black_to_move_planes = encode(black_state)
  assert white_to_move_planes[11, 0, 4] == 1.0
  assert black_to_move_planes[11, 0, 4] == 1.0

def test_color_swapped_mirror_position_produces_identical_encoding():
  state = GameState.initial()
  mirrored = _mirror_state(state)
  assert np.array_equal(encode(state), encode(mirrored))

def test_color_swapped_mirror_position_produces_identical_encoding_mid_game():
  state = GameState.initial()
  moves = legal_moves(state)
  state.make_move(next(m for m in moves if state.board.state[m.from_row][m.from_col] == 1 and abs(m.to_row - m.from_row) == 2))
  mirrored = _mirror_state(state)
  assert np.array_equal(encode(state), encode(mirrored))