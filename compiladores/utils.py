import os

def find_file(filename: str,
              root_dir: str = '.',
              exclude_dirs: list[str] = None) -> str:

    if exclude_dirs is None:
        exclude_dirs = ['venv', '__pycache__', 'node_modules', 'public', 'src']
    for dirpath, dirnames, filenames in os.walk(root_dir):

        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        if filename in filenames:
            return os.path.join(dirpath, filename)
    raise FileNotFoundError(f"Arquivo {filename!r} não encontrado em {root_dir}")