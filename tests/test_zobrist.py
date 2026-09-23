import random
from ..engine.chess.state import GameState
from ..engine.chess import zobrist
from ..engine.chess.rules import legal_moves

state = GameState.initial()
assert state.hash == zobrist.compute_hash(state)
print('initial hash matches recompute')

for _ in range(500):
  moves = legal_moves(state)
  if not moves:
    state = GameState.initial()
    continue
  move = random.choice(moves)
  hash_before = state.hash
  state.make_move(move)
  assert state.hash == zobrist.compute_hash(state), f'incremental hash diverged after {move}'
  state.unmake_move()
  assert state.hash == hash_before, f'unmake did not restore hash after {move}'
  state.make_move(random.choice(moves))
print('500-move incremental hash test passed')

state2 = GameState.initial()
n1 = next(m for m in legal_moves(state2) if state2.board.state[m.from_row][m.from_col] == 2 and m.to_col == 5)
state2.make_move(n1)
n2 = next(m for m in legal_moves(state2) if state2.board.state[m.from_row][m.from_col] == -2 and m.to_col == 5)
state2.make_move(n2)
n3 = next(m for m in legal_moves(state2) if m.from_square == n1.to_square and m.to_square == n1.from_square)
state2.make_move(n3)
n4 = next(m for m in legal_moves(state2) if m.from_square == n2.to_square and m.to_square == n2.from_square)
state2.make_move(n4)
fresh = GameState.initial()
print('knight-out-and-back reaches same hash as fresh initial position:', state2.hash == fresh.hash, state2.board.state == fresh.board.state)

c = GameState.initial()
d = GameState(white_kingside=False)
print('different castling rights produce different hashes:', c.hash != d.hash)

e = GameState.initial()
f = GameState(side_to_move=-1)
print('different side to move produces different hash:', e.hash != f.hash)

print('all zobrist tests completed')