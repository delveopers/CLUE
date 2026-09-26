import numpy as np

NUM_PLANES = 18
PIECE_PLANE = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, -1: 6, -2: 7, -3: 8, -4: 9, -5: 10, -6: 11}

def encode(state):
  planes = np.zeros((NUM_PLANES, 8, 8), dtype=np.float32)
  board = state.board.state

  for r in range(8):
    for c in range(8):
      piece = board[r][c]
      if piece != 0:
        planes[PIECE_PLANE[piece], r, c] = 1.0

  if state.side_to_move == 1:
    planes[12, :, :] = 1.0

  if state.white_kingside: planes[13, :, :] = 1.0
  if state.white_queenside: planes[14, :, :] = 1.0
  if state.black_kingside: planes[15, :, :] = 1.0
  if state.black_queenside: planes[16, :, :] = 1.0

  if state.en_passant_square is not None:
    r, c = state.en_passant_square
    planes[17, r, c] = 1.0

  return planes