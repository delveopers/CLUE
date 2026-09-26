import random
from ..engine.chess.state import GameState
from ..engine.chess.rules import legal_moves

def board_snapshot(state):
  return ([r[:] for r in state.board.state], state.side_to_move, state.castling_rights(), state.en_passant_square, state.halfmove_clock, state.fullmove_number)

def empty_state(side_to_move=1):
  state = GameState.initial()
  for r in range(8):
    for c in range(8): state.board.state[r][c] = 0
  state.side_to_move = side_to_move
  return state

def test_initial_position_has_twenty_legal_moves():
  assert len(legal_moves(GameState.initial())) == 20

def test_random_move_round_trip_is_exact():
  random.seed(0)
  state = GameState.initial()
  for _ in range(300):
    moves = legal_moves(state)
    if not moves:
      state = GameState.initial()
      continue
    before = board_snapshot(state)
    move = random.choice(moves)
    state.make_move(move)
    state.unmake_move()
    assert board_snapshot(state) == before
    state.make_move(random.choice(moves))

def test_castling_moves_king_and_rook_and_unmakes_cleanly():
  state = empty_state()
  state.board.state[7][4], state.board.state[7][7] = 6, 4
  move = next(m for m in legal_moves(state) if m.is_castle())
  state.make_move(move)
  assert state.board.state[7][6] == 6
  assert state.board.state[7][5] == 4
  state.unmake_move()
  assert state.board.state[7][4] == 6
  assert state.board.state[7][7] == 4

def test_en_passant_capture_and_unmake():
  state = empty_state()
  state.board.state[6][4], state.board.state[4][3] = 1, -1
  state.board.state[7][4], state.board.state[0][4] = 6, -6
  double_step = next(m for m in legal_moves(state) if m.from_row == 6 and m.to_row == 4)
  state.make_move(double_step)
  assert state.en_passant_square == (5, 4)
  capture = next(m for m in legal_moves(state) if m.is_en_passant())
  state.make_move(capture)
  assert state.board.state[4][4] == 0
  assert state.board.state[5][4] == -1
  state.unmake_move()
  assert state.board.state[4][4] == 1

def test_promotion_choices_and_unmake():
  state = empty_state()
  state.board.state[1][0], state.board.state[7][4], state.board.state[0][4] = 1, 6, -6
  promotions = [m for m in legal_moves(state) if m.is_promotion()]
  assert len(promotions) == 4
  queen_promo = next(m for m in promotions if m.promotion == 5)
  state.make_move(queen_promo)
  assert state.board.state[0][0] == 5
  state.unmake_move()
  assert state.board.state[1][0] == 1

def test_capturing_rook_on_home_square_revokes_castling_right():
  state = empty_state()
  state.board.state[7][4], state.board.state[0][4], state.board.state[7][0] = 6, -6, 4
  state.board.state[0][0] = -5
  state.white_kingside, state.white_queenside = False, True
  state.side_to_move = -1
  capture = next(m for m in legal_moves(state) if m.to_row == 7 and m.to_col == 0)
  state.make_move(capture)
  assert state.white_queenside is False