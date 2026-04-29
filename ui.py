"""
nextask/ui.py
All UI screens — redesigned with proper visual hierarchy.
  TaskListScreen   — card-based task list with progress
  ExecutionScreen  — focused single-item view, centred and calm
  ManageScreen     — tabbed: Tasks tab + Items tab, no dumping
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QPushButton, QScrollArea,
    QLineEdit, QPlainTextEdit,
    QMessageBox, QSizePolicy, QProgressBar,
    QInputDialog, QSpacerItem,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QCursor

from db import Database
from styles import (
    STYLESHEET,
    C_BG, C_SURFACE, C_BORDER, C_BORDER_DARK,
    C_TEXT, C_TEXT_2, C_TEXT_MUTED,
    C_ACCENT, C_ACCENT_LT, C_DANGER, C_SKIP_LT, C_SKIP,
    C_SURFACE_2,
)

SCREEN_LIST   = 0
SCREEN_EXEC   = 1
SCREEN_MANAGE = 2


# ── Helpers ───────────────────────────────────

def hline():
    """Thin horizontal rule."""
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"color: {C_BORDER}; background: {C_BORDER}; max-height: 1px; border: none;")
    return f


def spacer(h=1):
    w = QWidget()
    w.setFixedHeight(h)
    w.setStyleSheet("background: transparent;")
    return w


# ══════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════

class MainWindow(QMainWindow):

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self._setup_window()
        self._build_ui()
        self.setStyleSheet(STYLESHEET)

    def _setup_window(self):
        self.setWindowTitle("Nextask")
        self.setMinimumSize(500, 660)
        self.resize(520, 720)
        geo = self.screen().availableGeometry()
        self.move((geo.width()-520)//2, (geo.height()-720)//2)

    def _build_ui(self):
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._list_screen   = TaskListScreen(self.db, self)
        self._exec_screen   = ExecutionScreen(self.db, self)
        self._manage_screen = ManageScreen(self.db, self)

        self._stack.addWidget(self._list_screen)
        self._stack.addWidget(self._exec_screen)
        self._stack.addWidget(self._manage_screen)

        self._list_screen.sig_open_task.connect(self._go_exec)
        self._list_screen.sig_open_manage.connect(self._go_manage)
        self._exec_screen.sig_back.connect(self._go_list)
        self._manage_screen.sig_back.connect(self._go_list)

    def _go_list(self):
        self._list_screen.refresh()
        self._stack.setCurrentIndex(SCREEN_LIST)

    def _go_exec(self, task_id: int):
        self._exec_screen.load_task(task_id)
        self._stack.setCurrentIndex(SCREEN_EXEC)

    def _go_manage(self, task_id: int):
        self._manage_screen.load(task_id)
        self._stack.setCurrentIndex(SCREEN_MANAGE)

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)


# ══════════════════════════════════════════════
# SCREEN 1 — TASK LIST
# ══════════════════════════════════════════════

class TaskListScreen(QWidget):

    sig_open_task   = pyqtSignal(int)
    sig_open_manage = pyqtSignal(int)

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────
        header = QFrame()
        header.setObjectName("header")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(0, 0, 16, 0)

        title_wrap = QVBoxLayout()
        title_wrap.setSpacing(0)
        title_wrap.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Nextask")
        title.setObjectName("app-title")
        sub   = QLabel("Select a task to begin")
        sub.setObjectName("header-subtitle")
        title_wrap.addWidget(title)
        title_wrap.addWidget(sub)

        manage_btn = QPushButton("＋ New Task")
        manage_btn.setObjectName("btn-header")
        manage_btn.setFixedHeight(34)
        manage_btn.clicked.connect(lambda: self.sig_open_manage.emit(-1))

        hl.addLayout(title_wrap)
        hl.addStretch()
        hl.addWidget(manage_btn)
        root.addWidget(header)

        # ── Scroll area for cards ──────────────
        self._scroll = QScrollArea()
        self._scroll.setObjectName("task-scroll")
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._cards_widget = QWidget()
        self._cards_widget.setObjectName("task-scroll-content")
        self._cards_layout = QVBoxLayout(self._cards_widget)
        self._cards_layout.setContentsMargins(20, 20, 20, 20)
        self._cards_layout.setSpacing(10)

        self._scroll.setWidget(self._cards_widget)
        root.addWidget(self._scroll)

    def refresh(self):
        # Clear cards
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tasks = self.db.get_all_tasks()

        if not tasks:
            empty = QLabel("You have no tasks yet.\n\nTap '＋ New Task' to get started.")
            empty.setObjectName("empty-hint")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setContentsMargins(0, 80, 0, 0)
            self._cards_layout.addWidget(empty)
            self._cards_layout.addStretch()
            return

        for task in tasks:
            done, total = self.db.get_progress(task["id"])
            card = TaskCard(task, done, total)
            card.sig_open.connect(self._on_open_task)
            card.sig_manage.connect(lambda tid=task["id"]: self.sig_open_manage.emit(tid))
            self._cards_layout.addWidget(card)

        self._cards_layout.addStretch()

    def _on_open_task(self, task_id: int):
        done, total = self.db.get_progress(task_id)
        if total == 0:
            QMessageBox.information(self, "Empty task",
                "This task has no items.\nTap ··· to add items first.")
            return
        if done == total:
            QMessageBox.information(self, "All done! 🎉",
                "Every item in this task is complete.\nEdit the task to add more.")
            return
        self.sig_open_task.emit(task_id)


class TaskCard(QFrame):
    """Card widget representing one task in the list."""

    sig_open   = pyqtSignal(int)
    sig_manage = pyqtSignal(int)

    def __init__(self, task, done: int, total: int, parent=None):
        super().__init__(parent)
        self._task_id = task["id"]
        self.setObjectName("task-card")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._build_ui(task, done, total)

    def _build_ui(self, task, done: int, total: int):
        pct = int((done / total) * 100) if total > 0 else 0

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 18, 20, 18)
        outer.setSpacing(12)

        # Top row: name + manage button
        top = QHBoxLayout()
        top.setSpacing(8)

        name_lbl = QLabel(task["name"])
        name_lbl.setObjectName("task-card-name")
        name_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        top.addWidget(name_lbl)

        mgr_btn = QPushButton("···")
        mgr_btn.setObjectName("btn-action")
        mgr_btn.setFixedSize(36, 28)
        mgr_btn.setToolTip("Edit task")
        mgr_btn.clicked.connect(lambda: self.sig_manage.emit(self._task_id))
        top.addWidget(mgr_btn)

        outer.addLayout(top)

        # Progress bar
        bar = QProgressBar()
        bar.setValue(pct)
        bar.setTextVisible(False)
        bar.setFixedHeight(5)
        outer.addWidget(bar)

        # Bottom row: meta + percentage
        bottom = QHBoxLayout()

        if total == 0:
            meta_text = "No items yet"
        elif done == total:
            meta_text = "All done ✓"
        else:
            meta_text = f"{done} of {total} complete"

        meta_lbl = QLabel(meta_text)
        meta_lbl.setObjectName("task-card-meta")
        bottom.addWidget(meta_lbl)
        bottom.addStretch()

        pct_lbl = QLabel(f"{pct}%")
        pct_lbl.setObjectName("task-card-pct")
        bottom.addWidget(pct_lbl)

        outer.addLayout(bottom)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.sig_open.emit(self._task_id)
        super().mousePressEvent(event)


# ══════════════════════════════════════════════
# SCREEN 2 — EXECUTION
# ══════════════════════════════════════════════

class ExecutionScreen(QWidget):

    sig_back = pyqtSignal()

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db            = db
        self._task_id      = None
        self._current_item = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────
        header = QFrame()
        header.setObjectName("header")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(8, 0, 20, 0)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("btn-back")
        back_btn.setFixedWidth(90)
        back_btn.clicked.connect(self.sig_back.emit)
        hl.addWidget(back_btn)
        hl.addStretch()

        self._header_task_name = QLabel("")
        self._header_task_name.setObjectName("screen-title")
        self._header_task_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Override screen-title for this use
        self._header_task_name.setStyleSheet(
            f"font-size: 15px; font-weight: 600; color: {C_TEXT};"
        )
        hl.addWidget(self._header_task_name)
        hl.addStretch()

        # placeholder to balance back button
        hl.addSpacing(90)
        root.addWidget(header)

        # ── Progress strip ─────────────────────
        self._progress_strip = QProgressBar()
        self._progress_strip.setObjectName("progress-strip")
        self._progress_strip.setTextVisible(False)
        root.addWidget(self._progress_strip)

        # ── Main content (centred) ─────────────
        content = QWidget()
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        cl = QVBoxLayout(content)
        cl.setContentsMargins(32, 0, 32, 32)
        cl.setSpacing(0)

        # Progress percentage — large and centred
        cl.addSpacing(32)
        self._pct_label = QLabel("0%")
        self._pct_label.setObjectName("exec-pct")
        self._pct_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self._pct_label)

        self._pct_sub = QLabel("complete")
        self._pct_sub.setObjectName("exec-pct-label")
        self._pct_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self._pct_sub)

        cl.addSpacing(36)

        # Task label (small caps above item)
        self._task_label = QLabel("")
        self._task_label.setObjectName("exec-task-name")
        self._task_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        cl.addWidget(self._task_label)
        cl.addSpacing(8)

        # Item card — the focal point of the screen
        self._item_card = QFrame()
        self._item_card.setObjectName("exec-card")
        ic_layout = QVBoxLayout(self._item_card)
        ic_layout.setContentsMargins(28, 28, 28, 28)

        self._item_text = QLabel("")
        self._item_text.setObjectName("exec-item-text")
        self._item_text.setWordWrap(True)
        self._item_text.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._item_text.setMinimumHeight(80)
        ic_layout.addWidget(self._item_text)

        cl.addWidget(self._item_card)

        # All-done state (hidden by default)
        self._done_card = QFrame()
        self._done_card.setObjectName("exec-card")
        dc_layout = QVBoxLayout(self._done_card)
        dc_layout.setContentsMargins(28, 40, 28, 40)
        dc_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        done_icon = QLabel("✓")
        done_icon.setStyleSheet(f"font-size: 40px; color: {C_ACCENT};")
        done_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dc_layout.addWidget(done_icon)
        dc_layout.addSpacing(12)

        done_title = QLabel("All done!")
        done_title.setObjectName("exec-done-title")
        done_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dc_layout.addWidget(done_title)

        done_sub = QLabel("Every item in this task is complete.")
        done_sub.setObjectName("exec-done-sub")
        done_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dc_layout.addWidget(done_sub)

        self._done_card.hide()
        cl.addWidget(self._done_card)

        cl.addStretch()

        # ── Action buttons ─────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self._skip_btn = QPushButton("Skip for now")
        self._skip_btn.setObjectName("btn-skip")
        self._skip_btn.clicked.connect(self._on_skip)

        self._complete_btn = QPushButton("Mark Complete")
        self._complete_btn.clicked.connect(self._on_complete)

        btn_row.addWidget(self._skip_btn, 1)
        btn_row.addWidget(self._complete_btn, 2)
        cl.addLayout(btn_row)

        root.addWidget(content)

    def load_task(self, task_id: int):
        self._task_id = task_id
        task = self.db.get_task(task_id)
        name = task["name"] if task else ""
        self._header_task_name.setText(name)
        self._task_label.setText(name.upper())
        self._refresh()

    def _refresh(self):
        if self._task_id is None:
            return
        self._current_item = self.db.get_current_item(self._task_id)
        done, total = self.db.get_progress(self._task_id)
        pct = int((done / total) * 100) if total > 0 else 0

        self._progress_strip.setValue(pct)
        self._pct_label.setText(f"{pct}%")

        if self._current_item is None:
            self._item_card.hide()
            self._done_card.show()
            self._pct_label.setText("100%")
            self._complete_btn.setEnabled(False)
            self._skip_btn.setEnabled(False)
        else:
            self._done_card.hide()
            self._item_card.show()
            self._item_text.setText(self._current_item["text"])
            self._complete_btn.setEnabled(True)
            self._skip_btn.setEnabled(True)

    def _on_complete(self):
        if self._current_item:
            self.db.complete_item(self._current_item["id"])
            self._refresh()

    def _on_skip(self):
        if self._current_item:
            self.db.skip_item(self._current_item["id"], self._task_id)
            self._refresh()


# ══════════════════════════════════════════════
# SCREEN 3 — MANAGE (tabbed)
# ══════════════════════════════════════════════

class ManageScreen(QWidget):
    """
    Two tabs:
      Tasks  — list of all tasks, create/delete
      Items  — items within the selected task, add/edit/reorder/delete
    """

    sig_back = pyqtSignal()

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db            = db
        self._active_task_id = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────
        header = QFrame()
        header.setObjectName("header")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(8, 0, 20, 0)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("btn-back")
        back_btn.setFixedWidth(90)
        back_btn.clicked.connect(self._on_back)
        hl.addWidget(back_btn)
        hl.addStretch()

        self._header_lbl = QLabel("Manage")
        self._header_lbl.setStyleSheet(
            f"font-size: 15px; font-weight: 600; color: {C_TEXT};"
        )
        hl.addWidget(self._header_lbl)
        hl.addStretch()
        hl.addSpacing(90)
        root.addWidget(header)

        # ── Tab bar ────────────────────────────
        tab_bar = QFrame()
        tab_bar.setObjectName("tab-bar")
        tl = QHBoxLayout(tab_bar)
        tl.setContentsMargins(16, 0, 16, 0)
        tl.setSpacing(0)

        self._tab_tasks = QPushButton("Tasks")
        self._tab_tasks.setObjectName("tab-btn-active")
        self._tab_tasks.clicked.connect(lambda: self._switch_tab(0))

        self._tab_items = QPushButton("Items")
        self._tab_items.setObjectName("tab-btn")
        self._tab_items.clicked.connect(lambda: self._switch_tab(1))

        tl.addWidget(self._tab_tasks)
        tl.addWidget(self._tab_items)
        tl.addStretch()
        root.addWidget(tab_bar)

        # ── Tab pages ──────────────────────────
        self._tab_stack = QStackedWidget()
        self._tab_stack.addWidget(self._build_tasks_tab())   # 0
        self._tab_stack.addWidget(self._build_items_tab())   # 1
        root.addWidget(self._tab_stack)

    # ── Tab switching ──────────────────────────

    def _switch_tab(self, idx: int):
        self._tab_stack.setCurrentIndex(idx)
        if idx == 0:
            self._tab_tasks.setObjectName("tab-btn-active")
            self._tab_items.setObjectName("tab-btn")
        else:
            self._tab_tasks.setObjectName("tab-btn")
            self._tab_items.setObjectName("tab-btn-active")
        # Force style refresh
        self._tab_tasks.style().unpolish(self._tab_tasks)
        self._tab_tasks.style().polish(self._tab_tasks)
        self._tab_items.style().unpolish(self._tab_items)
        self._tab_items.style().polish(self._tab_items)

        if idx == 1:
            self._refresh_items_tab()

    # ══════════════════════════════════════════
    # TASKS TAB
    # ══════════════════════════════════════════

    def _build_tasks_tab(self) -> QWidget:
        page = QWidget()
        pl   = QVBoxLayout(page)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(0)

        # Create new task section
        create_section = QWidget()
        create_section.setStyleSheet(f"background: {C_SURFACE};")
        cl = QVBoxLayout(create_section)
        cl.setContentsMargins(24, 20, 24, 20)
        cl.setSpacing(10)

        create_lbl = QLabel("NEW TASK")
        create_lbl.setObjectName("section-header")
        cl.addWidget(create_lbl)

        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        self._new_task_input = QLineEdit()
        self._new_task_input.setPlaceholderText("Enter task name…")
        self._new_task_input.returnPressed.connect(self._on_create_task)
        input_row.addWidget(self._new_task_input)

        create_btn = QPushButton("Create")
        create_btn.setFixedWidth(90)
        create_btn.setFixedHeight(42)
        create_btn.clicked.connect(self._on_create_task)
        input_row.addWidget(create_btn)
        cl.addLayout(input_row)

        pl.addWidget(create_section)
        pl.addWidget(hline())

        # Existing tasks list
        lbl_wrap = QWidget()
        lbl_wrap.setStyleSheet(f"background: {C_BG};")
        lw = QVBoxLayout(lbl_wrap)
        lw.setContentsMargins(24, 16, 24, 8)
        all_tasks_lbl = QLabel("ALL TASKS")
        all_tasks_lbl.setObjectName("section-header")
        lw.addWidget(all_tasks_lbl)
        pl.addWidget(lbl_wrap)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background: {C_BG};")

        self._tasks_list_widget = QWidget()
        self._tasks_list_widget.setStyleSheet(f"background: {C_BG};")
        self._tasks_list_layout = QVBoxLayout(self._tasks_list_widget)
        self._tasks_list_layout.setContentsMargins(20, 4, 20, 20)
        self._tasks_list_layout.setSpacing(8)

        scroll.setWidget(self._tasks_list_widget)
        pl.addWidget(scroll)

        return page

    def _refresh_tasks_tab(self):
        while self._tasks_list_layout.count():
            item = self._tasks_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tasks = self.db.get_all_tasks()

        if not tasks:
            lbl = QLabel("No tasks yet. Create one above.")
            lbl.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 13px; padding: 20px 0;")
            self._tasks_list_layout.addWidget(lbl)
        else:
            for task in tasks:
                done, total = self.db.get_progress(task["id"])
                row = ManageTaskRow(task, done, total)
                row.sig_edit.connect(self._on_edit_task)
                row.sig_delete.connect(self._on_delete_task)
                row.sig_open_items.connect(self._on_open_items)
                self._tasks_list_layout.addWidget(row)

        self._tasks_list_layout.addStretch()

    def _on_create_task(self):
        name = self._new_task_input.text().strip()
        if not name:
            self._new_task_input.setFocus()
            return
        task_id = self.db.add_task(name)
        self._new_task_input.clear()
        self._refresh_tasks_tab()

    def _on_edit_task(self, task_id: int, current_name: str):
        text, ok = QInputDialog.getText(
            self, "Rename task", "Task name:", text=current_name
        )
        if ok and text.strip():
            self.db.update_task_name(task_id, text.strip())
            self._refresh_tasks_tab()

    def _on_delete_task(self, task_id: int, name: str):
        reply = QMessageBox.question(
            self, "Delete task",
            f"Delete '{name}' and all its items?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_task(task_id)
            if self._active_task_id == task_id:
                self._active_task_id = None
            self._refresh_tasks_tab()

    def _on_open_items(self, task_id: int):
        self._active_task_id = task_id
        task = self.db.get_task(task_id)
        if task:
            self._header_lbl.setText(f"Items — {task['name']}")
        self._switch_tab(1)

    # ══════════════════════════════════════════
    # ITEMS TAB
    # ══════════════════════════════════════════

    def _build_items_tab(self) -> QWidget:
        page = QWidget()
        pl   = QVBoxLayout(page)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(0)

        # No task selected state
        self._no_task_lbl = QLabel("Select a task from the Tasks tab first.")
        self._no_task_lbl.setStyleSheet(
            f"color: {C_TEXT_MUTED}; font-size: 14px; padding: 40px;"
        )
        self._no_task_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pl.addWidget(self._no_task_lbl)

        # Add items section
        self._add_section = QWidget()
        self._add_section.setStyleSheet(f"background: {C_SURFACE};")
        al = QVBoxLayout(self._add_section)
        al.setContentsMargins(24, 20, 24, 20)
        al.setSpacing(12)

        # Manual add
        manual_lbl = QLabel("ADD ITEMS")
        manual_lbl.setObjectName("section-header")
        al.addWidget(manual_lbl)

        manual_row = QHBoxLayout()
        manual_row.setSpacing(10)
        self._manual_input = QLineEdit()
        self._manual_input.setPlaceholderText("Type an item and press Enter…")
        self._manual_input.returnPressed.connect(self._on_manual_add)
        manual_row.addWidget(self._manual_input)
        add_one_btn = QPushButton("Add")
        add_one_btn.setFixedWidth(70)
        add_one_btn.setFixedHeight(42)
        add_one_btn.clicked.connect(self._on_manual_add)
        manual_row.addWidget(add_one_btn)
        al.addLayout(manual_row)

        # Bulk add (collapsible feel via toggle)
        bulk_toggle = QPushButton("＋ Bulk add (paste multiple items)")
        bulk_toggle.setObjectName("btn-ghost")
        bulk_toggle.setStyleSheet(
            f"color: {C_ACCENT}; font-size: 13px; text-align: left; padding: 0;"
            "background: transparent; border: none; min-height: 28px;"
        )
        al.addWidget(bulk_toggle)

        self._bulk_wrap = QWidget()
        bwl = QVBoxLayout(self._bulk_wrap)
        bwl.setContentsMargins(0, 0, 0, 0)
        bwl.setSpacing(8)
        self._bulk_input = QPlainTextEdit()
        self._bulk_input.setPlaceholderText(
            "Paste or type items here\nOne item per line\nOrder will be preserved"
        )
        self._bulk_input.setFixedHeight(100)
        bwl.addWidget(self._bulk_input)
        bulk_add_btn = QPushButton("Add All Lines")
        bulk_add_btn.setObjectName("btn-secondary")
        bulk_add_btn.clicked.connect(self._on_bulk_add)
        bwl.addWidget(bulk_add_btn)
        self._bulk_wrap.hide()
        al.addWidget(self._bulk_wrap)

        bulk_toggle.clicked.connect(
            lambda: self._bulk_wrap.setVisible(not self._bulk_wrap.isVisible())
        )

        pl.addWidget(self._add_section)
        self._add_section.hide()
        pl.addWidget(hline())

        # Items list
        self._items_scroll = QScrollArea()
        self._items_scroll.setWidgetResizable(True)
        self._items_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._items_scroll.setStyleSheet(f"background: {C_BG};")
        self._items_scroll.hide()

        self._items_list_widget = QWidget()
        self._items_list_widget.setStyleSheet(f"background: {C_BG};")
        self._items_list_layout = QVBoxLayout(self._items_list_widget)
        self._items_list_layout.setContentsMargins(20, 16, 20, 20)
        self._items_list_layout.setSpacing(8)

        self._items_scroll.setWidget(self._items_list_widget)
        pl.addWidget(self._items_scroll)

        return page

    def _refresh_items_tab(self):
        if self._active_task_id is None:
            self._no_task_lbl.show()
            self._add_section.hide()
            self._items_scroll.hide()
            return

        self._no_task_lbl.hide()
        self._add_section.show()
        self._items_scroll.show()

        # Clear
        while self._items_list_layout.count():
            child = self._items_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        items = self.db.get_items(self._active_task_id)

        if not items:
            lbl = QLabel("No items yet. Add some above.")
            lbl.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 13px; padding: 16px 0;")
            self._items_list_layout.addWidget(lbl)
        else:
            # Section header
            items_hdr = QLabel(f"ITEMS  ({len(items)})")
            items_hdr.setObjectName("section-header")
            self._items_list_layout.addWidget(items_hdr)
            self._items_list_layout.addSpacing(4)

            for idx, item in enumerate(items):
                row = ManageItemRow(item, idx + 1, len(items), self.db,
                                    self._refresh_items_tab)
                self._items_list_layout.addWidget(row)

        self._items_list_layout.addStretch()

    def _on_manual_add(self):
        if self._active_task_id is None:
            return
        text = self._manual_input.text().strip()
        if not text:
            return
        self.db.add_item(self._active_task_id, text)
        self._manual_input.clear()
        self._manual_input.setFocus()
        self._refresh_items_tab()

    def _on_bulk_add(self):
        if self._active_task_id is None:
            return
        text  = self._bulk_input.toPlainText()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not lines:
            return
        self.db.add_items_bulk(self._active_task_id, lines)
        self._bulk_input.clear()
        self._bulk_wrap.hide()
        self._refresh_items_tab()

    # ── Load / back ───────────────────────────

    def load(self, task_id: int):
        if task_id == -1:
            self._active_task_id = None
            self._header_lbl.setText("Manage")
            self._switch_tab(0)
        else:
            self._active_task_id = task_id
            task = self.db.get_task(task_id)
            if task:
                self._header_lbl.setText(f"Items — {task['name']}")
            self._switch_tab(1)
        self._refresh_tasks_tab()

    def _on_back(self):
        self._header_lbl.setText("Manage")
        self.sig_back.emit()


# ── Manage task row ────────────────────────────

class ManageTaskRow(QFrame):

    sig_edit       = pyqtSignal(int, str)
    sig_delete     = pyqtSignal(int, str)
    sig_open_items = pyqtSignal(int)

    def __init__(self, task, done: int, total: int, parent=None):
        super().__init__(parent)
        self._task_id   = task["id"]
        self._task_name = task["name"]
        self.setObjectName("manage-task-card")
        self._build_ui(task, done, total)

    def _build_ui(self, task, done: int, total: int):
        pct = int((done / total) * 100) if total > 0 else 0
        outer = QHBoxLayout(self)
        outer.setContentsMargins(16, 14, 12, 14)
        outer.setSpacing(12)

        # Left: name + progress
        left = QVBoxLayout()
        left.setSpacing(4)
        name_lbl = QLabel(task["name"])
        name_lbl.setObjectName("manage-task-name")
        left.addWidget(name_lbl)

        sub_lbl = QLabel(f"{done}/{total} items · {pct}%")
        sub_lbl.setObjectName("manage-task-sub")
        left.addWidget(sub_lbl)
        outer.addLayout(left, 1)

        # Right: action buttons
        items_btn = QPushButton("Items →")
        items_btn.setObjectName("btn-action")
        items_btn.setFixedHeight(30)
        items_btn.clicked.connect(lambda: self.sig_open_items.emit(self._task_id))

        edit_btn = QPushButton("Rename")
        edit_btn.setObjectName("btn-action")
        edit_btn.setFixedHeight(30)
        edit_btn.clicked.connect(
            lambda: self.sig_edit.emit(self._task_id, self._task_name)
        )

        del_btn = QPushButton("Delete")
        del_btn.setObjectName("btn-action")
        del_btn.setFixedHeight(30)
        del_btn.setStyleSheet(f"color: {C_DANGER}; border-color: #edcfcc;")
        del_btn.clicked.connect(
            lambda: self.sig_delete.emit(self._task_id, self._task_name)
        )

        outer.addWidget(items_btn)
        outer.addWidget(edit_btn)
        outer.addWidget(del_btn)


# ── Manage item row ────────────────────────────

class ManageItemRow(QFrame):
    """One item row in the items tab — position, text, reorder, edit, delete."""

    def __init__(self, item, position: int, total: int, db: Database,
                 refresh_fn, parent=None):
        super().__init__(parent)
        self._item    = item
        self._pos     = position
        self._total   = total
        self.db       = db
        self._refresh = refresh_fn
        self.setObjectName("item-card")
        self._build_ui()

    def _build_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(14, 12, 12, 12)
        outer.setSpacing(10)

        # Position number
        pos_lbl = QLabel(str(self._pos))
        pos_lbl.setObjectName("item-position")
        pos_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(pos_lbl)

        # Status dot
        if self._item["completed"]:
            dot = QLabel("✓")
            dot.setStyleSheet(f"color: {C_ACCENT}; font-size: 14px; font-weight: 600;")
        elif self._item["skipped"]:
            dot = QLabel("↷")
            dot.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 14px;")
        else:
            dot = QLabel("·")
            dot.setStyleSheet(f"color: {C_TEXT_MUTED}; font-size: 18px;")
        dot.setFixedWidth(18)
        outer.addWidget(dot)

        # Item text
        key = "item-card-text-done" if self._item["completed"] else "item-card-text"
        text_lbl = QLabel(self._item["text"])
        text_lbl.setObjectName(key)
        text_lbl.setWordWrap(True)
        text_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        outer.addWidget(text_lbl, 1)

        # Action buttons
        if self._pos > 1:
            up_btn = QPushButton("↑")
            up_btn.setObjectName("btn-action")
            up_btn.setFixedSize(28, 28)
            up_btn.clicked.connect(self._move_up)
            outer.addWidget(up_btn)

        if self._pos < self._total:
            dn_btn = QPushButton("↓")
            dn_btn.setObjectName("btn-action")
            dn_btn.setFixedSize(28, 28)
            dn_btn.clicked.connect(self._move_down)
            outer.addWidget(dn_btn)

        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("btn-action")
        edit_btn.setFixedHeight(28)
        edit_btn.clicked.connect(self._edit)
        outer.addWidget(edit_btn)

        del_btn = QPushButton("✕")
        del_btn.setObjectName("btn-action")
        del_btn.setFixedSize(28, 28)
        del_btn.setStyleSheet(f"color: {C_DANGER};")
        del_btn.clicked.connect(self._delete)
        outer.addWidget(del_btn)

    def _move_up(self):
        items = self.db.get_items(self._item["task_id"])
        ids   = [i["id"] for i in items]
        idx   = ids.index(self._item["id"])
        if idx > 0:
            ids[idx], ids[idx-1] = ids[idx-1], ids[idx]
            self.db.reorder_items(ids)
            self._refresh()

    def _move_down(self):
        items = self.db.get_items(self._item["task_id"])
        ids   = [i["id"] for i in items]
        idx   = ids.index(self._item["id"])
        if idx < len(ids)-1:
            ids[idx], ids[idx+1] = ids[idx+1], ids[idx]
            self.db.reorder_items(ids)
            self._refresh()

    def _edit(self):
        text, ok = QInputDialog.getText(
            self, "Edit item", "Item text:", text=self._item["text"]
        )
        if ok and text.strip():
            self.db.update_item_text(self._item["id"], text.strip())
            self._refresh()

    def _delete(self):
        reply = QMessageBox.question(
            self, "Delete item",
            f"Delete this item?\n\n{self._item['text']}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_item(self._item["id"])
            self._refresh()


# Need QStackedWidget imported
from PyQt6.QtWidgets import QStackedWidget