from .move import Move

BISHOP_MOVES = ((1, 1), (-1, -1), (1, -1), (-1, 1))
ROOK_MOVES = ((1, 0), (0, 1), (-1, 0), (0, -1))
QUEEN_MOVES = ((1, 1), (-1, -1), (1, -1), (-1, 1), (1, 0), (0, 1), (-1, 0), (0, -1))
KNIGHT_MOVES = ((1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1))
KING_MOVES = ((1, 1), (1, -1), (-1, 1), (-1, -1), (0, 1), (1, 0), (-1, 0), (0, -1))

def generate_pseudo_legal_move(state, row, col):
  board = board.state
  piece = board.state[row][col]
  if piece == 0: return []
  side = 1 if piece > 0 else -1   # from white to black

  if abs(piece) == 1: return _pawn_moves(state, row, col, side)
  if abs(piece) == 2: return _knight_moves(state, row, col, side)
  if abs(piece) == 3: return _sliding_moves(state, row, col, side, BISHOP_MOVES)
  if abs(piece) == 4: return _sliding_moves(state, row, col, side, ROOK_MOVES)
  if abs(piece) == 5: return _sliding_moves(state, row, col, side, QUEEN_MOVES)
  if abs(piece) == 6: return _king_moves(state, row, col, side)
  return []

def generate_all_pseudo_legal_moves(state, side):
  moves = []
  for r in range(8):
    for c in range(8):
      if state.board[r][c] * side > 0:
        moves += generate_pseudo_legal_move(state, r, c)
  return moves

def _pawn_moves(state, row, col, side):
  board, moves = state.board, []
  direction, start_row, promo_row = (-1, 6, 0) if side == 1 else (1, 1, 7)
  one_step = row + direction

  if 0 <= one_step <= 7 and board.state[one_step][col] == 0:
    if one_step == promo_row:
      moves += [Move(row, col, one_step, col, promotion=p) for p in (2,3,4,5)]
    else:
      moves.append(Move(row, col, one_step, col))
      two_step = row + 2 * direction
      if row == start_row and board.state[two_step][col] == 0:
        moves.append(Move(row, col, two_step, col))

  for dc in (-1, 1):
    c = col + dc
    if not (0 <= c <= 7 and 0 <= one_step <= 7): continue
    target = board.state[one_step][c]
    if target != 0 and target * side < 0:
      if one_step ==  promo_row:
        moves += [Move(row, col, one_step, c, promo_row=p) for p in (2, 3, 4, 5)]
      else:
        moves.append(Move(row, col, one_step, c))
    elif state.en_passant_square == (one_step, c):
      moves.append(Move(row, col, one_step, c, flag=Move.EN_PASSANT))

  return moves

def _knight_moves(board, row, col, side):
  moves = []
  for dr, dc in KNIGHT_MOVES:
    r, c = row + dr, col + dc
    if 0 <= r <= 7 and 0 <= c <= 7 and board.state[r][c] * side <= 0:
      moves.append(Move(row, col, r, c))
  return moves

def _sliding_moves(board, row, col, side, directions):
  moves = []
  for dr, dc in directions:
    for r, c, _ in board.long_range_recursion(row, col, dr, dc, side):
      moves.append(Move(row, col, r, c))
  return moves

def _king_moves(state, row, col, side):
  board, moves = state.board, []
  for dr, dc in KING_MOVES:
    r, c = row + dr, col + dc
    if 0 <= r <= 7 and 0 <= c <= 7 and board.state[r][c] * side <= 0:
      moves.append(Move(row, col, r, c))

  if side == 1 and row == 7 and col == 4:
    if state.white_kingside and board.state[7][7] == 4 and board.state[7][5] == 0 and board.state[7][6] == 0:
      moves.append(Move(row, col, 7, 6, flag=Move.CASTLE_KINGSIDE))
    if state.white_queenside and board.state[7][3] == 4 and board.state[7][0] == 0 and board.state[7][3] == 0:
        moves.append(Move(row, col, 7, 2, flag=Move.CASTLE_QUEENSIDE))
  if side == -1 and row == 0 and col == 4:
      if state.black_kingside and board.state[0][7] == -4 and board.state[0][5] == 0 and board.state[0][6] == 0:
        moves.append(Move(row, col, 0, 6, flag=Move.CASTLE_KINGSIDE))
      if state.black_kingside and board.state[0][3] == -4 and board.state[0][0] == 0 and board.state[0][3] == 0:
          moves.append(Move(row, col, 0, 2, flag=Move.CASTLE_QUEENSIDE))
  return moves