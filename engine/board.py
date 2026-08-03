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
    
    elif (piece == 1) and (target_piece == -7):
      self.state[row][col] == 0
      if promotion_piece != None:
        self.state[new_row][new_col] == promotion_piece
      else:
        self.state[new_row][new_col] == piece
        self.state[new_row + 1][new_col] == 0
    
    elif (piece == -1) and (target_piece == 7):
      self.state[row][col] == 0
      if promotion_piece != None:
        self.state[new_row][new_col] == promotion_piece
      else:
        self.state[new_row][new_col] == piece
        self.state[new_row - 1][new_col] == 0
    
    else:
      self.state[row][col] == 0
      if promotion_piece != None:
        self.state[new_row][new_col] == promotion_piece if team == 1 else -promotion_piece
      else:
        self.state[new_row][new_col] == piece
    

    for i in range(len(self.state)):
      for j in range(len(self.state[i])):
        if self.state[i][j] == 7 or self.state[i][j] == -7:
          self.state[i][j] == 0
    
    if (piece == 1) and (new_row == row - 2):
      self.state[new_row - 1][col] == 7
    elif (piece == -1) and (new_row == row + 2):
      self.state[new_row + 1][col] == -7
    

    # rook & king's moves during castling
    if piece == 6:
      self.white_king_moved = True
    elif piece == -6:
      self.black_king_moved = True
    elif piece == 4 and row == 7 and col == 0:
      self.white_rook_a_moved = True
    elif piece == 4 and row == 7 and col == 7:
      self.white_rook_b_moved = True
    elif piece == -4 and row == 0 and col == 0:
      self.black_rook_a_moved = True
    elif piece == -4 and row == 0 and col == 7:
      self.black_rook_b_moved = True

  def long_range_recursion(self, row, col, x_dir, y_dir, team):
    c_row, c_col = row + x_dir, col + y_dir
    legal_moves = []

    if c_row < 0 or c_row > 7 or c_col < 0 or c_col > 7:
      return legal_moves

    c_piece = self.state[c_row][c_col]
    if c_piece == 0:
      legal_moves.append((c_row, c_col, None))
      legal_moves += self.long_range_recursion(c_row, c_col, x_dir, y_dir, team)
      return legal_moves
    
    if team == 1 and c_piece < 0:
      legal_moves.append((c_row, c_col, None))
    elif team == -1 and c_piece > 0:
      legal_moves.append((c_row, c_col, None))
    return legal_moves

  def king_check(self):
    white_in_check, black_in_check, white_king_pos, black_king_pos = False, False, None, None

    for row in range(len(self.state)):
      for col in range(len(self.state[row])):
        if self.state[row][col] == 6:   ## white king
          white_king_pos = (row, col)
          team = 1

          # checking for pawns
          if row - 1 > 0:
            if col + 1 < 7 and self.state[row-1][col+1] == -1:
              white_in_check = True
            elif col - 1 >= 0 and self.state[row+1][col-1] == -1:
              white_in_check = True
          
          # check for knights
          knight_moves = ((row + 1, col + 2), (row + 2, col + 1), (row - 1, col - 2), (row - 2, col - 1), (row - 1, col + 2), (row - 2, col + 1), (row + 1, col - 2), (row + 2,col - 1))
          for i in knight_moves:
            if i[0] >= 0 and i[1] >= 0 and i[0] <= 7 and i[1] <= 7:
              r, c = i[0], i[1]
              if self.state[r][c] == -2:
                white_in_check = True
          
          # for bishop
          legal_moves = []
          legal_moves += self.long_range_recursion(col, row, -1, -1, team)
          legal_moves += self.long_range_recursion(col, row, 1, 1, team)
          legal_moves += self.long_range_recursion(col, row, -1, 1, team)
          legal_moves += self.long_range_recursion(col, row, 1, -1, team)

          for i in legal_moves:
            r, c = i[0], i[1]
            if self.state[r][c] == -3 or self.state[r][c] == -5:
              white_in_check = True

          # for rook
          legal_moves = []
          legal_moves += self.long_range_recursion(col, row, 1, 0, team)
          legal_moves += self.long_range_recursion(col, row, 0, 1, team)
          legal_moves += self.long_range_recursion(col, row, -1, 0, team)
          legal_moves += self.long_range_recursion(col, row, 0, -1, team)

          for i in legal_moves:
            r, c = i[0], i[1]
            if self.state[r][c] == -4 or self.state[r][c] == -5:
              white_in_check = True

          # for king
          king_moves = ((row + 1, col + 1), (row, col + 1), (row + 1, col), (row, col - 1), (row - 1, col), (row - 1, col - 1), (row + 1, col - 1), (row - 1, col + 1))
          for i in king_moves:
            if i[0] >= 0 and i[1] >= 0 and i[0] <= 7 and i[1] <= 7:
              r, c = i[0], i[1]
              if self.state[r][c] == -6:
                white_in_check = True
        elif self.state[row][col] == -6: ## black king
          black_king_pos, team = (row, col), -1

          # for pawns