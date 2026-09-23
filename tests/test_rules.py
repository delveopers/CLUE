from ..chess.state import GameState
from ..chess.rules import legal_moves, result, is_terminal, ONGOING, WHITE_WIN, BLACK_WIN, DRAW

state = GameState.initial()
print('initial position result (expect ongoing):', result(state))
assert result(state) == ONGOING
assert not is_terminal(state)

state = GameState.initial()
for r in range(8):
  for c in range(8): state.board.state[r][c] = 0
state.board.state[0][0], state.board.state[0][7] = 4, -6
state.board.state[1][5], state.board.state[1][6], state.board.state[1][7] = -1, -1, -1
state.board.state[7][4] = 6
state.side_to_move = -1
print('back-rank checkmate legal move count (expect 0):', len(legal_moves(state)))
print('back-rank checkmate result (expect white_win):', result(state))
assert result(state) == WHITE_WIN
assert is_terminal(state)

state = GameState.initial()
for r in range(8):
  for c in range(8): state.board.state[r][c] = 0
state.board.state[0][0] = -6
state.board.state[2][1] = 5
state.board.state[7][7] = 6
state.side_to_move = -1
print('stalemate legal move count (expect 0):', len(legal_moves(state)))
w_in_check, b_in_check, _, _ = state.board.king_check()
print('stalemate: black in check (expect False):', b_in_check)
print('stalemate result (expect draw):', result(state))
assert result(state) == DRAW
assert is_terminal(state)

state = GameState.initial()
for r in range(8):
  for c in range(8): state.board.state[r][c] = 0
state.board.state[7][4], state.board.state[0][4] = 6, -6
state.board.state[6][0] = 1
state.side_to_move = 1
state.halfmove_clock = 100
print('50-move rule result (expect draw):', result(state))
assert result(state) == DRAW

state = GameState.initial()
def knight_shuffle():
  moves = legal_moves(state)
  m1 = next(m for m in moves if state.board.state[m.from_row][m.from_col] == 2 and m.to_col == 5)
  state.make_move(m1)
  moves = legal_moves(state)
  m2 = next(m for m in moves if state.board.state[m.from_row][m.from_col] == -2 and m.to_col == 5)
  state.make_move(m2)
  moves = legal_moves(state)
  m3 = next(m for m in moves if m.from_square == m1.to_square and m.to_square == m1.from_square)
  state.make_move(m3)
  moves = legal_moves(state)
  m4 = next(m for m in moves if m.from_square == m2.to_square and m.to_square == m2.from_square)
  state.make_move(m4)

print('repetition count before shuffles (expect 1):', state.position_history.count(state.hash))
knight_shuffle()
print('repetition result after 1st return to start (expect ongoing):', result(state))
assert result(state) == ONGOING
knight_shuffle()
print('repetition result after 2nd return to start (expect draw):', result(state))
assert result(state) == DRAW

state = GameState.initial()
before_history = state.position_history[:]
moves = legal_moves(state)
for _ in range(50):
  m = moves[0]
  state.make_move(m)
  state.unmake_move()
  moves = legal_moves(state)
print('position_history unaffected by search-style make/unmake (expect True):', state.position_history == before_history)
assert state.position_history == before_history

print('all termination tests completed')