import random
from engine.environment.chess_environment import ChessEnvironment
from engine.chess import rules
from engine.encoding.position_encoder import encode

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

def test_position_encoding_is_deterministic():
  env = ChessEnvironment()
  encoded_a = encode(env.current_state())
  encoded_b = encode(env.current_state())
  assert (encoded_a == encoded_b).all()