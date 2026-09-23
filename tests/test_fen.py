import random
from ..chess.fen import parse_fen, to_fen
from ..chess.state import GameState
from ..chess.rules import legal_moves
from ..chess import zobrist

STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
NO_CASTLING_FEN = '4k3/8/8/8/8/8/8/4K2R w - - 12 30'
EN_PASSANT_FEN = 'rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3'
KIWIPETE_FEN = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1'

for name, target in (('starting', STARTING_FEN), ('no castling', NO_CASTLING_FEN), ('en passant', EN_PASSANT_FEN), ('kiwipete', KIWIPETE_FEN)):
  state = parse_fen(target)
  result = to_fen(state)
  print(f'{name} round-trip:', result == target)
  assert result == target
  assert state.hash == zobrist.compute_hash(state)

state = parse_fen(STARTING_FEN)
fresh = GameState.initial()
print('parsed starting FEN matches GameState.initial() hash:', state.hash == fresh.hash)
print('parsed starting FEN legal move count (expect 20):', len(legal_moves(state)))
assert len(legal_moves(state)) == 20

state = parse_fen(KIWIPETE_FEN)
moves = legal_moves(state)
print('kiwipete legal move count (expect 48):', len(moves))

state = GameState.initial()
for _ in range(200):
  moves = legal_moves(state)
  if not moves:
    state = GameState.initial()
    continue
  state.make_move(random.choice(moves))
  fen = to_fen(state)
  reloaded = parse_fen(fen)
  assert reloaded.hash == state.hash, f'hash mismatch after FEN round-trip at move: {fen}'
  assert reloaded.board.state == state.board.state
  assert to_fen(reloaded) == fen
print('200-move random-game FEN round-trip test passed')

print('all fen tests completed')