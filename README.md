# Nextask

A task managing system that reduces decision-making during work
by guiding you to the next step — one item at a time.

---

## The idea

Most task managers show you everything at once. That creates decision fatigue —
you spend time choosing what to do instead of actually doing it.

Nextask works differently. You pick a task, and it shows you only the current item.
Complete it, move to the next. That's the entire loop.

---

## How it works

**Three screens, one flow:**

```
Task List → select a task → Execution → complete or skip → next item
                ↓
            Manage → create, edit, reorder tasks and items
```

**Task List** — shows all your tasks with a progress percentage. Tap one to start.

**Execution** — shows only the current item. Two actions:
- **Complete** — marks item done, moves to next
- **Skip** — moves item to end of remaining items, shows next

**Manage** — create tasks, add items in bulk or one at a time, reorder, edit, delete.

---

## Skip logic

Skipped items cycle to the end of the incomplete list. If all remaining items
are skipped, they reset and become available again — so you never get stuck.

---

## Progress

Progress is calculated as `(completed / total) × 100` and shown as a percentage
on both the task list and during execution. Nothing else is shown — no item counts,
no future items, no timeline.

---

## Installation

```bash
chmod +x install.sh
./install.sh
```

**Uninstall:**
```bash
./install.sh --uninstall
```

**Run:**
```bash
nextask
```

Or find Nextask in your applications menu.

---

## Requirements

- Linux (Ubuntu 20.04+)
- Python 3.10+
- PyQt6

---

## Data

Tasks and items are stored locally at:
```
~/.local/share/nextask/nextask.db
```

Plain SQLite — no cloud, no account, fully offline. Back it up by copying that file.

---

## Project structure

```
nextask/
├── main.py        ← entry point
├── db.py          ← all SQLite operations
├── ui.py          ← all three screens (TaskList, Execution, Manage)
├── styles.py      ← QSS stylesheet
├── install.sh     ← install and uninstall
├── requirements.txt
├── README.md
└── assets/
    └── icon.png
```

---

## License

MIT