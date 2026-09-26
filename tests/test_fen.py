import random
import pytest
from ..engine.chess.fen import parse_fen, to_fen
from ..engine.chess.state import GameState
from ..engine.chess.rules import legal_moves
from ..engine.chess import zobrist

STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
NO_CASTLING_FEN = '4k3/8/8/8/8/8/8/4K2R w - - 12 30'
EN_PASSANT_FEN = 'rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3'
KIWIPETE_FEN = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1'

@pytest.mark.parametrize('fen', [STARTING_FEN, NO_CASTLING_FEN, EN_PASSANT_FEN, KIWIPETE_FEN])
def test_round_trip(fen):
  assert to_fen(parse_fen(fen)) == fen

def test_parsed_starting_fen_matches_initial_gamestate_hash():
  assert parse_fen(STARTING_FEN).hash == GameState.initial().hash

def test_parsed_starting_fen_has_twenty_legal_moves():
  assert len(legal_moves(parse_fen(STARTING_FEN))) == 20

def test_kiwipete_legal_move_count():
  assert len(legal_moves(parse_fen(KIWIPETE_FEN))) == 48

def test_random_game_fen_round_trip_stays_consistent():
  random.seed(2)
  state = GameState.initial()
  for _ in range(200):
    moves = legal_moves(state)
    if not moves:
      state = GameState.initial()
      continue
    state.make_move(random.choice(moves))
    fen = to_fen(state)
    reloaded = parse_fen(fen)
    assert reloaded.hash == state.hash
    assert reloaded.board.state == state.board.state
    assert to_fen(reloaded) == fen