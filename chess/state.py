from .board import Board

class GameState:
  WHITE, BLACK = 1, -1

  def __init__(self, board:Board=None, side_to_move:bool=WHITE, white_kingside:bool=True, white_queenside:bool=True,
               black_kingside:bool=True, black_queenside:bool=True, en_passant_square:list=None,
               halfmove_clock:int=0, fullmove_number:int=1):
    self.board = board if board is not None else Board()
    self.side_to_move = side_to_move   # 1 for white, -1 for black (white by default)

    self.white_kingside, self.white_queenside = white_kingside, white_queenside
    self.black_kingside, self.black_queenside = black_kingside, black_queenside
    self.en_passant_square = en_passant_square
    self.halfmove_clock, self.fullmove_number = halfmove_clock, fullmove_number

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

  def __repr__(self):
    return f'GameState(side_to_move={self.side_to_move}, castling={self.castling_rights()}, en_passant={self.en_passant_square}, halfmove={self.halfmove_clock}, fullmove={self.fullmove_number})'
 