import h5py
import numpy as np
import glob
import random

class ChessDataset:
  def __init__(self, file_pattern="*.h5"):
    self.files = sorted(glob.glob(file_pattern))
    self.file_handles = [h5py.File(f, "r") for f in self.files]

    self.lengths = [fh["boards"].shape[0] for fh in self.file_handles]

    self.cumulative = np.cumsum(self.lengths)
    self.total_size = int(self.cumulative[-1])

  def __len__(self):
    return self.total_size

  def _locate_index(self, idx):
    file_idx = np.searchsorted(self.cumulative, idx, side="right")
    prev_cum = 0 if file_idx == 0 else self.cumulative[file_idx - 1]
    local_idx = idx - prev_cum
    return file_idx, local_idx

  def __getitem__(self, idx):
    file_idx, local_idx = self._locate_index(idx)
    fh = self.file_handles[file_idx]

    return {
      "board": fh["boards"][local_idx],
      "mask": fh["legal_masks"][local_idx],
      "from": fh["from"][local_idx],
      "to": fh["to"][local_idx],
      "next_board": fh["next_boards"][local_idx]
    }

  def close(self):
    for fh in self.file_handles:
      fh.close()


class DataLoader:
  def __init__(self, dataset, batch_size=32, shuffle=True):
    self.dataset = dataset
    self.batch_size = batch_size
    self.shuffle = shuffle

    self.indices = list(range(len(dataset)))

  def __iter__(self):
    if self.shuffle:
      random.shuffle(self.indices)

    self.current = 0
    return self

  def __next__(self):
    if self.current >= len(self.indices):
      raise StopIteration

    batch_indices = self.indices[self.current:self.current + self.batch_size]
    self.current += self.batch_size
    boards, masks, froms, tos, next_boards = [], [], [], [], []

    for idx in batch_indices:
      sample = self.dataset[idx]
      boards.append(sample["board"])
      masks.append(sample["mask"])
      froms.append(sample["from"])
      tos.append(sample["to"])
      next_boards.append(sample["next_board"])

    return {
      "boards": np.array(boards, dtype=np.float32),
      "masks": np.array(masks, dtype=np.float32),
      "from": np.array(froms, dtype=np.int64),
      "to": np.array(tos, dtype=np.int64),
      "next_boards": np.array(next_boards, dtype=np.int64)
    }