import json
import numpy as np
import pytest
from collections import Counter
from engine.chess.pgn import iter_games, replay
from engine.encoding.position_encoder import encode
from engine.encoding.move_encoder import index_to_move
from trainer.dataset import build_dataset, ShardDataset, iter_batches

OPERA = '[Event "opera"]\n[Result "1-0"]\n\n1. e4 e5 2. Nf3 d6 3. d4 Bg4 4. dxe5 Bxf3 5. Qxf3 dxe5 6. Bc4 Nf6 7. Qb3 Qe7 8. Nc3 c6 9. Bg5 b5 10. Nxb5 cxb5 11. Bxb5+ Nbd7 12. O-O-O Rd8 13. Rxd7 Rxd7 14. Rd1 Qe6 15. Bxd7+ Nxd7 16. Qb8+ Nxb8 17. Rd8# 1-0\n'
FOOLS = '[Event "fools"]\n[Result "0-1"]\n\n1. f3 e5 2. g4 Qh4# 0-1\n'
DRAW = '[Event "draw"]\n[Result "1/2-1/2"]\n\n1. e4 e5 1/2-1/2\n'
UNKNOWN = '[Event "unknown"]\n[Result "*"]\n\n1. e4 e5 *\n'
ALL_TEXT = '\n'.join([OPERA, FOOLS, DRAW, UNKNOWN])
TOTAL_POSITIONS = 33 + 4 + 2

def games():
  return iter_games(ALL_TEXT)

def load_all(directory):
  dataset = ShardDataset(directory)
  items = [dataset[i] for i in range(len(dataset))]
  return np.stack([i[0] for i in items]), np.array([i[1] for i in items]), np.array([i[2] for i in items])

def test_manifest_counts_and_shard_layout(tmp_path):
  manifest = build_dataset(games(), tmp_path, shard_size=10)
  assert manifest['num_positions'] == TOTAL_POSITIONS
  assert manifest['num_games'] == 3
  assert manifest['games_skipped_unknown_result'] == 1
  assert [s['count'] for s in manifest['shards']] == [10, 10, 10, 9]
  assert all((tmp_path / s['file']).exists() for s in manifest['shards'])
  assert json.loads((tmp_path / 'manifest.json').read_text()) == manifest

def test_value_targets_follow_side_to_move(tmp_path):
  build_dataset(games(), tmp_path, shuffle=False)
  _, _, value = load_all(tmp_path)
  expected = [r * (1 if ply % 2 == 0 else -1) for r, count in ((1, 33), (-1, 4), (0, 2)) for ply in range(count)]
  assert value.tolist() == expected

def test_unshuffled_samples_match_encoding_and_decode_to_the_human_move(tmp_path):
  opera = list(iter_games(OPERA))
  build_dataset(opera, tmp_path, shuffle=False)
  dataset = ShardDataset(tmp_path)
  for k, (state, move) in enumerate(replay(opera[0])):
    planes, policy, _ = dataset[k]
    assert np.array_equal(planes, encode(state))
    assert index_to_move(int(policy), state) == move

def test_shuffle_preserves_samples_but_changes_order(tmp_path):
  build_dataset(games(), tmp_path / 'ordered', shuffle=False)
  build_dataset(games(), tmp_path / 'shuffled', shuffle=True, seed=1)
  _, ordered_policy, ordered_value = load_all(tmp_path / 'ordered')
  _, shuffled_policy, shuffled_value = load_all(tmp_path / 'shuffled')
  assert Counter(zip(ordered_policy.tolist(), ordered_value.tolist())) == Counter(zip(shuffled_policy.tolist(), shuffled_value.tolist()))
  assert not np.array_equal(ordered_policy, shuffled_policy)

def test_shuffle_is_deterministic_per_seed(tmp_path):
  build_dataset(games(), tmp_path / 'a', seed=7)
  build_dataset(games(), tmp_path / 'b', seed=7)
  build_dataset(games(), tmp_path / 'c', seed=8)
  policy_a, policy_b, policy_c = (load_all(tmp_path / name)[1] for name in 'abc')
  assert np.array_equal(policy_a, policy_b)
  assert not np.array_equal(policy_a, policy_c)

def test_all_unknown_results_produces_empty_dataset(tmp_path):
  manifest = build_dataset(iter_games(UNKNOWN), tmp_path)
  assert manifest['num_positions'] == 0
  assert manifest['shards'] == []
  assert len(ShardDataset(tmp_path)) == 0

def test_max_games_limits_output(tmp_path):
  manifest = build_dataset(games(), tmp_path, max_games=1)
  assert manifest['num_games'] == 1
  assert manifest['num_positions'] == 33

@pytest.mark.parametrize('shuffle_buffer', [8, 10])
def test_mid_stream_flushes_lose_nothing(tmp_path, shuffle_buffer):
  manifest = build_dataset(games(), tmp_path, shard_size=4, shuffle_buffer=shuffle_buffer)
  counts = [s['count'] for s in manifest['shards']]
  assert sum(counts) == TOTAL_POSITIONS
  assert counts[:-1] == [4] * (len(counts) - 1)
  assert len(ShardDataset(tmp_path)) == TOTAL_POSITIONS

def test_dataset_item_shapes_dtypes_and_indexing(tmp_path):
  build_dataset(games(), tmp_path, shard_size=10)
  dataset = ShardDataset(tmp_path)
  planes, policy, value = dataset[0]
  assert planes.shape == (18, 8, 8) and planes.dtype == np.float32
  assert policy.dtype == np.int64 and value.dtype == np.float32
  assert all(np.array_equal(a, b) for a, b in zip(dataset[-1], dataset[len(dataset) - 1]))
  with pytest.raises(IndexError):
    dataset[len(dataset)]

def test_shard_cache_stays_bounded(tmp_path):
  build_dataset(games(), tmp_path, shard_size=5)
  dataset = ShardDataset(tmp_path, cache_size=2)
  for i in range(len(dataset)):
    dataset[i]
  assert len(dataset._cache) <= 2

def test_incompatible_encoding_is_rejected(tmp_path):
  build_dataset(games(), tmp_path)
  manifest = json.loads((tmp_path / 'manifest.json').read_text())
  manifest['num_planes'] = 17
  (tmp_path / 'manifest.json').write_text(json.dumps(manifest))
  with pytest.raises(ValueError):
    ShardDataset(tmp_path)

def test_iter_batches_covers_every_sample_exactly_once(tmp_path):
  build_dataset(games(), tmp_path, shard_size=10)
  batches = list(iter_batches(tmp_path, batch_size=8, seed=3))
  assert [len(b[1]) for b in batches] == [8, 8, 8, 8, 7]
  planes, policy, value = batches[0]
  assert planes.shape == (8, 18, 8, 8) and planes.dtype == np.float32
  assert policy.dtype == np.int64 and value.dtype == np.float32
  _, dataset_policy, dataset_value = load_all(tmp_path)
  seen = Counter((int(p), int(v)) for b in batches for p, v in zip(b[1], b[2]))
  assert seen == Counter(zip(dataset_policy.tolist(), dataset_value.tolist()))

def test_iter_batches_drop_last(tmp_path):
  build_dataset(games(), tmp_path, shard_size=10)
  assert sum(len(b[1]) for b in iter_batches(tmp_path, batch_size=8, drop_last=True)) == 32

def test_iter_batches_unshuffled_matches_dataset_order(tmp_path):
  build_dataset(games(), tmp_path, shard_size=10)
  _, dataset_policy, _ = load_all(tmp_path)
  streamed = np.concatenate([b[1] for b in iter_batches(tmp_path, batch_size=7, shuffle=False)])
  assert np.array_equal(streamed, dataset_policy)

def test_iter_batches_shuffle_depends_on_seed(tmp_path):
  build_dataset(games(), tmp_path, shard_size=10)
  first = np.concatenate([b[1] for b in iter_batches(tmp_path, batch_size=8, seed=1)])
  again = np.concatenate([b[1] for b in iter_batches(tmp_path, batch_size=8, seed=1)])
  other = np.concatenate([b[1] for b in iter_batches(tmp_path, batch_size=8, seed=2)])
  assert np.array_equal(first, again)
  assert not np.array_equal(first, other)