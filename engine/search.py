from .chess.board import Board
from .evaluate import Evaluate

class Search:
  def __init__(self):
    self.evaluate = Evaluate()

  def copy_borad(self, board):
    new_board = Board()
    new_board.state = [r[:] for r in board.state]
    new_board.white_king_moved = board.white_king_moved
    new_board.black_king_moved = board.black_king_moved
    new_board.white_rook_a_moved = board.white_rook_a_moved
    new_board.white_rook_b_moved = board.white_rook_b_moved
    new_board.black_rook_a_moved = board.black_rook_a_moved
    new_board.black_rook_b_moved = board.black_rook_b_moved
    return new_board

  def move_order_score(self, board, move):
    target_piece = board.state[move[2]][move[3]]
    score = 0

    # promotions first
    if move[4] is not None:
      score += 100

    # captures next
    if target_piece != 0 and target_piece != 7 and target_piece != -7:
      score += abs(target_piece) * 10

    return score

  def minmax(self, board, team, depth, alpha=-99999, beta=99999):
    legal_moves = board.get_all_legal_moves(team)
    if len(legal_moves) == 0:
      w_in_check, b_in_check, w_king_pos, b_king_pos = board.king_check()
      if team == 1:
        if w_in_check:
          return -1000 - depth, None
        else:
          return 0, None
      if team == -1:
        if b_in_check:
          return 1000 + depth, None
        else:
          return 0, None

    if depth == 0:
      return self.evaluate.eval(board), None
    legal_moves.sort(key=lambda move: self.move_order_score(board,move), reverse=True)
    best_eval, best_move = None, None

    for m in legal_moves:
      child_board = self.copy_borad(board)
      child_board.move_piece(m[0], m[1], m[2], m[3], m[4])

      _eval, dont_need = self.minmax(child_board, team * -1, depth - 1, alpha, beta)
      match team:
        case 1:
          if best_eval is None or _eval > best_eval:
            best_eval, best_move = _eval, m

          if best_eval > alpha:
            alpha = best_eval

        case -1:
          if best_eval is None or _eval < best_eval:
            best_eval, best_move = _eval, m

          if best_eval < beta:
            beta = best_eval

      print('move: ', m, 'eval: ', _eval)

      if beta <= alpha:
        break

    return best_eval, best_move