"""
nextask/styles.py
Design system — calm, focused, professional.
Warm whites, generous space, clear hierarchy, soft depth.
"""

# ── Colour tokens ─────────────────────────────
C_BG          = "#f5f4f0"   # warm page background
C_SURFACE     = "#ffffff"   # card surface
C_SURFACE_2   = "#faf9f6"   # slightly off-white for nested areas
C_BORDER      = "#e8e3da"   # subtle warm border
C_BORDER_DARK = "#d4cfc5"   # slightly stronger border
C_TEXT        = "#1e1e1e"   # near-black primary text
C_TEXT_2      = "#4a4640"   # secondary text
C_TEXT_MUTED  = "#9a948c"   # placeholder / hint text
C_ACCENT      = "#3d7a57"   # forest green — calm, not loud
C_ACCENT_LT   = "#e8f4ed"   # green tint for hover/selected states
C_ACCENT_DARK = "#2f6244"   # deeper green for pressed states
C_DANGER      = "#c0392b"   # clear but not alarming red
C_DANGER_LT   = "#fdf1f0"   # light red bg
C_SKIP        = "#6b6560"   # neutral warm grey for skip
C_SKIP_LT     = "#f2efeb"   # light skip bg

STYLESHEET = f"""

/* ═══════════════════════════════════════════
   GLOBAL
═══════════════════════════════════════════ */
* {{
    font-family: "Inter", "SF Pro Text", "Segoe UI", "Ubuntu", sans-serif;
    font-size: 14px;
    color: {C_TEXT};
}}

QMainWindow, QWidget {{
    background-color: {C_BG};
}}

QStackedWidget {{
    background-color: {C_BG};
}}

QDialog {{
    background-color: {C_SURFACE};
}}

/* ═══════════════════════════════════════════
   HEADER BAR
═══════════════════════════════════════════ */
QFrame#header {{
    background-color: {C_SURFACE};
    border-bottom: 1px solid {C_BORDER};
    min-height: 60px;
    max-height: 60px;
}}

QLabel#app-title {{
    font-size: 20px;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: {C_TEXT};
    padding-left: 24px;
}}

QLabel#header-subtitle {{
    font-size: 12px;
    color: {C_TEXT_MUTED};
    padding-left: 24px;
    padding-bottom: 2px;
}}

/* ═══════════════════════════════════════════
   TASK LIST SCREEN
═══════════════════════════════════════════ */
QScrollArea#task-scroll {{
    border: none;
    background-color: {C_BG};
}}

QWidget#task-scroll-content {{
    background-color: {C_BG};
}}

/* Task cards are painted manually via TaskCardWidget */
QFrame#task-card {{
    background-color: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 12px;
}}

QFrame#task-card:hover {{
    border-color: {C_BORDER_DARK};
    background-color: #fdfcf9;
}}

QLabel#task-card-name {{
    font-size: 16px;
    font-weight: 600;
    color: {C_TEXT};
}}

QLabel#task-card-meta {{
    font-size: 12px;
    color: {C_TEXT_MUTED};
}}

QLabel#task-card-pct {{
    font-size: 13px;
    font-weight: 600;
    color: {C_ACCENT};
}}

QLabel#empty-hint {{
    font-size: 15px;
    color: {C_TEXT_MUTED};
    line-height: 2;
}}

/* ═══════════════════════════════════════════
   EXECUTION SCREEN
═══════════════════════════════════════════ */
QFrame#exec-card {{
    background-color: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 16px;
}}

QLabel#exec-task-name {{
    font-size: 13px;
    font-weight: 600;
    color: {C_TEXT_MUTED};
    letter-spacing: 0.5px;
}}

QLabel#exec-item-text {{
    font-size: 20px;
    font-weight: 400;
    color: {C_TEXT};
    line-height: 1.6;
}}

QLabel#exec-pct {{
    font-size: 28px;
    font-weight: 700;
    color: {C_ACCENT};
}}

QLabel#exec-pct-label {{
    font-size: 12px;
    color: {C_TEXT_MUTED};
}}

QLabel#exec-done-title {{
    font-size: 24px;
    font-weight: 700;
    color: {C_ACCENT};
}}

QLabel#exec-done-sub {{
    font-size: 14px;
    color: {C_TEXT_MUTED};
}}

/* ═══════════════════════════════════════════
   MANAGE SCREEN — TAB BAR
═══════════════════════════════════════════ */
QFrame#tab-bar {{
    background-color: {C_SURFACE};
    border-bottom: 1px solid {C_BORDER};
    min-height: 44px;
    max-height: 44px;
}}

QPushButton#tab-btn {{
    background-color: transparent;
    color: {C_TEXT_MUTED};
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0px;
    font-size: 13px;
    font-weight: 500;
    padding: 0px 20px;
    min-height: 44px;
}}

QPushButton#tab-btn:hover {{
    color: {C_TEXT};
    background-color: transparent;
}}

QPushButton#tab-btn-active {{
    background-color: transparent;
    color: {C_ACCENT};
    border: none;
    border-bottom: 2px solid {C_ACCENT};
    border-radius: 0px;
    font-size: 13px;
    font-weight: 600;
    padding: 0px 20px;
    min-height: 44px;
}}

/* ═══════════════════════════════════════════
   MANAGE SCREEN — TASK LIST TAB
═══════════════════════════════════════════ */
QFrame#manage-task-card {{
    background-color: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
}}

QLabel#manage-task-name {{
    font-size: 15px;
    font-weight: 600;
    color: {C_TEXT};
}}

QLabel#manage-task-sub {{
    font-size: 12px;
    color: {C_TEXT_MUTED};
}}

/* ═══════════════════════════════════════════
   MANAGE SCREEN — ITEMS TAB
═══════════════════════════════════════════ */
QFrame#item-card {{
    background-color: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
}}

QLabel#item-card-text {{
    font-size: 14px;
    color: {C_TEXT};
}}

QLabel#item-card-text-done {{
    font-size: 14px;
    color: {C_TEXT_MUTED};
    text-decoration: line-through;
}}

QLabel#item-position {{
    font-size: 12px;
    font-weight: 600;
    color: {C_TEXT_MUTED};
    min-width: 24px;
}}

/* ═══════════════════════════════════════════
   SECTION HEADERS
═══════════════════════════════════════════ */
QLabel#section-header {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.2px;
    color: {C_TEXT_MUTED};
    padding: 0 0 4px 0;
}}

/* ═══════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════ */

/* Primary */
QPushButton {{
    background-color: {C_ACCENT};
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 0px 24px;
    font-size: 14px;
    font-weight: 600;
    min-height: 42px;
}}
QPushButton:hover    {{ background-color: {C_ACCENT_DARK}; }}
QPushButton:pressed  {{ background-color: #255038; }}
QPushButton:disabled {{ background-color: {C_BORDER}; color: {C_TEXT_MUTED}; }}

/* Secondary — outlined */
QPushButton#btn-secondary {{
    background-color: {C_SURFACE};
    color: {C_TEXT_2};
    border: 1.5px solid {C_BORDER_DARK};
    min-height: 42px;
}}
QPushButton#btn-secondary:hover {{
    background-color: {C_SURFACE_2};
    border-color: #b8b2a8;
}}

/* Skip — warm neutral */
QPushButton#btn-skip {{
    background-color: {C_SKIP_LT};
    color: {C_SKIP};
    border: 1.5px solid {C_BORDER_DARK};
    min-height: 42px;
}}
QPushButton#btn-skip:hover {{
    background-color: #ebe7e2;
    color: {C_TEXT_2};
}}

/* Danger — warm red */
QPushButton#btn-danger {{
    background-color: {C_DANGER_LT};
    color: {C_DANGER};
    border: 1.5px solid #edcfcc;
    min-height: 38px;
}}
QPushButton#btn-danger:hover {{
    background-color: {C_DANGER};
    color: #ffffff;
    border-color: {C_DANGER};
}}

/* Ghost — no background */
QPushButton#btn-ghost {{
    background-color: transparent;
    color: {C_TEXT_MUTED};
    border: none;
    padding: 0px 10px;
    font-size: 13px;
    min-height: 32px;
    font-weight: 400;
}}
QPushButton#btn-ghost:hover {{
    color: {C_TEXT};
    background-color: {C_SURFACE_2};
    border-radius: 6px;
}}

/* Small icon action */
QPushButton#btn-action {{
    background-color: transparent;
    color: {C_TEXT_MUTED};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
    padding: 0px 8px;
    font-size: 13px;
    min-height: 30px;
    max-height: 30px;
    font-weight: 400;
}}
QPushButton#btn-action:hover {{
    background-color: {C_SURFACE_2};
    color: {C_TEXT};
    border-color: {C_BORDER_DARK};
}}

/* Manage header button */
QPushButton#btn-header {{
    background-color: {C_ACCENT_LT};
    color: {C_ACCENT};
    border: 1px solid #c2dece;
    border-radius: 7px;
    font-size: 13px;
    font-weight: 600;
    min-height: 34px;
    padding: 0px 16px;
}}
QPushButton#btn-header:hover {{
    background-color: #d8ecde;
}}

/* Back button */
QPushButton#btn-back {{
    background-color: transparent;
    color: {C_TEXT_MUTED};
    border: none;
    font-size: 14px;
    min-height: 36px;
    padding: 0px 16px;
    font-weight: 400;
    text-align: left;
}}
QPushButton#btn-back:hover {{
    color: {C_TEXT};
    background-color: {C_SURFACE_2};
    border-radius: 6px;
}}

/* ═══════════════════════════════════════════
   INPUTS
═══════════════════════════════════════════ */
QLineEdit {{
    background-color: {C_SURFACE};
    border: 1.5px solid {C_BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    color: {C_TEXT};
    min-height: 20px;
    selection-background-color: {C_ACCENT};
    selection-color: #ffffff;
}}
QLineEdit:focus {{
    border-color: {C_ACCENT};
}}

QPlainTextEdit, QTextEdit {{
    background-color: {C_SURFACE};
    border: 1.5px solid {C_BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    color: {C_TEXT};
    selection-background-color: {C_ACCENT};
    selection-color: #ffffff;
}}
QPlainTextEdit:focus, QTextEdit:focus {{
    border-color: {C_ACCENT};
}}

/* ═══════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════ */
QProgressBar {{
    background-color: {C_BORDER};
    border: none;
    border-radius: 3px;
    min-height: 5px;
    max-height: 5px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {C_ACCENT};
    border-radius: 3px;
}}

/* Full-width progress strip */
QProgressBar#progress-strip {{
    background-color: {C_BORDER};
    border: none;
    border-radius: 0px;
    min-height: 3px;
    max-height: 3px;
}}
QProgressBar#progress-strip::chunk {{
    background-color: {C_ACCENT};
    border-radius: 0px;
}}

/* ═══════════════════════════════════════════
   SCROLLBAR
═══════════════════════════════════════════ */
QScrollBar:vertical {{
    background: transparent;
    width: 5px;
    margin: 4px 0;
}}
QScrollBar::handle:vertical {{
    background: {C_BORDER_DARK};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: #b8b2a8;
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 0; }}

/* ═══════════════════════════════════════════
   MISCELLANEOUS
═══════════════════════════════════════════ */
QMessageBox {{
    background-color: {C_SURFACE};
}}

QInputDialog {{
    background-color: {C_SURFACE};
}}
"""