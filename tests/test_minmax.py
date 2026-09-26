from engine.environment.chess_environment import ChessEnvironment
from engine.search.minmax import Search

env = ChessEnvironment()
search = Search()

before_hash = env.current_state().hash
before_board = [r[:] for r in env.current_state().board.state]

best_eval, best_move = search.minmax(env, 1, 2)
print('depth-2 search from start found a move:', best_move is not None)
print('env fully unwound after search (hash matches):', env.current_state().hash == before_hash)
print('env fully unwound after search (board matches):', env.current_state().board.state == before_board)
assert best_move is not None
assert env.current_state().hash == before_hash
assert env.current_state().board.state == before_board

env.reset(fen='6k1/5ppp/8/8/8/8/8/R6K w - - 0 1')
best_eval, best_move = search.minmax(env, 1, 2)
print('mate-in-1 found move:', best_move)
print('mate-in-1 eval is a mate score (expect >= 999):', best_eval >= 999)
assert best_move.to_row == 0 and best_move.to_col == 0
assert best_eval >= 999

env.make_move(best_move)
print('applying found move actually delivers checkmate:', env.is_terminal() and env.get_result() == 'white_win')
assert env.is_terminal() and env.get_result() == 'white_win'

print('all minmax tests passed')