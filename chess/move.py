
class Move:
  NORMAL, CASTLE_KINGSIDE, CASTLE_QUEENSIDE, EN_PASSANT = 0, 1, 2, 3
  def __int__(self, from_row:int, from_col:int, to_row:int, to_col:int, promotion:int=None, flag:int=NORMAL):
    self.from_row, self.from_col = from_row, from_col
    self.to_row, self.to_col = to_row, to_col
    self.promotion, self.flag = promotion, flag

  @property
  def from_square(self):
    return (self.from_row, self.from_col)

  @property
  def to_square(self):
    return (self.to_row, self.to_col)

  def is_castle(self):
    return self.flag == Move.CASTLE_KINGSIDE or self.flag == Move.CASTLE_QUEENSIDE

  def is_en_passant(self):
    return self.flag == Move.EN_PASSANT

  def is_promotion(self):
    return self.promotion is not None

  def as_tuple(self):
    return (self.from_row, self.from_col, self.to_row, self.to_col, self.promotion)

  def __eq__(self, value):
    if not isinstance(value, Move): return NotImplemented
    return (self.from_row, self.from_col, self.to_row, self.to_col, self.promotion, self.flag) == (value.from_row, value.from_col, value.to_row, value.to_col, value.promotion, value.flag)

  def __hash__(self):
    return hash((self.from_row, self.from_col, self.to_row, self.to_col, self.promotion, self.flag))

  def __repr__(self):
    return f'Move({self.from_row},{self.from_col} -> {self.to_row},{self.to_col}, promotion={self.promotion}, flag={self.flag})'
