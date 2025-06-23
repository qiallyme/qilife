import os
import shutil
from a_core.e_utils.ae03_utils import load_env

env = load_env()
processed_dir = env["PROCESSED_FOLDER"]

def move_file(src: str, new_name: str) -> str:
    """
    Move src → processed_dir/new_name.
    Append (1), (2), … if dup exists.
    """
    dest = os.path.join(processed_dir, new_name)
    base, ext = os.path.splitext(dest)
    counter = 1
    while os.path.exists(dest):
        dest = f"{base}({counter}){ext}"
        counter += 1
    shutil.move(src, dest)
    return dest
