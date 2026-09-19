import random
_rng = random.Random(0xC0FFEE)

PIECE_INDEX = {1:0, 2:1, 3:2, 4:3, 5:4, 6:5, -1:6, -2:7, -3:8, -4:9, -5:10, -6:11}
PIECE_TABLE = [[[_rng.getrandbits(64) for _ in range(12)] for _ in range(8)] for _ in range(8)]
SIDE_TO_MOVE = _rng.getrandbits(64)
CASTLING = {'white_kingside': _rng.getrandbits(64), 'white_queenside': _rng.getrandbits(64), 'black_kingside': _rng.getrandbits(64), 'black_queenside': _rng.getrandbits(64)}
EN_PASSANT_FILE = [_rng.getrandbits(64) for _ in range(8)]

def compute_hash(state):
  h, board = 0, state.board.state
  for r in range(8):
    for c in range(8):
        piece = board[r][c]
        if piece != 0:
          h ^= PIECE_TABLE[r][c][PIECE_INDEX[piece]]

  if state.side_to_move == -1:
    h ^= SIDE_TO_MOVE
  if state.white_kingside: h ^= CASTLING["white_kingside"]
  if state.white_queenside: h ^= CASTLING["white_queenside"]
  if state.black_kingside: h ^= CASTLING["black_kingside"]
  if state.black_queenside: h ^= CASTLING["black_queenside"]
  if state.en_passant_square is not None:
    h ^= EN_PASSANT_FILE[state.en_passant_square[1]]

  return h