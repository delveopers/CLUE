from ..chess.state import GameState
from ..chess.fen import parse_fen
from ..chess import rules

class ChessEnvironment:
  def __init__(self, state=None):
    self.state = state if state is not None else GameState.initial()

  def reset(self, fen=None):
    self.state = parse_fen(fen) if fen is not None else GameState.initial()
    return self.state

  def legal_moves(self):
    return rules.legal_moves(self.state)

  def legal_moves_for_square(self, row, col):
    return rules.legal_moves_for_square(self.state, row, col)

  def make_move(self, move):
    self.state.make_move(move)

  def unmake_move(self):
    self.state.unmake_move()

  def side_to_move(self):
    return self.state.side_to_move

  def is_terminal(self):
    return rules.is_terminal(self.state)

  def get_result(self):
    return rules.result(self.state)

  def current_state(self):
    return self.state