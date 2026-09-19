import random
from ..chess.state import GameState
from ..chess.board import Board
from ..chess.rules import legal_moves

def snapshot(state):
  return ([r[:] for r in state.board.state], state.side_to_move, state.castling_rights(), state.en_passant_square, state.halfmove_clock, state.fullmove_number)

state = GameState.initial()
moves = legal_moves(state)
print('initial legal move count (expect 20):', len(moves))
assert len(moves) == 20

for _ in range(300):
  before = snapshot(state)
  moves = legal_moves(state)
  if not moves:
    state = GameState.initial()
    continue
  move = random.choice(moves)
  state.make_move(move)
  state.unmake_move()
  after = snapshot(state)
  assert before == after, f'make/unmake mismatch on {move}'
  move = random.choice(moves)
  state.make_move(move)
print('random make/unmake round-trip test passed')

state = GameState.initial()
b = state.board.state
b[7][4], b[7][5], b[7][6], b[7][7] = 6, 0, 0, 4
b[6][4], b[6][5], b[6][6] = 0, 0, 0
moves = legal_moves(state)
castle_moves = [m for m in moves if m.is_castle()]
print('white kingside castle available:', len(castle_moves) == 1)
state.make_move(castle_moves[0])
print('king landed on g1:', state.board.state[7][6] == 6, 'rook landed on f1:', state.board.state[7][5] == 4)
state.unmake_move()
print('unmake restored king e1, rook h1:', state.board.state[7][4] == 6 and state.board.state[7][7] == 4)

state = GameState.initial()
b = state.board.state
for r in range(8):
  for c in range(8): b[r][c] = 0
b[6][4], b[4][3] = 1, -1
b[7][4], b[0][4] = 6, -6
state.side_to_move = 1
ep_moves = legal_moves(state)
double_step = [m for m in ep_moves if m.from_row == 6 and m.to_row == 4]
print('white pawn double step available:', len(double_step) == 1)
state.make_move(double_step[0])
print('en passant square set:', state.en_passant_square == (5, 4))
black_moves = legal_moves(state)
ep_capture = [m for m in black_moves if m.is_en_passant()]
print('black en passant capture available:', len(ep_capture) == 1)
state.make_move(ep_capture[0])
print('white pawn captured:', state.board.state[4][4] == 0, 'black pawn landed on (5,4):', state.board.state[5][4] == -1)
state.unmake_move()
print('unmake restored white pawn:', state.board.state[4][4] == 1)

state = GameState.initial()
b = state.board.state
for r in range(8):
  for c in range(8): b[r][c] = 0
b[1][0], b[7][4], b[0][4] = 1, 6, -6
state.side_to_move = 1
promo_moves = [m for m in legal_moves(state) if m.is_promotion()]
print('promotion move count (expect 4):', len(promo_moves))
queen_promo = [m for m in promo_moves if m.promotion == 5][0]
state.make_move(queen_promo)
print('promoted piece is queen:', state.board.state[0][0] == 5)
state.unmake_move()
print('unmake restored pawn:', state.board.state[1][0] == 1)

state = GameState.initial()
for r in range(8):
  for c in range(8): state.board.state[r][c] = 0
state.board.state[7][4], state.board.state[0][4], state.board.state[7][0] = 6, -6, 4
state.white_kingside, state.white_queenside = False, True
state.side_to_move = -1
capture_rook_moves = [m for m in legal_moves(state) if m.to_row == 7 and m.to_col == 0]
if capture_rook_moves:
  state.make_move(capture_rook_moves[0])
  print('white queenside right revoked after rook captured:', state.white_queenside == False)

print('all v01 step4/5 tests completed')