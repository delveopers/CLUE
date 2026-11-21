import numpy as np

NUM_PLANES = 18
PIECE_TYPE_INDEX = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}

def _canonical_row(row, side_to_move):
  return row if side_to_move == 1 else 7 - row

def encode(state):
  side = state.side_to_move
  planes = np.zeros((NUM_PLANES, 8, 8), dtype=np.float32)
  board = state.board.state

  for r in range(8):
    for c in range(8):
      piece = board[r][c]
      if piece == 0: continue
      piece_side = 1 if piece > 0 else -1
      plane_offset = 0 if piece_side == side else 6
      plane = plane_offset + PIECE_TYPE_INDEX[abs(piece)]
      planes[plane, _canonical_row(r, side), c] = 1.0

  planes[12, :, :] = 1.0

  if side == 1:
    my_kingside, my_queenside, opp_kingside, opp_queenside = state.white_kingside, state.white_queenside, state.black_kingside, state.black_queenside
  else:
    my_kingside, my_queenside, opp_kingside, opp_queenside = state.black_kingside, state.black_queenside, state.white_kingside, state.white_queenside

  if my_kingside: planes[13, :, :] = 1.0
  if my_queenside: planes[14, :, :] = 1.0
  if opp_kingside: planes[15, :, :] = 1.0
  if opp_queenside: planes[16, :, :] = 1.0

  if state.en_passant_square is not None:
    r, c = state.en_passant_square
    planes[17, _canonical_row(r, side), c] = 1.0

  return planes