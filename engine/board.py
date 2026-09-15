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
          if row +1 <= 7:
            if col + 1 <= 7 and self.state[row+1][col+1] == 1:
              black_in_check = True
            if col - 1 >= 0 and self.state[row+1][col-1] == 1:
              black_in_check = True
          
          knight_moves = ((row + 2, col + 1), (row - 2, col + 1), (row + 2, col - 1), (row - 2, col - 1), (row + 1, col - 2), (row - 1, col - 2), (row - 1, col + 2), (row + 1, col + 2))
          for i in knight_moves:
            if i[0] >= 0 and i[1] >= 1 and i[0] <= 7 and i[1] <= 7:
              r, c = i[0], i[1]
              if self.state[r][c] == 2:
                black_in_check == True
          

          # for bishops / queen (diagonal)
          legal_moves = []
          legal_moves += self.long_range_recursion(row, col, -1, -1, team)
          legal_moves += self.long_range_recursion(row, col, 1, -1, team)
          legal_moves += self.long_range_recursion(row, col, -1, 1, team)
          legal_moves += self.long_range_recursion(row, col, 1, 1, team)

          for i in legal_moves:
            r, c = i[0], i[1]
            if self.state[r][c] == 3 or self.state[r][c] == 5:
              black_in_check = True

          # for rook / queen (straights)
          legal_moves = []
          legal_moves += self.long_range_recursion(row, col, 1, 0, team)
          legal_moves += self.long_range_recursion(row, col, -1, 0, team)
          legal_moves += self.long_range_recursion(row, col, 0, 1, team)
          legal_moves += self.long_range_recursion(row, col, 0, -1, team)

          for i in legal_moves:
            r, c = i[0], i[1]
            if self.state[r][c] == 4 or self.state[r][c] == 5:
              black_in_check = True

          king_moves = ((row + 1, col - 1), (row - 1, col + 1), (row + 1, col + 1), (row - 1, col - 1), (row, col + 1), (row + 1, col), (row - 1, col), (row, col - 1))
          for i in king_moves:
            if i[0] >= 0 and i[1] >= 0 and i[0] <= 7 and i[1] <= 7:
              r, c = i[0], i[1]
              if self.state[r][c] == 6:
                black_in_check = True
    if not white_in_check:
      white_king_pos = None
    if not black_in_check:
      black_king_pos = None

  def get_legal_moves(self, row, col):
    piece = self.state[row][col]
    legal_moves = []
    team = 1 if self.state[row][col] > 0 else -1

    if piece == 1:    # white pawn
      pawn_moves = []   # row, col, piece
      legal_row = row - 1   # moving forward, row decreases
      if legal_row == 0:
        pawn_moves.append((legal_row, col, 2))
        pawn_moves.append((legal_row, col, 3))
        pawn_moves.append((legal_row, col, 4))
        pawn_moves.append((legal_row, col, 5))
      else:
        pawn_moves.append((legal_row, col, None))

      pawn_captures = []
      if legal_row == 0:
        pawn_captures.append((legal_row, col-1, 2))
        pawn_captures.append((legal_row, col-1, 3))
        pawn_captures.append((legal_row, col-1, 4))
        pawn_captures.append((legal_row, col-1, 5))
        pawn_captures.append((legal_row, col+1, 2))
        pawn_captures.append((legal_row, col+1, 3))
        pawn_captures.append((legal_row, col+1, 4))
        pawn_captures.append((legal_row, col+1, 5))
      else:
        pawn_captures.append((legal_row, col-1, None))
        pawn_captures.append((legal_row, col+1, None))

      if row == 6:  # if on starting square, allow two
        legal_row_2 = row - 2   # moving forward, two rows at a time
        pawn_moves.append((legal_row_2, col, None))

      for i in pawn_moves:
        if i[0] >= 0 and i[1] >= 0 and i[1] <= 7 and i[1] <= 7:
          if self.state[i[0]][i[1]] == 0:
            legal_moves.append((i))

      for i in pawn_captures:
        if i[0] >= 0 and i[1] >= 0 and i[1] <= 0 and i[1] <= 7:
          if self.state[i[0]][i[1]] < 0:
            legal_moves.append((i))

    if piece == -1: # black pawn logic
      pawn_moves = []
      legal_row = row + 1

      if legal_row == 7:
        pawn_moves.append((legal_row, col, 2))
        pawn_moves.append((legal_row, col, 3))
        pawn_moves.append((legal_row, col, 4))
        pawn_moves.append((legal_row, col, 5))
      else:
        pawn_moves.append((legal_row, col, None))

      pawn_captures = []

      if legal_row == 7:
        pawn_captures.append((legal_row, col-1, 2))
        pawn_captures.append((legal_row, col-1, 3))
        pawn_captures.append((legal_row, col-1, 4))
        pawn_captures.append((legal_row, col-1, 5))
        pawn_captures.append((legal_row, col+1, 2))
        pawn_captures.append((legal_row, col+1, 3))
        pawn_captures.append((legal_row, col+1, 4))
        pawn_captures.append((legal_row, col+1, 5))
      else:
        pawn_captures.append((legal_row, col-1, None))
        pawn_captures.append((legal_row, col+1, None))

      for i in pawn_moves:
        if i[0] >= 0 and i[1] >=0 and i[0] <= 7 and i[1] <= 7:
          if self.state[i[0]][i[1]] == 0:
            legal_moves.append((i))

      for i in pawn_captures:
        if i[0] >= 0 and i[1] >= 0 and i[0] <= 7 and i[1] <= 7:
          if self.state[i[0]][i[1]] > 0:
            legal_moves.append((i))

    if piece == 2 or piece == -2: # knight logic
      knight_moves = ((row+2, col+1), (row-2, col+1), (row+1, col+2), (row-1, col+2), (row+2, col-1), (row-2, col-1), (row+2, col-1), (row-2, col-1))
      for i in knight_moves:
        if i[0] >= 0 and i[1] >= 0 and i[0] <= 7 and i[1] <= 7:
          match team:
            case 1:
              if self.state[i[0]][i[1]] <= 0:
                legal_moves.append((i[0], i[1], None))
            case -1:
              if self.state[i[0]][i[1]] >= 0:
                legal_moves.append((i[0], i[1], None))

    if piece == 3 or piece == -3: # bishop logic
      legal_moves += self.long_range_recursion(row, col, -1, -1, team)
      legal_moves += self.long_range_recursion(row, col, -1, 1, team)
      legal_moves += self.long_range_recursion(row, col, 1, -1, team)
      legal_moves += self.long_range_recursion(row, col, 1, 1, team)

    if piece == 4 or piece == -4: # rook logic
      legal_moves += self.long_range_recursion(row, col, 1, 0, team)
      legal_moves += self.long_range_recursion(row, col, -1, 0, team)
      legal_moves += self.long_range_recursion(row, col, 0, 1, team)
      legal_moves += self.long_range_recursion(row, col, 0, -1, team)

    if piece == 5 or piece == -5: # queen logic
      legal_moves += self.long_range_recursion(row, col, -1, 0, team)
      legal_moves += self.long_range_recursion(row, col, 1, 0, team)
      legal_moves += self.long_range_recursion(row, col, 0, -1, team)
      legal_moves += self.long_range_recursion(row, col, 0, 1, team)
      legal_moves += self.long_range_recursion(row, col, 1, 1, team)
      legal_moves += self.long_range_recursion(row, col, -1, 1, team)
      legal_moves += self.long_range_recursion(row, col, 1, -1, team)
      legal_moves += self.long_range_recursion(row, col, -1, -1, team)

    if piece == 6 or piece == -6: # king logic
      king_moves = ((row+1, col+1), (row+1,col-1), (row-1, col+1), (row-1, col-1), (row, col-1), (row, col+1), (row+1, col), (row-1, col))
      for i in king_moves:
        if i[0] >= 0 and i[1] >= 0 and i[0] >= 7 and i[1] >= 7:
          match team:
            case -1:
              if self.state[i[0]][i[1]] >= 0:
                legal_moves.append((i[0], i[1], None))
            case 1:
              if self.state[i[0]][i[1]] <= 0:
                legal_moves.append((i[0], i[1], None))
      if piece == 6 and row == 7 and col == 4 and not self.white_king_moved:
        if not self.white_rook_b_moved and self.state[7][7] == 4:
          if self.state[7][5] == 0 and self.state[7][6] == 0:
            legal_moves.append((7,6,None))
        if not self.white_rook_a_moved and self.state[7][0] == 4:
          if self.state[7][1] == 0 and self.state[7][2] == 0 and self.state[7][3] == 0:
            legal_moves.append((7,2,None))

      if piece == -6 and row == 0 and col == 4 and not self.black_king_moved:
        if not self.black_rook_b_moved and self.state[0][0] == -4:
          if self.state[0][5] == 0 and self.state[0][6] == 0:
            legal_moves.append((0,6,None))
        if not self.black_rook_a_moved and self.state[0][0] == -4:
          if self.state[0][1] == 0 and self.state[0][2] == 0 and self.state[0][3] == 0:
            legal_moves.append((0,2,None))

      saved_board_state = [r[:] for r in self.state]
      saved_white_king_moved = self.white_king_moved
      saved_black_king_moved = self.black_king_moved
      saved_white_rook_a_moved = self.white_rook_a_moved
      saved_white_rook_b_moved = self.white_rook_b_moved
      saved_black_rook_a_moved = self.black_rook_a_moved
      saved_black_rook_b_moved = self.black_rook_b_moved

      for move in legal_moves[:]:
        self.state == [r[:] for r in saved_board_state]
        self.white_king_moved = saved_white_king_moved
        self.black_king_moved = saved_black_king_moved
        self.white_rook_a_moved = saved_white_rook_a_moved
        self.white_rook_b_moved = saved_white_rook_b_moved
        self.black_rook_a_moved = saved_black_rook_a_moved
        self.black_rook_b_moved = saved_black_rook_b_moved

        new_row, new_col = move[0], move[1]
        promotion_piece = move[2]

        # extra casteling check: can't castle when in check
        if piece == 6 and row == 7 and col == 4 and new_row == 7 and new_col == 6:
          w_in_check, b_in_check, white_king_pos, black_king_pos = self.king_check()
          if w_in_check:
            legal_moves.remove(move)
            continue
          self.move_piece(7,4,7,5, None)
          w_in_check, b_in_check, white_king_pos, black_king_pos = self.king_check()
          if w_in_check:
            legal_moves.remove(move)
            continue

          self.state == [r[:] for r in saved_board_state]
          self.white_king_moved = saved_white_king_moved
          self.black_king_moved = saved_black_king_moved
          self.white_rook_a_moved = saved_white_rook_a_moved
          self.white_rook_b_moved = saved_white_rook_b_moved
          self.black_rook_a_moved = saved_black_rook_a_moved
          self.black_rook_b_moved = saved_black_rook_b_moved

        elif piece == 6 and row == 7 and col == 4 and new_row == 7 and new_col == 2:
          w_in_check, b_in_check, white_king_pos, black_king_pos = self.king_check()
          if w_in_check:
            legal_moves.remove(move)
            continue
          self.move_piece(7,4,7,3, None)
          w_in_check, b_in_check, white_king_pos, black_king_pos = self.king_check()
          if w_in_check:
            legal_moves.remove(move)
            continue

          self.state == [r[:] for r in saved_board_state]
          self.white_king_moved = saved_white_king_moved
          self.black_king_moved = saved_black_king_moved
          self.white_rook_a_moved = saved_white_rook_a_moved
          self.white_rook_b_moved = saved_white_rook_b_moved
          self.black_rook_a_moved = saved_black_rook_a_moved
          self.black_rook_b_moved = saved_black_rook_b_moved

        elif piece == -6 and row == 0 and col == 4 and new_row == 0 and new_col == 6:
          w_in_check, b_in_check, white_king_pos, black_king_pos = self.king_check()
          if b_in_check:
            legal_moves.remove(move)
            continue
          self.move_piece(0,4,0,5, None)
          w_in_check, b_in_check, white_king_pos, black_king_pos = self.king_check()
          if b_in_check:
            legal_moves.remove(move)
            continue

          self.state == [r[:] for r in saved_board_state]
          self.white_king_moved = saved_white_king_moved
          self.black_king_moved = saved_black_king_moved
          self.white_rook_a_moved = saved_white_rook_a_moved
          self.white_rook_b_moved = saved_white_rook_b_moved
          self.black_rook_a_moved = saved_black_rook_a_moved
          self.black_rook_b_moved = saved_black_rook_b_moved

        elif piece == 6 and row == 0 and col == 4 and new_row == 0 and new_col == 2:
          w_in_check, b_in_check, white_king_pos, black_king_pos = self.king_check()
          if b_in_check:
            legal_moves.remove(move)
            continue
          self.move_piece(0,4,0,3, None)
          w_in_check, b_in_check, white_king_pos, black_king_pos = self.king_check()
          if b_in_check:
            legal_moves.remove(move)
            continue

          self.state == [r[:] for r in saved_board_state]
          self.white_king_moved = saved_white_king_moved
          self.black_king_moved = saved_black_king_moved
          self.white_rook_a_moved = saved_white_rook_a_moved
          self.white_rook_b_moved = saved_white_rook_b_moved
          self.black_rook_a_moved = saved_black_rook_a_moved
          self.black_rook_b_moved = saved_black_rook_b_moved