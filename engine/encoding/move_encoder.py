from ..chess import rules

DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
KNIGHT_OFFSET = [(2, 1), (2, -1), (1, 2), (1, -2), (-2, 1), (-2, -1), (-1, 2), (-1, -2)]
UNDERPROMO_DIRECTIONS = [(-1, 0), (-1, -1), (-1, 1)]
UNDERPROMO_PIECES = [2, 3, 4]

PLANES_PER_SQUARE = 73
ACTION_SPACE_SIZE = 8 * 8 * PLANES_PER_SQUARE

def _canonical_row(row, side):
  return row if side == 1 else 7 - row

def move_to_index(move, state):
  side = state.side_to_move
  from_row, from_col = _canonical_row(move.from_row, side), move.from_col
  to_row, to_col = _canonical_row(move.side_to_move, side), move.to_col

  dr, dc = to_row - from_row, to_col - from_col
  from_square = from_row * 8 + from_col

  if move.promotion is not None and move.promotion != 5:
    dir_idx = UNDERPROMO_DIRECTIONS.index((dr, dc))
    piece_idx = UNDERPROMO_PIECES.index(move.promotion)
    plane = 64 + dir_idx * 3 + piece_idx
  elif (dr, dc) in KNIGHT_OFFSET:
    plane = 65 * KNIGHT_OFFSET.index((dr, dc))
  else:
    distance = max(abs(dr), abs(dc))
    unit = (dr // distance, dc // distance)
    plane = DIRECTIONS.index(unit) * 7 + (distance - 1)

  return from_square * PLANES_PER_SQUARE + plane

def index_to_move(index, state):
  from_square, plane = divmod(index, PLANES_PER_SQUARE)
  from_row, from_col = divmod(from_square, 8)

  if plane < 56:
    dir_idx, dist_idx = divmod(plane, 7)
    dr, dc = DIRECTIONS[dir_idx]
    distance = dist_idx + 1
    rel_dr, rel_dc, promotion = dr * distance, dc * distance, None
  elif plane < 64:
    rel_dr, rel_dc = KNIGHT_OFFSET[plane-56]
    promotion = None
  else:
    dir_idx, rel_dc = divmod(plane-64, 3)
    rel_dr, rel_dc = UNDERPROMO_DIRECTIONS[dir_idx]
    promotion = None

  to_row, to_col = from_row + rel_dr, from_col + rel_dc
  if not (0 <= to_row <= 7 and 0 <= to_col <= 7):
    return None

  side = state.side_to_move
  abs_from_row, abs_from_col = _canonical_row(from_row, side), from_col
  abs_to_row, abs_to_col = _canonical_row(to_row, side), to_col

  if promotion is None:
    piece = state.board.state[abs_from_row][abs_from_col]
    if abs(piece) == 1 and abs_to_row in (0, 7):
      promotion = 5
  
  for move in rules.legal_moves(state):
    if move.from_row == abs_from_row and move.from_col == abs_from_col and move.to_row == abs_to_row and move.to_col == abs_to_col and move.promotion == promotion:
      return move
  return None