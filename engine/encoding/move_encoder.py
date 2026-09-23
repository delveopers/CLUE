from ..chess import rules

ACTION_SPACE_SIZE = 64 * 64 * 5

def move_to_index(move):
  from_sq, to_sq = move.from_row * 8 + move.from_col, move.to_row * 8 + move.to_col
  promo_code = 0 if move.promotion is None else move.promotion - 1
  return (from_sq * 64 + to_sq) * 5 + promo_code

def index_to_move(index, state):
  promo_code, rest = index % 5, index // 5
  to_sq, from_sq = rest % 64, rest // 64
  from_row, from_col = divmod(from_sq, 8)
  to_row, to_col = divmod(to_sq, 8)
  promotion = None if promo_code == 0 else promo_code + 1

  for move in rules.legal_moves(state):
    if move.from_row == from_row and move.from_col == from_col and move.to_row == to_row and move.to_col == to_col and move.promotion == promotion:
      return move
  return None