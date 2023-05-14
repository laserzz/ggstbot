import glob, os

os.system("python -m pip install -r requirements.txt")

path = "./**"

for p in glob.glob(path, recursive=True):
    if p.endswith("py"):
        os.system(f"python -m black {p}")
