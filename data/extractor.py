import os, glob, subprocess

def run_command(cmd):
  print(f"Running: {cmd}")
  subprocess.run(cmd, shell=True, check=True)

def create_filenames_file():
  files = sorted(glob.glob("lichess_elite_20*.pgn"))
  with open("filenames.txt", "w") as f:
    for file in files:
      f.write(file + "\n")
  print(f"{len(files)} PGN files listed.")

def combine_pgn():
  run_command("pgn-extract -ffilenames.txt --output combined.pgn")
  run_command("rm lichess_elite_20*.pgn filenames.txt")

def filter_time_control():
  with open("tags.txt", "w") as f:
    f.write('TimeControl >= "300"')
  run_command("pgn-extract -t tags.txt combined.pgn --output time_control_gte_5m.pgn")
  run_command("rm combined.pgn tags.txt")

def filter_checkmate():
  run_command("pgn-extract --checkmate time_control_gte_5m.pgn --output filtered_games.pgn")
  run_command("rm time_control_gte_5m.pgn")

def split_pgn():
  run_command("pgn-extract -#500000 filtered_games.pgn")
  os.remove("filtered_games.pgn")

def extract_fens_and_moves():
  pgn_files = sorted(glob.glob("[0-9]*.pgn"))

  for file in pgn_files:
    base = file.split(".")[0]

    run_command(f"pgn-extract -Wfen {file} --notags --noresults --output {base}.fens")
    run_command(f"pgn-extract -Wlalg {file} --notags --nomovenumbers --nochecks -w7 --output {base}.moves")

    os.remove(file)

def main():
  create_filenames_file()
  combine_pgn()
  filter_time_control()
  filter_checkmate()
  split_pgn()
  extract_fens_and_moves()
  print("Extraction pipeline complete.")

if __name__ == "__main__":
  main()