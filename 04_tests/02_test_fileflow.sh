#!/usr/bin/env bash
# scripts/test_fileflow.sh
# Usage: ./test_fileflow.sh /full/path/to/your/testfile.png

TEST_FILE="$1"
if [ -z "$TEST_FILE" ]; then
  echo "❌  Usage: $0 /full/path/to/your/testfile.png"
  exit 1
fi

python - <<EOF
import os
from common.utils import load_env
from QiFileFlow.analyze import analyze_file
from QiFileFlow.rename import generate_new_name
from QiFileFlow.filer import move_file

# Load env (must have SOURCE_FOLDER & PROCESSED_FOLDER set)
cfg = load_env()
print("✔️ Env loaded. SOURCE_FOLDER=", cfg["SOURCE_FOLDER"])
print("✔️ PROCESSED_FOLDER=", cfg["PROCESSED_FOLDER"])

# Analyze
meta = analyze_file("$TEST_FILE")
print("🕵️  OCR/Text snippet:", repr(meta.get("text",""))[:100])
print("⏱️  Timestamp:", meta["timestamp"])

# Rename
new_name = generate_new_name("$TEST_FILE", meta)
print("✏️  New filename:", new_name)

# Move
dest = move_file("$TEST_FILE", new_name)
print("🚚  File moved to:", dest)
EOF
