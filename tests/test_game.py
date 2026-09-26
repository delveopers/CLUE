import pygame
from ..engine import Game

game = Game()
print('game initialized with ChessEnvironment:', hasattr(game, 'env'))
print('no leftover active_team attribute:', not hasattr(game, 'active_team'))
print('no leftover board attribute:', not hasattr(game, 'board'))

def click(row, col):
  x = col * game.square_size + game.square_size + game.square_size // 2
  y = row * game.square_size + game.square_size + game.square_size // 2
  pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(x, y), button=1))

click(6, 4)
game.check_click()
print('pawn selected at e2:', game.selected_square == (6, 4))

click(4, 4)
game.check_click()
print('white pawn e2-e4 applied, side to move is black:', game.env.side_to_move() == -1)
assert game.env.side_to_move() == -1

pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION, pos=(0, 0)))
game.check_click()
print('black (CPU) replied automatically, side to move is white again:', game.env.side_to_move() == 1)
assert game.env.side_to_move() == 1

game.env.reset(fen='7k/P7/8/8/8/8/4K3/8 w - - 0 1')
click(1, 0)
game.check_click()
print('pawn selected at a7:', game.selected_square == (1, 0))

click(0, 0)
game.check_click()
print('promotion_possible triggered:', game.promotion_possible)
print('matched_moves actually populated (this was the bug):', len(game.matched_moves) == 4)
assert game.promotion_possible
assert len(game.matched_moves) == 4

game.draw()

queen_rect = game.promotion_rects[5]
pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(queen_rect.x + 60, queen_rect.y + 5), button=1))
game.check_click()

board = game.env.current_state().board.state
print('queen promotion actually applied to the board:', board[0][0] == 5)
print('pawn no longer at a7:', board[1][0] == 0)
print('promotion_possible cleared after selection:', not game.promotion_possible)
assert board[0][0] == 5
assert board[1][0] == 0
assert not game.promotion_possible

print('all game.py tests passed')