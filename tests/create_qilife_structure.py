import os

# Set target path for QiLife app root
base_path = "F:/QiLife"

# Define folders to create inside the QiLife project
folders_to_create = [
    "src/ai",
    "src/common",
    "src/constants",
    "src/core",
    "src/fileflow",
    "src/lifelog",
    "src/qinote",
    "src/pipelines",
    "src/ui",
    "src/interfaces",
    "src/archive",
    "config",
    "tests",
    "delete",
    "docs",
    "static",
    "templates",
    "scripts"
]

# Define basic starter files in the root
files_to_create = [
    ".gitignore",
    "README.md",
    "requirements.txt",
    "start.py",
    ".env"
]

# Create all folders with a .keep file to preserve them in Git
for folder in folders_to_create:
    full_path = os.path.join(base_path, folder)
    os.makedirs(full_path, exist_ok=True)
    keep_file = os.path.join(full_path, ".keep")
    with open(keep_file, "w") as f:
        f.write("# placeholder to keep this directory in version control\n")
    print(f"📁 Created folder: {full_path}")

# Create essential files in the root of the project
for file in files_to_create:
    file_path = os.path.join(base_path, file)
    with open(file_path, "w") as f:
        if file == "README.md":
            f.write("# QiLifeAi Unified App\n\nWelcome to the QiLifeAi local assistant.")
        elif file == ".gitignore":
            f.write("__pycache__/\n.env\n*.pyc\n")
        elif file == "requirements.txt":
            f.write("# List your dependencies here\n")
        elif file == "start.py":
            f.write("# Entry point for the QiLife app\n\nif __name__ == '__main__':\n    print('QiLife App starting...')\n")
        elif file == ".env":
            f.write("# Environment variables go here\n")
    print(f"📄 Created file: {file_path}")

print("\n✅ QiLife project structure created successfully at F:/QiLife")
