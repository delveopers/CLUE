import json
import numpy as np
from collections import OrderedDict
from pathlib import Path
from engine.chess.pgn import replay
from engine.encoding.position_encoder import encode, NUM_PLANES
from engine.encoding.move_encoder import move_to_index, index_to_move, ACTION_SPACE_SIZE

MANIFEST = 'manifest.json'

class ShardWriter:
  def __init__(self, out_dir, shard_size=4096, shuffle_buffer=None, shuffle=True, seed=0):
    self.out_dir = Path(out_dir)
    self.out_dir.mkdir(parents=True, exist_ok=True)
    self.shard_size, self.shuffle = shard_size, shuffle
    self.shuffle_buffer = shuffle_buffer if shuffle else shard_size * 8
    self.rng = np.random.default_rng(seed)
    self.planes, self.policy, self.value, self.shards = [], [], [], []

  def add(self, planes, policy, value):
    self.planes.append(planes)
    self.policy.append(policy)
    self.value.append(value)
    if len(self.policy) >= self.shuffle_buffer:
      self._write(final=False)

  def _write(self, final):
    count = len(self.policy)
    if count == 0: return

    planes, policy, value = np.stack(self.planes), np.array(self.policy, dtype=np.int16), np.array(self.value, dtype=np.int8)
    if self.shuffle:
      order = self.rng.permutation(count)
      planes, policy, value = planes[order], policy[order], value[order]

    full = count if final else (count // self.shard_size) * self.shard_size
    for start in range(0, full, self.shard_size):
      stop = min(start + self.shard_size, full)
      name = f"shard_{len(self.shards):05d}.npz"
      np.savez_compressed(self.out_dir / name, planes=planes[start:stop], policy=policy[start:stop], value=value[start:stop])
      self.shards.append({'file': name, 'count': stop-start})
    self.planes, self.policy, self.value = list(planes[full:]), list(planes[full:]), list(value[full:])

  def close(self, game_used=0, game_skipped=0):
    self._write(final=True)
    manifest = {'num_planes': NUM_PLANES, 'action_space_size': ACTION_SPACE_SIZE, 'shard_size': self.shard_size, 'num_positions': sum(s['count'] for s in self.shards),
                'num_games': game_used, 'games_skipped_unknown_result': game_skipped, 'shards': self.shards}
    (self.out_dir / MANIFEST).write_text(json.dumps(manifest, indent=2))
    return manifest

def build_dateset(games, out_dir, shard_size=4096, shuffle_buffer=None, shuffle=True, seed=0, max_games=None):
  writer = ShardWriter(out_dir, shard_size, shuffle_buffer, shuffle, seed)
  games_used = game_skipped = 0

  for game in games:
    if max_games is not None and games_used >= max_games: break
    if game.result is None:
      game_skipped += 1
      continue

    for state, move in replay(game):
      writer.add(encode(state).astype(np.uint8), move_to_index(move, state), game.result * state.side_to_move)
      games_used += 1

  return writer.close(games_used, game_skipped)

class ShardDataset:
  def __init__(self, directory, cache_size=2):
    self.directory, self.cache_size, self._cache = Path(directory), cache_size, OrderedDict()
    manifest = json.loads((self.directory / MANIFEST).read_text())
    if manifest['num_planes'] != NUM_PLANES or manifest['action_space_size'] != ACTION_SPACE_SIZE:
      raise ValueError(f'dataset was built with planes={manifest["num_planes"]}, actions={manifest["action_space_size"]}; current encoding is planes={NUM_PLANES}, actions={ACTION_SPACE_SIZE}')

    self.shards = manifest['shards']
    self.offsets = np.cumsum([0] + (s['count'] for s in self.shards))

  def __len__(self):
    return int(self.offsets[-1])

  def load_shard(self, shard_index):
    if shard_index in self._cache:
      self._cache.move_to_end(shard_index)
      return self._cache[shard_index]

    with np.load(self.directory / self.shards[shard_index]['file']) as archive:
      data = {key: archive[key] for key in archive.files}
    self._cache[shard_index] = data

    if len(self._cache) > self.cache_size:
      self._cache.popitem(last=False)
    return data

  def __getitem__(self, index):
    if index < 0: index += len(self)
    if not 0 <= index < len(self): raise IndexError(index)

    shard_index = int(np.searchsorted(self.offsets, index, side='right') - 1)
    data, local = self.load_shard(shard_index), index - int(self.offsets[shard_index])
    return data['planes'][local].astype(np.float32), np.int64(data['policy'][local]), np.float32(data['value'][local])

def _to_batch(planes, policy, value):
  return planes.astype(np.float32), policy.astype(np.int64), value.astype(np.float32)

def iter_batches(directory, batch_size, shuffle=True, seed=0, drop_last=False):
  dataset, rng = ShardDataset(directory), np.random.default_rng(seed)
  order = rng.permutation(len(dataset.shards)) if shuffle else range(len(dataset.shards))
  carry = None

  for shard_index in order:
    data = dataset.load_shard(int(shard_index))
    planes, policy, value = data['planes'], data['policy'], data['value']

    if shuffle:
      perm = rng.permutation(len(policy))
      planes, policy, value = planes[perm], policy[perm], value[perm]
    if carry is not None:
      planes, policy, value = np.concatenate([carry[0], planes]), np.concatenate([carry[1], policy]), np.concatenate([carry[2], value])

    full = (len(policy) // batch_size) * batch_size
    for start in range(0, full, batch_size):
      yield _to_batch(planes[start:start + batch_size], policy[start:start + batch_size], value[start:start + batch_size])
    carry = (planes[full:], policy[full:], value[full:])

  if carry is not None and len(carry[1]) > 0 and not drop_last:
    yield _to_batch(*carry)