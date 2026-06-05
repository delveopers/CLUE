# pieces

# 0 - empty
# 1 - pawn
# 2 - knight
# 3 - bishop
# 4 - rook
# 5 - queen
# 6 - king

# +ve - white
# -ve - black

class Board:
  def __init__(self):
    self.state = [[-4, -2, -3, -5, -6, -3, -2, -4],
                  [-1, -1, -1, -1, -1, -1, -1, -1],
                  [ 0,  0,  0,  0,  0,  0,  0,  0],
                  [ 0,  0,  0,  0,  0,  0,  0,  0],
                  [ 0,  0,  0,  0,  0,  0,  0,  0],
                  [ 0,  0,  0,  0,  0,  0,  0,  0],
                  [ 1,  1,  1,  1,  1,  1,  1,  1],
                  [ 4,  2,  3,  5,  6,  3,  2,  4]]

    self.white_king_moved = False
    self.black_king_moved = False
    self.white_rook_a_moved = False
    self.white_rook_b_moved = False
    self.black_rook_a_moved = False
    self.black_rook_b_moved = False
  
  def move_piece(self, row, col, new_row, new_col, promotion_piece=False):
    piece = self.state[row][col]
    team = 1 if self.state[row][col] > 0 else -1
    target_piece = self.state[new_row][new_col]

    if (piece == 6) and (row == 7 and col == 4) and (new_row == 7 and new_col == 6) and self.state[7][7] == 4:    ## white kingside castling
      self.state[row][col] == 0
      self.state[new_row][new_col] == piece
      self.state[7][5] = 4
      self.state[7][7] = 0
    
    elif (piece == 6) and (row == 7 and col == 4) and (new_row == 7 and new_col == 2) and self.state[0][7] == 4:    ## white queenside castling
      self.state[row][col] == 0
      self.state[new_row][new_col] == piece
      self.state[7][3] == 4
      self.state[7][0] == 0
    
    elif (piece == -6) and (row == 0 and col == 4) and (new_row == 0 and new_col == 6) and self.state[0][7] == -4:    ## black kingside castling
      self.state[row][col] == 0
      self.state[new_row][new_col] == piece
      self.state[0][5] == -4
      self.state[0][7] == 0
    
    elif (piece == -6) and (row == 0 and col == 4) and (new_row == 0 and new_col == 2) and self.state[0][0] == -4:      ## black queenside castling
      self.state[row][col] == 0
      self.state[new_row][new_col] == piece
      self.state[0][3] == -4
      self.state[0][0] == 0