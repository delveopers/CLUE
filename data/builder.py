import glob
import numpy as np
import chess, h5py
from .level import PIECE_TO_CLASS, PIECE_TO_PLANE


def square_to_index(square):
  return chess.square_file(square) + chess.square_rank(square) * 8

def board_to_tensor(board):
  tensor = np.zeros((8, 8, 17), dtype=np.float32)

  # Pieces
  for square in chess.SQUARES:
    piece = board.piece_at(square)
    if piece:
      plane = PIECE_TO_PLANE[piece.symbol()]
      r = chess.square_rank(square)
      c = chess.square_file(square)
      tensor[r, c, plane] = 1

  # Attack maps
  for square in chess.SQUARES:
    r = chess.square_rank(square)
    c = chess.square_file(square)
    if board.is_attacked_by(chess.WHITE, square):
      tensor[r, c, 12] = 1
    if board.is_attacked_by(chess.BLACK, square):
      tensor[r, c, 13] = 1

  # Castling rights
  if board.has_kingside_castling_rights(chess.WHITE): tensor[:, :, 14] = 1
  if board.has_queenside_castling_rights(chess.WHITE): tensor[:, :, 14] = 1
  if board.has_kingside_castling_rights(chess.BLACK): tensor[:, :, 14] = 1
  if board.has_queenside_castling_rights(chess.BLACK): tensor[:, :, 14] = 1

  # En passant
  if board.ep_square is not None:
    r = chess.square_rank(board.ep_square)
    c = chess.square_file(board.ep_square)
    tensor[r, c, 15] = 1

  # Side to move
  if board.turn == chess.WHITE: tensor[:, :, 16] = 1
  return tensor

def legal_move_mask(board):
  mask = np.zeros((64, 64), dtype=np.float32)
  for move in board.legal_moves:
    from_sq = square_to_index(move.from_square)
    to_sq = square_to_index(move.to_square)
    mask[from_sq, to_sq] = 1
  return mask

def next_board_tensor(board, move):
  board.push(move)
  tensor = np.zeros((8, 8), dtype=np.int8)

  for square in chess.SQUARES:
    piece = board.piece_at(square)
    r = chess.square_rank(square)
    c = chess.square_file(square)
    tensor[r, c] = PIECE_TO_CLASS[piece.symbol() if piece else None]

  board.pop()
  return tensor

def process_file(fen_file, move_file, h5_file):
  with open(fen_file) as f_fen, open(move_file) as f_move:
    fens = f_fen.readlines()
    moves = f_move.readlines()

  n = len(fens)

  boards = np.zeros((n, 8, 8, 17), dtype=np.float32)
  masks = np.zeros((n, 64, 64), dtype=np.float32)
  froms = np.zeros((n,), dtype=np.int16)
  tos = np.zeros((n,), dtype=np.int16)
  next_boards = np.zeros((n, 8, 8), dtype=np.int8)

  for i in range(n):
    fen = fens[i].strip()
    move_uci = moves[i].strip()

    board = chess.Board(fen)
    move = chess.Move.from_uci(move_uci)

    boards[i] = board_to_tensor(board)
    masks[i] = legal_move_mask(board)
    froms[i] = square_to_index(move.from_square)
    tos[i] = square_to_index(move.to_square)
    next_boards[i] = next_board_tensor(board, move)

    if i % 10000 == 0:
      print(f"Processed {i}/{n}")

  with h5py.File(h5_file, "w") as hf:
    hf.create_dataset("boards", data=boards)
    hf.create_dataset("legal_masks", data=masks)
    hf.create_dataset("from", data=froms)
    hf.create_dataset("to", data=tos)
    hf.create_dataset("next_boards", data=next_boards)