from collections import namedtuple

PositionEncoding = namedtuple('PositionEncoding', ['pieces', 'side_to_move', 'white_kingside', 'white_queenside', 'black_kingside', 'black_queenside', 'en_passant_square'])

def encode(state):
  pieces = tuple(tuple(row) for row in state.board.state)
  return PositionEncoding(pieces, state.side_to_move, state.white_kingside, state.white_queenside, state.black_kingside, state.black_queenside, state.en_passant_square)
