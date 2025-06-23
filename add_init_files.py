from pathlib import Path

project_root = Path(__file__).resolve().parent  # or manually: Path("C:/Users/codyr/Documents/GitHub/qilife")

def add_init_files(base: Path):
    count = 0
    for folder in base.rglob("*"):
        if folder.is_dir() and not (folder / "__init__.py").exists():
            (folder / "__init__.py").touch()
            print(f"🧩 Added __init__.py to: {folder}")
            count += 1
    print(f"\n✅ Done. Added {count} __init__.py files.")

add_init_files(project_root)
