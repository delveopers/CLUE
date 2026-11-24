import sys, glob, h5py
import numpy as np

SAMPLE = 2000
KNOWN = ('boards', 'legal_masks', 'from', 'to', 'next_boards')

def describe(name, obj):
  if isinstance(obj, h5py.Dataset):
    print(f'  {name}: shape={obj.shape} dtype={obj.dtype} chunks={obj.chunks} compression={obj.compression}')

def main(pattern):
  files = sorted(glob.glob(pattern))
  if not files:
    sys.exit(f'no files match {pattern}')
  total = 0
  for path in files:
    with h5py.File(path, 'r') as f:
      total += f['boards'].shape[0]
  print(f'{len(files)} file(s), {total:,} samples total, first files: {files[:3]}')

  with h5py.File(files[0], 'r') as f:
    print(f'\ndatasets in {files[0]}:')
    f.visititems(describe)
    print('  file attrs:', dict(f.attrs))
    print('  keys the dataloader does not read:', [k for k in f.keys() if k not in KNOWN] or 'none')
    k = min(SAMPLE, f['boards'].shape[0])
    boards, nexts, masks, frm, to = f['boards'][:k], f['next_boards'][:k], f['legal_masks'][:k], f['from'][:k], f['to'][:k]

  print(f'\nfrom: min={frm.min()} max={frm.max()}   to: min={to.min()} max={to.max()}')

  flat = masks.reshape(k, -1)
  print(f'\nlegal_masks: per-sample size={flat.shape[1]}, mean ones per sample={flat.sum(1).mean():.1f}, distinct values={np.unique(flat)[:5].tolist()}')
  candidates = {'from*64+to': frm * 64 + to, 'to*64+from': to * 64 + frm, 'from': frm, 'to': to}
  for name, idx in candidates.items():
    if idx.max() < flat.shape[1]:
      print(f'  human move is marked legal if indexed as {name}: {(flat[np.arange(k), idx] > 0).mean():.0%}')

  print(f'\nboards: shape={boards.shape[1:]} dtype={boards.dtype} min={boards.min()} max={boards.max()} distinct={np.unique(boards).size}')
  if boards.shape[1:] == (8, 8):
    print('  first board (row 0 is printed first):')
    for row in boards[0]:
      print('   ', ' '.join(f'{int(v):2d}' for v in row))
    diff = (boards.reshape(k, -1) != nexts.reshape(k, -1)).sum(1)
    print(f'  squares that differ between board and next_board (count: samples): {dict(enumerate(np.bincount(diff)[:8].tolist()))}')
    same = np.mean([np.array_equal(boards[i + 1], nexts[i]) for i in range(k - 1)])
    flipped = np.mean([np.array_equal(boards[i + 1], -nexts[i][::-1]) for i in range(k - 1)])
    print(f'  row i+1 board equals row i next_board: {same:.0%};  equals colour-swapped + row-flipped next_board: {flipped:.0%}')
  else:
    print('  not an 8x8 grid, skipping board-level checks')

if __name__ == '__main__':
  main(sys.argv[1] if len(sys.argv) > 1 else 'data/*.h5')