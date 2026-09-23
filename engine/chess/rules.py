"""
* Ongoing — the starting position correctly reports ongoing

* Checkmate — a back-rank mate (rook on a8, black king boxed in by its own pawns) correctly reports white_win

* Stalemate — black king with no legal moves and not in check correctly reports draw, distinct from checkmate

* 50-move rule — halfmove_clock >= 100 reports draw even with plenty of legal moves available

* Threefold repetition — the same position via a knight shuffle counts as 1 occurrence initially, ongoing after the second occurrence,
  and draw only once it recurs a third time

* Search doesn't pollute repetition tracking — 50 rounds of make_move immediately followed by unmake_move (the pattern
  search/legality-filtering already uses) leave position_history byte-for-byte unchanged, confirming that hypothetical exploration won't
  falsely trigger a repetition draw in the real game

"""

from .move import Move
from .move_generator import generate_pseudo_legal_moves, generate_all_pseudo_legal_moves

ONGOING, WHITE_WIN, BLACK_WIN, DRAW = 'ongoing', 'white_win', 'black_win', 'draw'

def result(state):
  moves = legal_moves(state)
  if not moves:
    w_in_check, b_in_check, _, _ = state.board.king_check()
    if state.side_to_move == 1:
      return BLACK_WIN if w_in_check else DRAW
    else:
      return WHITE_WIN if b_in_check else DRAW

  if state.halfmove_clock >= 100:
    return DRAW

  if state.position_history.count(state.hash) >= 3:
    return DRAW

  return ONGOING

def is_terminal(state):
  return result(state) != ONGOING

def legal_moves(state):
  return filter_legal_moves(state, generate_all_pseudo_legal_moves(state, state.side_to_move))

def legal_moves_for_square(state, row, col):
  return filter_legal_moves(state, generate_pseudo_legal_moves(state, row, col))

def filter_legal_moves(state, moves):
  side, legal = state.side_to_move, []
  for move in moves:
    if move.is_castle() and not _castle_path_is_safe(state, move, side):
      continue

    state.make_move(move)
    w_in_check, b_in_check, _, _ = state.board.king_check()
    left_king_in_check = w_in_check if side == 1 else b_in_check
    state.unmake_move()

    if not left_king_in_check:
      legal.append(move)

  return legal

def _castle_path_is_safe(state, move, side):
  board = state.board
  row, king_col = move.from_row, move.from_col
  path_col = (king_col + move.to_col) // 2

  for test_col in (king_col, path_col):
    original, saved = board.state[row][king_col], board.state[row][test_col]
    board.state[row][king_col], board.state[row][test_col] = 0, original
    w_in_check, b_in_check, _, _ = state.board.king_check()
    board.state[row][test_col], board.state[row][king_col] = saved, original

    in_check = w_in_check if side == 1 else b_in_check
    if in_check:
      return False

  return True