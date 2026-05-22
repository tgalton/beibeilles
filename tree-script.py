import os

EXCLUDE = {'.venv', '__pycache__', 'site-packages', '.git', 'node_modules'}

def tree(path, prefix=""):
    for item in sorted(os.listdir(path)):
        if item in EXCLUDE:
            continue
        full = os.path.join(path, item)
        print(prefix + "|-- " + item)
        if os.path.isdir(full):
            tree(full, prefix + "    ")

tree(".")