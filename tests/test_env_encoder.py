import random
from ..engine.environment.chess_environment import ChessEnvironment
from ..engine.chess import rules
from ..engine.encoding.position_encoder import encode
from ..engine.encoding.move_encoder import move_to_index, index_to_move, ACTION_SPACE_SIZE

env = ChessEnvironment()
print('reset gives 20 legal moves:', len(env.legal_moves()) == 20)
print('not terminal at start:', not env.is_terminal())
print('get_result ongoing at start:', env.get_result() == rules.ONGOING)
print('side_to_move is white at start:', env.side_to_move() == 1)

move = env.legal_moves()[0]
env.make_move(move)
print('side_to_move flips after a move:', env.side_to_move() == -1)
env.unmake_move()
print('unmake_move restores 20 legal moves:', len(env.legal_moves()) == 20)

env.reset(fen='r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1')
print('reset from FEN (kiwipete) legal move count (expect 48):', len(env.legal_moves()))
assert len(env.legal_moves()) == 48

env.reset()
depth = 0
while not env.is_terminal() and depth < 80:
  env.make_move(random.choice(env.legal_moves()))
  depth += 1
print(f'played {depth} random plies without crashing, final result:', env.get_result())

state = env.current_state()
enc = encode(state)
print('encode returns hashable, deterministic structure:', hash(enc) == hash(encode(state)))

env.reset()
total_checked = 0
for _ in range(40):
  moves = env.legal_moves()
  if not moves:
    env.reset()
    continue
  for m in moves:
    idx = move_to_index(m)
    assert 0 <= idx < ACTION_SPACE_SIZE
    decoded = index_to_move(idx, env.current_state())
    assert decoded == m, f'round-trip failed for {m}, decoded as {decoded}'
    total_checked += 1
  env.make_move(random.choice(moves))
print(f'move encoder round-trip verified across {total_checked} legal moves')

env.reset(fen='r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1')
for m in env.legal_moves():
  idx = move_to_index(m)
  decoded = index_to_move(idx, env.current_state())
  assert decoded == m, f'kiwipete round-trip failed for {m}'
print('kiwipete move encoder round-trip passed, including castling/promotion-free tactical position')

print('bad index returns None instead of a fabricated move:', index_to_move(999999, env.current_state()) is None)

print('all environment/encoding tests completed')