import os, glob, random
import regex as re

def shuffle_games():
  random.seed(1234)
  with open("filtered_games.pgn", "r") as f:
    text = f.read()

  games = re.split(r'\n{2,}(?=\[Event)', text)
  random.shuffle(games)

  print(f"{len(games)} games shuffled.")

  with open("shuffled_filtered_games.pgn", "w") as f:
    f.write("\n\n".join(games))

  os.remove("filtered_games.pgn")

def pair_fens_and_moves():
  fen_files = sorted(glob.glob("*.fens"))
  move_files = sorted(glob.glob("*.moves"))

  for fen_file, move_file in zip(fen_files, move_files):
    base = fen_file.split(".")[0]
    output_file = f"{base}.dataset"

    with open(fen_file, "r") as f_fen, open(move_file, "r") as f_move, open(output_file, "w") as out:
      for fen, move in zip(f_fen, f_move):
        out.write(fen.strip() + " | " + move.strip() + "\n")

    print(f"Created {output_file}")

def main():
  pair_fens_and_moves()
  print("Formatting pipeline complete.")

if __name__ == "__main__":
  main()