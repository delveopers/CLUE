import random
from engine.environment.chess_environment import ChessEnvironment
from engine.chess import rules
from engine.encoding.position_encoder import encode
from engine.encoding.move_encoder import move_to_index, index_to_move, ACTION_SPACE_SIZE

KIWIPETE_FEN = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1'

def test_reset_gives_initial_position():
  env = ChessEnvironment()
  assert len(env.legal_moves()) == 20
  assert not env.is_terminal()
  assert env.get_result() == rules.ONGOING
  assert env.side_to_move() == 1

def test_make_and_unmake_move_round_trip():
  env = ChessEnvironment()
  move = env.legal_moves()[0]
  env.make_move(move)
  assert env.side_to_move() == -1
  env.unmake_move()
  assert len(env.legal_moves()) == 20
  assert env.side_to_move() == 1

def test_reset_from_fen():
  env = ChessEnvironment()
  env.reset(fen=KIWIPETE_FEN)
  assert len(env.legal_moves()) == 48

def test_random_game_does_not_crash():
  random.seed(3)
  env = ChessEnvironment()
  depth = 0
  while not env.is_terminal() and depth < 80:
    env.make_move(random.choice(env.legal_moves()))
    depth += 1
  assert env.get_result() in (rules.ONGOING, rules.WHITE_WIN, rules.BLACK_WIN, rules.DRAW)

def test_position_encoding_is_deterministic_and_hashable():
  env = ChessEnvironment()
  encoded = encode(env.current_state())
  assert hash(encoded) == hash(encode(env.current_state()))

def test_move_encoder_round_trips_across_random_game():
  random.seed(4)
  env = ChessEnvironment()
  checked = 0
  for _ in range(40):
    moves = env.legal_moves()
    if not moves:
      env.reset()
      continue
    for move in moves:
      index = move_to_index(move)
      assert 0 <= index < ACTION_SPACE_SIZE
      assert index_to_move(index, env.current_state()) == move
      checked += 1
    env.make_move(random.choice(moves))
  assert checked > 0

def test_move_encoder_round_trips_including_castling():
  env = ChessEnvironment()
  env.reset(fen=KIWIPETE_FEN)
  for move in env.legal_moves():
    assert index_to_move(move_to_index(move), env.current_state()) == move

def test_move_encoder_rejects_bogus_index():
  env = ChessEnvironment()
  assert index_to_move(999999, env.current_state()) is None