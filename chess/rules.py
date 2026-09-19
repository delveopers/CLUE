from .move import Move
from .move_generator import generate_pseudo_legal_move, generate_all_pseudo_legal_moves

def legal_moves(state):
  return filter_legal_moves(state, generate_all_pseudo_legal_moves(state, state.side_to_move))

def legal_moves_for_square(state, row, col):
  return filter_legal_moves(state, generate_pseudo_legal_move(state, row, col))

def filter_legal_moves(state, moves):
  side, legal = state.side_to_move, []
  for move in moves:
    if move.is_castle() and not _castle_path_is_safe(state, move, side):
      continue

    state.make_move(move)
    w_in_check, b_in_check, _, _ = state.king_check()
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
    w_in_check, b_in_check, _, _ = state.king_check()
    board.state[row][test_col], board.state[row][king_col] = saved, original

    in_check = w_in_check if side == 1 else b_in_check
    if in_check:
      return False

  return True