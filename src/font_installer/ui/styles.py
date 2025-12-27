"""CSS styles for the TUI application."""

APP_CSS = """
Screen {
    background: #1a1b26;
}

/* Header styling */
Header {
    background: #7aa2f7;
    color: #1a1b26;
}

/* Welcome Panel */
#welcome-panel {
    width: 100%;
    height: 3;
    content-align: center middle;
    background: #24283b;
    color: #c0caf5;
    border: round #7aa2f7;
    margin: 1 2;
    text-style: bold;
}

/* Status bar */
#status-bar {
    width: 100%;
    height: 1;
    background: #1f2335;
    color: #565f89;
    padding: 0 2;
    margin: 0 2;
}

#status-bar.ok {
    color: #9ece6a;
}

#status-bar.error {
    color: #f7768e;
}

/* Dependencies Warning */
#deps-warning {
    background: #f7768e 20%;
    color: #f7768e;
    padding: 1 2;
    margin: 0 2 1 2;
    height: auto;
    border: solid #f7768e;
    display: none;
}

#deps-warning.visible {
    display: block;
}

/* Tabs Container */
#tabs-container {
    height: 1fr;
    min-height: 12;
    margin: 0 2;
    border: round #3b4261;
    background: #1f2335;
}

TabbedContent {
    height: 1fr;
}

/* Tab styling */
Tab {
    background: #24283b;
    color: #a9b1d6;
    padding: 0 2;
}

Tab:hover {
    background: #3b4261;
}

Tab.-active {
    background: #7aa2f7;
    color: #1a1b26;
    text-style: bold;
}

TabPane {
    height: 1fr;
    padding: 1;
    background: #1f2335;
}

VerticalScroll {
    height: 1fr;
    padding: 0 1;
    scrollbar-color: #3b4261;
    scrollbar-color-hover: #7aa2f7;
    scrollbar-color-active: #7aa2f7;
}

/* Category headers */
.category-header {
    padding: 0 0 1 0;
    color: #bb9af7;
    text-style: bold;
    border-bottom: solid #3b4261;
    margin-bottom: 1;
}

/* Font checkboxes */
.font-checkbox {
    margin: 0 0 1 1;
    height: auto;
    padding: 0;
    background: transparent;
}

.font-checkbox:focus {
    background: #24283b;
}

.font-checkbox > .toggle--label {
    color: #c0caf5;
}

/* Font descriptions */
.font-list {
    color: #565f89;
    margin: 0 0 1 3;
    padding: 0;
}

/* Info panel items */
.info-title {
    color: #bb9af7;
    text-style: bold;
    margin: 1 0;
}

.info-item {
    color: #a9b1d6;
}

.info-path {
    color: #9ece6a;
}

Rule {
    color: #3b4261;
    margin: 1 0;
}

/* Progress Container */
#progress-container {
    height: auto;
    padding: 1;
    margin: 1 2;
    background: #24283b;
    border: round #7aa2f7;
    display: none;
}

#progress-container.visible {
    display: block;
}

#progress-header {
    color: #7aa2f7;
    text-style: bold;
    text-align: center;
    margin-bottom: 1;
}

#progress-label {
    text-align: center;
    color: #c0caf5;
    height: 1;
}

#progress-bar {
    width: 100%;
    margin: 0 1;
    padding: 0 1;
}

#progress-bar > Bar {
    color: #9ece6a;
}

#progress-bar > .bar--bar {
    color: #9ece6a;
}

#progress-bar > PercentageStatus {
    color: #c0caf5;
    text-style: bold;
}

#installing-indicator {
    display: none;
    height: 1;
    color: #7aa2f7;
}

#installing-indicator.visible {
    display: block;
}

/* Log Container */
#log-container {
    height: 8;
    margin: 1 2;
    border: round #3b4261;
    background: #1f2335;
}

#log-header {
    background: #24283b;
    color: #7aa2f7;
    text-style: bold;
    padding: 0 1;
    height: 1;
    border-bottom: solid #3b4261;
}

#install-log {
    height: 100%;
    background: #1a1b26;
    padding: 0 1;
    scrollbar-color: #3b4261;
    scrollbar-color-hover: #7aa2f7;
}

/* Action Buttons */
#action-buttons {
    height: auto;
    width: 100%;
    align: center middle;
    padding: 1 0;
    background: transparent;
}

Button {
    margin: 0 1;
    min-width: 16;
    border: none;
}

Button:hover {
    opacity: 0.8;
}

#select-all-btn {
    background: #7aa2f7;
    color: #1a1b26;
}

#clear-btn {
    background: #e0af68;
    color: #1a1b26;
}

#install-btn {
    background: #9ece6a;
    color: #1a1b26;
}

#install-btn:disabled {
    background: #565f89;
    color: #1a1b26;
}

/* Footer */
Footer {
    background: #24283b;
    color: #a9b1d6;
}

Footer > .footer--key {
    background: #7aa2f7;
    color: #1a1b26;
}

Footer > .footer--description {
    color: #a9b1d6;
}

/* Scrollbar styling */
Scrollbar {
    scrollbar-size: 1 1;
}
"""
