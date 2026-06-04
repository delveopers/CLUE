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