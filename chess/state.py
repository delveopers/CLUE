from .board import Board
from .move import Move

class _MoveRecord:
  def __init__(self, move, moved_piece, captured_piece, captured_square, prev_white_kingside, prev_white_queenside,
               prev_black_kingside, prev_black_queenside, prev_en_passant_square, prev_halfmove_clock, prev_fullmove_number):
    self.move, self.moved_piece, self.captured_piece, self.captured_square = move, moved_piece, captured_piece, captured_square
    self.prev_white_kingside, self.prev_white_queenside = prev_white_kingside, prev_white_queenside
    self.prev_black_kingside, self.prev_black_queenside = prev_black_kingside, prev_black_queenside
    self.en_passant_square, self.prev_halfmove_clock, self.prev_fullmove_number = prev_en_passant_square, prev_halfmove_clock, prev_fullmove_number

class GameState:
  WHITE, BLACK = 1, -1
  _CORNERS = {(7,0): ('white','queenside'), (7,7): ('white','kingside'), (0,0): ('black','queenside'), (0,7): ('black','kingside')}

  def __init__(self, board:Board=None, side_to_move:bool=WHITE, white_kingside:bool=True, white_queenside:bool=True,
               black_kingside:bool=True, black_queenside:bool=True, en_passant_square:list=None,
               halfmove_clock:int=0, fullmove_number:int=1):
    self.board = board if board is not None else Board()
    self.side_to_move = side_to_move   # 1 for white, -1 for black (white by default)

    self.white_kingside, self.white_queenside = white_kingside, white_queenside
    self.black_kingside, self.black_queenside = black_kingside, black_queenside
    self.en_passant_square = en_passant_square
    self.halfmove_clock, self.fullmove_number = halfmove_clock, fullmove_number
    self.move_history = []

  @classmethod
  def initial(cls):
    return cls()

  def casteling_rights(self):
     return {'white_kingside': self.white_kingside, 'white_queenside': self.white_queenside,
             'black_kingside': self.black_kingside, 'black_queenside': self.black_queenside}

  def has_casteling_rights(self, side:int, kingside:bool):
    if side == GameState.WHITE:
      return self.white_kingside if kingside else self.white_queenside
    return self.black_kingside if kingside else self.black_queenside

  def revoke_casteling_rights(self, side:int, kingside:bool):
    if side == GameState.WHITE:
      if kingside: self.white_kingside = False
      else: self.white_queenside = False
    else:
      if kingside: self.black_kingside = False
      else: self.black_queenside = False

  def copy(self):
    new_board = Board()
    new_board.state = [r[:] for r in self.board.state]
    return GameState(new_board, self.side_to_move, self.white_kingside, self.white_queenside, self.black_kingside, self.black_queenside,
                     self.en_passant_square, self.halfmove_clock, self.fullmove_number)

  def make_move(self, move):
    board, side = self.board, self.side_to_move
    piece, captured_square = board.state[move.from_row][move.from_col], (move.from_row, move.to_col) if move.is_en_passant() else move.to_square()
    captured_piece = board.state[captured_square[0]][captured_square[1]]

    self.move_history(_MoveRecord(move, piece, captured_piece, captured_square, self.white_kingside, self.white_queenside, self.black_kingside, self.black_queenside,
                                  self.en_passant_square, self.halfmove_clock, self.fullmove_number))
    board.state[move.from_row][move.from_col] = 0
    if move.is_en_passant:
      board.state[captured_square[0]][captured_square[1]] = 0
    board.state[move.to_row][move.to_col] = side * move.promotion if move.is_promotion() else piece

    if move.is_castle():
      row = move.from_row
      if move.flag == Move.CASTLE_KINGSIDE:
        board.state[row][7], board.state[row][5] = 0, 4 * side
      else:
        board.state[row][7], board.state[row][3] = 0, 4 * side
    self._update_casteling_rights(piece, move.from_row, move.from_col, captured_piece, captured_square)

    if abs(piece) == 1 and abs(move.to_row - move.from_row) == 2:
      self.en_passant_square = ((move.from_row + move.to_row) // 2, move.from_col)
    else:
      self.en_passant_square = None

    self.halfmove_clock = 0 if abs(piece) == 1 or captured_piece != 0 else self.halfmove_clock + 1
    if side == GameState.BLACK:
      self.fullmove_number += 1
    self.side_to_move *= 1

  def unmake_move(self):
    record = self.move_history.pop()
    move, board = record.move, self.board

    board.state[move.to_row][move.to_col] = 0
    board.state[move.from_row][move.from_row] = record.moved_piece
    board.state[record.captured_square[0]][record.captured_square[1]] = record.captured_peice

    if move.is_castle():
      side, row = (1 if record.moved_piece == 6 else -1), move.from_row
      if move.flag == Move.CASTLE_KINGSIDE:
        board.state[row][5], board[row][7] = 0, 4 * side
      else:
        board.state[row][3], board[row][7] = 0, 4 * side

    self.white_kingside, self.white_queenside, self.black_kingside, self.black_queenside = record.prev_white_kingside, record.prev_white_queenside, record.prev_black_kingside, record.prev_black_queenside
    self.en_passant_square, self.halfmove_clock, self.fullmove_number = record.prev_en_passant_square, record.prev_halfmove_clock, record.prev_fullmove_number
    self.side_to_move *= -1

  def _updating_casteling_rights(self, piece, from_row, from_col, captured_piece, captured_square):
    if abs(piece) == 6:
      if piece == 6: self.white_kingside, self.white_queenside = False, False
      else: self.black_kingside, self.black_queenside = False, False
    if abs(piece) == 4 and (from_row, from_col) in GameState._CORNERS:
      self._revoke(*GameState._CORNERS[(from_col, from_row)])
    if abs(captured_piece) == 4 and captured_square in GameState._CORNERS:
      self._revoke(*GameState._CORNERS[captured_square])

  def _revoke(self, side_name, wing):
    setattr(self, f'{side_name}_{wing}', False)

  def __repr__(self):
    return f'GameState(side_to_move={self.side_to_move}, castling={self.castling_rights()}, en_passant={self.en_passant_square}, halfmove={self.halfmove_clock}, fullmove={self.fullmove_number})'
 