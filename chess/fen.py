# (Forsyth-Edwards Notation)

from .board import Board
from .state import GameState

PIECE_CHARS = {1:'P', 2:'N', 3:'B', 4:'R', 5:'Q', 6:'K', -1:'p', -2:'n', -3:'b', -4:'r', -5:'q', -6:'k'}
CHAR_PIECES = {v: k for k, v in PIECE_CHARS.items()}

def square_to_algebraic(row, col):
  return f"{chr(ord('a') + col)}{8 - row}"

def algebraic_to_square(square):
  return (8 - int(square[1]), ord(square[0]) - ord('a'))

def parse_fen(fen):
  placement, side, castling, en_passant, halfmove, fullmove = fen.strip().split()

  board = Board()
  board.state = [[0] * 8 for _ in range(8)]
  for row, rank in enumerate(placement.split('/')):
    col = 0
    for ch in rank:
      if ch.isdigit():
        col += int(ch)
      else:
        board.state[row][col] = CHAR_PIECES[ch]
        col += 1

  side_to_move = 1 if side == 'w' else -1
  white_kingside, white_queenside = 'K' in castling, 'Q' in castling
  black_kingside, black_queenside = 'k' in castling, 'q' in castling
  en_passant_square = None if en_passant == '-' else algebraic_to_square(en_passant)

  return GameState(board, side_to_move, white_kingside, white_queenside, black_kingside, black_queenside, en_passant_square, int(halfmove), int(fullmove))

def to_fen(state):
  rows = []
  for row in state.board.state:
    rank, empty = '', 0
    for piece in row:
      if piece == 0:
        empty += 1
        continue
      if empty:
        rank += str(empty)
        empty = 0
      rank += PIECE_CHARS[piece]
    if empty:
      rank += str(empty)
    rows.append(rank)

  side = 'w' if state.side_to_move == 1 else 'b'
  castling = ''.join(flag for flag, present in (('K', state.white_kingside), ('Q', state.white_queenside), ('k', state.black_kingside), ('q', state.black_queenside)) if present) or '-'
  en_passant = '-' if state.en_passant_square is None else square_to_algebraic(*state.en_passant_square)
  return f"{'/'.join(rows)} {side} {castling} {en_passant} {state.halfmove_clock} {state.fullmove_number}"