import re
import logging
from collections import namedtuple
from .fen import parse_fen
from .state import GameState
from .move import Move
from . import rules

logger = logging.getLogger(__name__)

class PGNError(ValueError):
  pass

ResolvedGame = namedtuple('ResolvedGame', ['headers', 'start_fen', 'moves', 'result'])

HEADER_RE = re.compile(r'^\[(\`w+)\s+"(.*)"\]\s*$')
MOVE_NUMBER_RE = re.compile(r'^\d+\.+')
SAN_RE = re.compile(r'^([NBRQK])?([a-h])?([1-8])?(x)?([a-h][1-8])(?:=?([NBRQ]))?$')
PIECE_TYPES = {'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6}
PROMOTION_IDS = {'N': 2, 'B': 3, 'R': 4, 'Q': 5}
RESULTS = {'1-0': 1, '0-1': -1, '1/2-1/2': 0, '*': None}

def _split_games(lines):
  headers, movetext, started = {}, [], False
  for line in lines:
    stripped = line.strip()
    if stripped.startswith('%'): continue
    match = HEADER_RE.match(stripped)
    if match:
      if started:
        yield headers, '\n'.join(movetext)
        headers, movetext, started = {}, [], False
      headers[match.group(1)] = match.group(2)
    elif stripped:
      movetext.append(stripped)
      started = True
  if headers or movetext:
    yield headers, '\n'.join(movetext)

def _strip_movetext(text):
  out, depth, i, n = [], 0, 0, len(text)
  while i < n:
    ch = text[i]
    if ch == '{':
      end = text.find('}', i)
      i = n if end == -1 else end + 1
      out.append(' ')
    elif ch == ';':
      end = text.find('\n', i)
      i = n if end == -1 else end
    elif ch == '(':
      depth += 1
      i += 1
      out.append(' ')
    elif ch == ')':
      depth = max(0, depth - 1)
      i += 1
      out.append(' ')
    else:
      if depth == 0: out.append(ch)
      i += 1
  return ''.join(out)

def _tokenize(movetext):
  san, result_token = [], None
  for token in _strip_movetext(movetext).split():
    if token in RESULTS:
      result_token = token
      break
    if token.startswith('$'): continue
    token = MOVE_NUMBER_RE.sub('', token)
    if token: san.append(token)
  return san, result_token

def san_to_move(state, san):
  token = san.rstrip('+#!?')
  castle_token = token.replace('0', 'O')
  legal = rules.legal_moves(state)

  if castle_token in ('O-O', 'O-O-O'):
    flag = Move.CASTLE_KINGSIDE if castle_token == 'O-O' else Move.CASTLE_QUEENSIDE
    matches = [m for m in legal if m.flag == flag]
  else:
    parsed = SAN_RE.match(token)
    if parsed is None:
      raise PGNError(f'unparseable move: {san}')
    piece, from_file, from_rank, _, dest, promotion = parsed.groups()
    piece_type = PIECE_TYPES[piece] if piece else 1
    to_row, to_col = 8 - int(dest[1]), ord(dest[0]) - 97
    promotion_id = PROMOTION_IDS[promotion] if promotion else None
    board = state.board.state
    matches = [m for m in legal if not m.is_castle() and abs(board[m.from_row][m.from_col]) == piece_type and m.to_row == to_row and m.to_col == to_col and m.promotion == promotion_id and (from_file is None or m.from_col == ord(from_file) - 97) and (from_rank is None or m.from_row == 8 - int(from_rank))]

  if len(matches) != 1:
    raise PGNError(f'{"illegal" if not matches else "ambiguous"} move: {san}')
  return matches[0]

def _resolve(headers, movetext):
  if headers.get('Variant', 'Standard') not in ('Standard', 'From Position'):
    raise PGNError(f'unsupported variant: {headers["Variant"]}')

  start_fen = headers.get('FEN')
  try:
    state = parse_fen(start_fen) if start_fen else GameState.initial()
  except (KeyError, ValueError, IndexError):
    raise PGNError(f'invalid FEN header: {start_fen}') from None

  san_moves, result_token = _tokenize(movetext)
  moves = []
  for ply, san in enumerate(san_moves, start=1):
    try:
      move = san_to_move(state, san)
    except PGNError as error:
      raise PGNError(f'ply {ply}: {error}') from None
    moves.append(move)
    state.make_move(move)

  return ResolvedGame(headers, start_fen, moves, RESULTS.get(result_token or headers.get('Result', '*')))

def iter_games(source, skip_invalid=True):
  lines = source.splitlines() if isinstance(source, str) else source
  for headers, movetext in _split_games(lines):
    try:
      yield _resolve(headers, movetext)
    except PGNError as error:
      if not skip_invalid: raise
      logger.warning('skipping game %s: %s', headers.get('Event', '?'), error)

def load_pgn_file(path, skip_invalid=True):
  with open(path, encoding='utf-8', errors='replace') as handle:
    yield from iter_games(handle, skip_invalid)

def replay(game):
  state = parse_fen(game.start_fen) if game.start_fen else GameState.initial()
  for move in game.moves:
    yield state, move
    state.make_move(move)