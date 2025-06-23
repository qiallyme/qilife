# QiLife
QiLife is a modular, AI-assisted automation system designed to bring structure, insight, and flow to your digital world. It organizes scattered information, automates file processing, tracks activity, and creates meaningful logs—all from a single interface.

> ⚛️ Think of it as a digital nervous system for your life.
---

## 🌿 Purpose
QiLife was built to:
- Monitor and process files and folders automatically
- Extract and organize context from documents and screenshots
- Log life and work activity into Notion or local databases
- Help neurodivergent users (especially ADHD minds) make sense of chaos
- Offer a toolkit of reusable tools for file management, reflection, and digital housekeeping

---
## 🧱 Folder Structure
| Folder           | Purpose                                                                 |
|------------------|-------------------------------------------------------------------------|
| `00_core/`        | Core logic modules: fileflow engine, lifelog processor, QuNote system  |
| `01_gui/`         | Interface components and UI layout                                     |
| `02_scripts/`     | One-off scripts, scratch utilities, and config helpers                 |
| `03_docs/`        | Internal notes and documentation                                       |
| `04_tests/`       | Test scripts and test files                                            |
| `05_vector_db/`   | Local vector store (for embeddings, document matching, etc.)           |
| `06_tools/`       | Mini apps and reusable helpers (file merger, Notion logger, etc.)      |
| `07_sandbox/`     | Experimental playground—try things without affecting main code         |

---
## 🧠 Key Concepts

### FileFlow
An intelligent file watcher and organizer that:
- Renames files based on content or metadata
- Moves them into structured folders
- Extracts text, context, and relevance

### LifeLog
A passive life-tracking system that:
- Captures activities, screenshots, and patterns
- Logs entries to Notion or local storage
- Helps you reflect on your day with clarity
### QuNote
A quantum-inspired thought framework:
- Captures thoughts, tasks, and memories as connected nodes
- Reflects ADHD-style thinking—nonlinear, relational, multi-layered
- Organizes insight across time and context

---
## 🛠 Tools & Utilities
Reusable helpers live in `06_tools/`, including:
# QiLife Tools Library

This repository houses modular utilities and mini-apps designed to automate, sort, clean, and understand your digital life. Each category folder contains task-focused tools organized by purpose:

- `0601_file_manipulators`: Tools for sorting, renaming, or transforming files.
- `0602_folder_manipulators`: Folder creation, merging, and structural cleanups.
- `0603_ai`: Semantic tools using AI to extract meaning and provide insights.
- `0604_loggers`: Background monitors and trackers for file and device activity.
- `0605_index_dups`: Indexing and duplicate detection utilities.
- `0606_configurators`: API and service configuration modules.
- `0607_utilities`: Internal helpers and generic system tools.

Most tools are standalone and can be reused or integrated. This structure aims to mirror real workflows, not arbitrary categories.

---

To run a tool, navigate into its folder and launch with:
```bash
python toolname.py
```
Some tools may require environment variables or additional dependencies (see individual READMEs).

---
## 🚧 Status
QiLife is actively evolving.  
Modules are refactored gradually, and integration points are expanding.

Use at your own pace—this project is designed to be flexible, personal, and extensible.

---
## 🤝 Contributing
This project is personal, but modular. If you're exploring similar territory, feel free to fork and adapt. Guidance is available through the code and structure itself.
---

## 📜 License
MIT License — See `3_LICENSE` for details.
