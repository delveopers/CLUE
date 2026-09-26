from ..evaluate import Evaluate
import logging

logger = logging.getLogger(__name__)

class Search:
  def __init__(self):
    self.evaluate = Evaluate()

  def move_order_score(self, board, move):
    score = 0
    if move.is_promotion():
      score += 100
    if move.is_en_passant():
      score += 10
    else:
      target_piece = board.state[move.to_row][move.to_col]
      if target_piece != 0:
        score += abs(target_piece) * 10
    return score

  def minmax(self, env, team, depth, alpha=-99999, beta=99999):
    legal_moves = env.legal_moves()
    state = env.current_state()

    if len(legal_moves) == 0:
      w_in_check, b_in_check, _, _ = state.board.king_check()
      in_check = w_in_check if team == 1 else b_in_check
      if in_check:
        return (-1000 - depth if team == 1 else 1000 + depth), None
      return 0, None

    if state.halfmove_clock >= 100 or state.position_history.count(state.hash) >= 3:
      return 0, None
    if depth == 0:
      return self.evaluate.eval(env.state.board), None

    legal_moves.sort(key=lambda move: self.move_order_score(env.state.board, move),  reverse=True)
    best_eval, best_move = None, None

    for move in legal_moves:
      env.make_move(move)
      _eval, _ = self.minmax(env, team * -1, depth - 1, alpha, beta)
      env.unmake_move()
      match team:
        case 1:
          if best_eval is None or _eval > best_eval:
            best_eval, best_move = _eval, move
          if best_eval > alpha:
            alpha = best_eval
        case -1:
          if best_eval is None or _eval < best_eval:
            best_eval, best_move = _eval, move
          if best_eval < beta:
            beta = best_eval

      logger.debug('move: %s eval: %s', move, _eval)

      if beta <= alpha:
        break
    return best_eval, best_move