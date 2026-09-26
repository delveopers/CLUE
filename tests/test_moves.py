from engine.chess.state import GameState
from engine.chess.move import Move
from engine.chess.move_generator import generate_pseudo_legal_moves

def squares(moves):
  return {(m.to_row, m.to_col) for m in moves}

def empty_state(side_to_move=1):
  state = GameState.initial()
  for r in range(8):
    for c in range(8): state.board.state[r][c] = 0
  state.side_to_move = side_to_move
  return state

def test_knight_center_move_count():
  state = empty_state()
  state.board.state[4][4] = 2
  assert len(generate_pseudo_legal_moves(state, 4, 4)) == 8

def test_knight_corner_move_count():
  state = empty_state()
  state.board.state[0][0] = 2
  assert len(generate_pseudo_legal_moves(state, 0, 0)) == 2

def test_bishop_blocked_by_own_piece():
  state = empty_state()
  state.board.state[4][4], state.board.state[6][6] = 3, 1
  moves = generate_pseudo_legal_moves(state, 4, 4)
  assert (6, 6) not in squares(moves)
  assert (5, 5) in squares(moves)
  assert (7, 7) not in squares(moves)

def test_rook_captures_enemy_and_stops():
  state = empty_state()
  state.board.state[4][4], state.board.state[4][6] = 4, -1
  moves = generate_pseudo_legal_moves(state, 4, 4)
  assert (4, 6) in squares(moves)
  assert (4, 7) not in squares(moves)

def test_queen_move_count_center_open_board():
  state = empty_state()
  state.board.state[4][4] = 5
  assert len(generate_pseudo_legal_moves(state, 4, 4)) == 27

def test_king_move_count_center_open_board():
  state = empty_state()
  state.board.state[4][4] = 6
  assert len(generate_pseudo_legal_moves(state, 4, 4)) == 8

def test_pawn_double_step_available_from_start_row():
  state = empty_state()
  state.board.state[6][4] = 1
  moves = generate_pseudo_legal_moves(state, 6, 4)
  assert (5, 4) in squares(moves)
  assert (4, 4) in squares(moves)

def test_pawn_double_step_unavailable_off_start_row():
  state = empty_state()
  state.board.state[5][4] = 1
  moves = generate_pseudo_legal_moves(state, 5, 4)
  assert squares(moves) == {(4, 4)}

def test_pawn_promotion_generates_four_choices():
  state = empty_state()
  state.board.state[1][0] = 1
  moves = generate_pseudo_legal_moves(state, 1, 0)
  assert {m.promotion for m in moves} == {2, 3, 4, 5}

def test_pawn_en_passant_candidate():
  state = empty_state()
  state.board.state[3][4], state.board.state[3][3] = 1, -1
  state.en_passant_square = (2, 3)
  moves = generate_pseudo_legal_moves(state, 3, 4)
  ep_moves = [m for m in moves if m.is_en_passant()]
  assert len(ep_moves) == 1
  assert ep_moves[0].to_square == (2, 3)

def test_white_kingside_castle_candidate_when_path_clear():
  state = empty_state()
  state.board.state[7][4], state.board.state[7][7] = 6, 4
  moves = generate_pseudo_legal_moves(state, 7, 4)
  castles = [m for m in moves if m.is_castle()]
  assert len(castles) == 1
  assert castles[0].flag == Move.CASTLE_KINGSIDE

def test_castle_unavailable_without_right():
  state = empty_state()
  state.board.state[7][4], state.board.state[7][7] = 6, 4
  state.white_kingside = False
  moves = generate_pseudo_legal_moves(state, 7, 4)
  assert not any(m.is_castle() for m in moves)