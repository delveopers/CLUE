import random
from ..engine.chess.state import GameState
from ..engine.chess import zobrist
from ..engine.chess.rules import legal_moves

def test_initial_hash_matches_recompute():
  state = GameState.initial()
  assert state.hash == zobrist.compute_hash(state)

def test_incremental_hash_matches_recompute_over_random_moves():
  random.seed(1)
  state = GameState.initial()
  for _ in range(500):
    moves = legal_moves(state)
    if not moves:
      state = GameState.initial()
      continue
    move = random.choice(moves)
    hash_before = state.hash
    state.make_move(move)
    assert state.hash == zobrist.compute_hash(state)
    state.unmake_move()
    assert state.hash == hash_before
    state.make_move(random.choice(moves))

def test_transposition_reaches_same_hash():
  state = GameState.initial()
  n1 = next(m for m in legal_moves(state) if state.board.state[m.from_row][m.from_col] == 2 and m.to_col == 5)
  state.make_move(n1)
  n2 = next(m for m in legal_moves(state) if state.board.state[m.from_row][m.from_col] == -2 and m.to_col == 5)
  state.make_move(n2)
  n3 = next(m for m in legal_moves(state) if m.from_square == n1.to_square and m.to_square == n1.from_square)
  state.make_move(n3)
  n4 = next(m for m in legal_moves(state) if m.from_square == n2.to_square and m.to_square == n2.from_square)
  state.make_move(n4)
  assert state.hash == GameState.initial().hash

def test_castling_rights_affect_hash():
  assert GameState.initial().hash != GameState(white_kingside=False).hash

def test_side_to_move_affects_hash():
  assert GameState.initial().hash != GameState(side_to_move=-1).hash

def test_en_passant_square_affects_hash():
  with_ep = GameState(en_passant_square=(2, 3))
  without_ep = GameState(en_passant_square=None)
  assert with_ep.hash != without_ep.hash