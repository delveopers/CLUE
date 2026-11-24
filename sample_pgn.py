import sys
import zstandard

source, target = sys.argv[1], sys.argv[2]
limit_mb = float(sys.argv[3]) if len(sys.argv) > 3 else 20

with open(source, 'rb') as handle, zstandard.ZstdDecompressor().stream_reader(handle) as reader:
  data = reader.read(int(limit_mb * 1024 * 1024))

text = data.decode('utf-8', errors='replace')
cut = text.rfind('\n[Event ')
text = text[:cut] if cut != -1 else text
with open(target, 'w', encoding='utf-8') as out:
  out.write(text.rstrip() + '\n')
print(f'wrote {target}: {text.count(chr(10) + "[Event ") + 1} games, {len(text) / 2**20:.1f} MiB')