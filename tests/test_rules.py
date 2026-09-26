from ..engine.chess.state import GameState
from ..engine.chess.rules import legal_moves, result, is_terminal, ONGOING, WHITE_WIN, BLACK_WIN, DRAW

def empty_state(side_to_move=1):
  state = GameState.initial()
  for r in range(8):
    for c in range(8): state.board.state[r][c] = 0
  state.side_to_move = side_to_move
  return state

def test_initial_position_is_ongoing():
  state = GameState.initial()
  assert result(state) == ONGOING
  assert not is_terminal(state)

def test_back_rank_checkmate():
  state = empty_state(side_to_move=-1)
  state.board.state[0][0], state.board.state[0][7] = 4, -6
  state.board.state[1][5], state.board.state[1][6], state.board.state[1][7] = -1, -1, -1
  state.board.state[7][4] = 6
  assert legal_moves(state) == []
  assert result(state) == WHITE_WIN
  assert is_terminal(state)

def test_stalemate():
  state = empty_state(side_to_move=-1)
  state.board.state[0][0] = -6
  state.board.state[2][1] = 5
  state.board.state[7][7] = 6
  assert legal_moves(state) == []
  assert result(state) == DRAW

def test_fifty_move_rule():
  state = empty_state(side_to_move=1)
  state.board.state[7][4], state.board.state[0][4] = 6, -6
  state.board.state[6][0] = 1
  state.halfmove_clock = 100
  assert result(state) == DRAW

def test_no_fifty_move_draw_below_threshold():
  state = empty_state(side_to_move=1)
  state.board.state[7][4], state.board.state[0][4] = 6, -6
  state.board.state[6][0] = 1
  state.halfmove_clock = 99
  assert result(state) == ONGOING

def test_threefold_repetition():
  state = GameState.initial()

  def shuffle_out_and_back():
    m1 = next(m for m in legal_moves(state) if state.board.state[m.from_row][m.from_col] == 2 and m.to_col == 5)
    state.make_move(m1)
    m2 = next(m for m in legal_moves(state) if state.board.state[m.from_row][m.from_col] == -2 and m.to_col == 5)
    state.make_move(m2)
    m3 = next(m for m in legal_moves(state) if m.from_square == m1.to_square and m.to_square == m1.from_square)
    state.make_move(m3)
    m4 = next(m for m in legal_moves(state) if m.from_square == m2.to_square and m.to_square == m2.from_square)
    state.make_move(m4)

  shuffle_out_and_back()
  assert result(state) == ONGOING
  shuffle_out_and_back()
  assert result(state) == DRAW

def test_search_style_make_unmake_does_not_pollute_repetition():
  state = GameState.initial()
  before = state.position_history[:]
  for _ in range(30):
    moves = legal_moves(state)
    state.make_move(moves[0])
    state.unmake_move()
  assert state.position_history == before