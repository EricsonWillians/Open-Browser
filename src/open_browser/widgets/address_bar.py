"""
Clean, minimal address bar with refined design.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFocusEvent, QKeyEvent
from PyQt6.QtWidgets import QLineEdit

from open_browser.utils import SearchUtils


class AddressBar(QLineEdit):
    """
    Clean address bar with minimal, elegant design.
    """
    
    navigate_requested = pyqtSignal(str)
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._current_url: str = ""
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Configure the clean address bar UI."""
        self.setPlaceholderText("Search or enter address")
        self.setClearButtonEnabled(True)
        self.setFixedHeight(36)
        self.setTextMargins(14, 0, 14, 0)
    
    def focusInEvent(self, event: QFocusEvent) -> None:
        """Handle focus - select all text."""
        super().focusInEvent(event)
        self.selectAll()
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events."""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._handle_navigation()
        elif event.key() == Qt.Key.Key_Escape:
            self.clearFocus()
            self.setText(self._current_url)
        else:
            super().keyPressEvent(event)
    
    def _handle_navigation(self) -> None:
        """Process the input and emit navigation request."""
        text = self.text().strip()
        if not text:
            return
        
        url = SearchUtils.process_input(text)
        self.navigate_requested.emit(url)
    
    def set_url(self, url: str) -> None:
        """Set the displayed URL."""
        self._current_url = url
        self.setText(url)
    
    def get_url(self) -> str:
        """Get the current URL."""
        return self._current_url
