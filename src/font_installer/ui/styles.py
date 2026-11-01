"""Gruvbox Dark; compact catalog and stable activity surfaces."""

LOG_COLORS = {
    "red": "#fb4934",
    "green": "#b8bb26",
    "yellow": "#fabd2f",
    "blue": "#83a598",
    "cyan": "#8ec07c",
}

APP_CSS = """
Screen { background: #282828; color: #ebdbb2; }
#masthead { height: 1; background: #83a598; color: #282828; text-style: bold; padding: 0 2; }
#welcome-panel { height: 1; color: #d5c4a1; padding: 0 2; }
#status-bar { height: 1; color: #b8bb26; padding: 0 2; }
#status-bar.warning { color: #fabd2f; }
#selection-count { height: 1; color: #8ec07c; padding: 0 2; }
#catalog { height: 1fr; min-height: 12; padding: 0 1; }
#categories { height: 12; }
.category { width: 1fr; height: 12; border: round #665c54; padding: 0 1; margin: 0 1; }
.category-title { height: 1; color: #d3869b; text-style: bold; }
.font-checkbox { height: 1; min-height: 1; padding: 0; margin: 0; border: none; background: transparent; }
.font-checkbox:focus { background: #3c3836; text-style: bold; }
.font-checkbox.-on { color: #b8bb26; }
.font-names { height: 2; padding-left: 3; color: #d5c4a1; }
.package-note { height: 1; color: #a89984; }
#activity { height: 4; margin: 0 2; }
#progress-label { height: 1; color: #8ec07c; }
#progress-row { height: 1; }
#progress-bar { width: 1fr; height: 1; }
#installing-indicator { width: 6; height: 1; color: #8ec07c; }
#summary { height: 2; color: #ebdbb2; }
#log-container { height: 8; border: round #665c54; margin: 0 2; }
#log-heading { height: 1; background: #3c3836; }
#log-header { width: 1fr; height: 1; color: #83a598; }
#follow-btn { height: 1; min-height: 1; min-width: 8; border: none; padding: 0; }
#install-log { height: 1fr; padding: 0 1; }
#action-buttons { height: 3; align: center middle; }
Button { margin: 0 1; min-width: 12; background: #3c3836; color: #ebdbb2; }
Button:hover { background: #665c54; }
Button:focus { text-style: bold reverse; }
#install-btn { background: #b8bb26; color: #282828; }
Button:disabled { opacity: 0.5; }
Footer { height: 1; background: #3c3836; color: #d5c4a1; }
VerticalScroll, RichLog { scrollbar-color: #665c54; scrollbar-color-hover: #83a598; scrollbar-color-active: #8ec07c; }
.compact #categories { layout: vertical; height: 24; }
.compact .category { width: 100%; }
.compact #catalog { min-height: 4; }
.compact #action-buttons Button { min-width: 8; margin: 0; }
"""

MODAL_CSS = """
ModalScreen { align: center middle; background: #1d2021 80%; }
.dialog { width: 85%; max-width: 100; height: 85%; padding: 1 2; background: #282828; border: round #83a598; }
.dialog-title { height: 2; color: #fabd2f; text-style: bold; }
.dialog-content { height: 1fr; margin: 1 0; }
.dialog-actions { height: 3; align: right middle; }
.dialog-actions Button { margin-left: 1; }
.exit-dialog { height: 12; }
"""
