"""
Refined browser tab with clean design.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QSizePolicy
)

from open_browser.models import TabState
from open_browser.widgets.web_view import WebEngineView
from open_browser.theme import get_theme

if TYPE_CHECKING:
    from PyQt6.QtGui import QCloseEvent


class BrowserTab(QWidget):
    """
    A single browser tab with clean, refined design.
    """
    
    # Signals
    title_changed = pyqtSignal(str)
    url_changed = pyqtSignal(str)
    load_started = pyqtSignal()
    load_progress = pyqtSignal(int)
    load_finished = pyqtSignal(bool)
    favicon_changed = pyqtSignal()
    new_tab_requested = pyqtSignal(QUrl)
    
    def __init__(self, url: str | None = None, parent=None) -> None:
        super().__init__(parent)
        self._state = TabState(url=url or "about:blank")
        self._title: str = "New Tab"
        self._is_loading: bool = False
        
        self._setup_ui()
        self._connect_signals()
        self._apply_theme()
        
        if url:
            self.load_url(url)
    
    def _setup_ui(self) -> None:
        """Set up the tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create web view
        self._web_view = WebEngineView(self)
        self._web_view.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        
        layout.addWidget(self._web_view)
    
    def _connect_signals(self) -> None:
        """Connect web view signals."""
        # Load events
        self._web_view.loadStarted.connect(self._on_load_started)
        self._web_view.loadProgress.connect(self._on_load_progress)
        self._web_view.loadFinished.connect(self._on_load_finished)
        
        # URL and title changes
        self._web_view.urlChanged.connect(self._on_url_changed)
        self._web_view.titleChanged.connect(self._on_title_changed)
        
        # New tab requests
        self._web_view.open_in_new_tab_requested.connect(self.new_tab_requested)
    
    def _apply_theme(self) -> None:
        """Apply current theme."""
        c = get_theme().colors
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c.bg_primary};
            }}
        """)
    
    def _on_load_started(self) -> None:
        """Handle page load start."""
        self._is_loading = True
        self.title_changed.emit("Loading...")
        self.load_started.emit()
    
    def _on_load_progress(self, progress: int) -> None:
        """Handle load progress updates."""
        self.load_progress.emit(progress)
    
    def _on_load_finished(self, success: bool) -> None:
        """Handle page load completion."""
        self._is_loading = False
        self.load_finished.emit(success)
        
        # Update title
        title = self._web_view.title() or self._state.url
        self._title = title
        self.title_changed.emit(title)
    
    def _on_url_changed(self, url: QUrl) -> None:
        """Handle URL changes."""
        url_str = url.toString()
        self._state.navigate_to(url_str)
        self.url_changed.emit(url_str)
    
    def _on_title_changed(self, title: str) -> None:
        """Handle page title changes."""
        if title and not self._is_loading:
            self._title = title
            self.title_changed.emit(title)
    
    # Public API
    
    def load_url(self, url: str) -> None:
        """Load a URL in this tab."""
        if not url.startswith(("http://", "https://", "file://", "data:", "about:")):
            url = f"https://{url}"
        
        self._web_view.load(QUrl(url))
    
    def reload(self) -> None:
        """Reload the current page."""
        self._web_view.reload()
    
    def stop(self) -> None:
        """Stop loading the current page."""
        self._web_view.stop()
    
    def back(self) -> bool:
        """Go back in history."""
        if self._web_view.history().canGoBack():
            self._web_view.back()
            return True
        return False
    
    def forward(self) -> bool:
        """Go forward in history."""
        if self._web_view.history().canGoForward():
            self._web_view.forward()
            return True
        return False
    
    def can_go_back(self) -> bool:
        """Check if we can go back."""
        return self._web_view.history().canGoBack()
    
    def can_go_forward(self) -> bool:
        """Check if we can go forward."""
        return self._web_view.history().canGoForward()
    
    def current_url(self) -> str:
        """Get the current URL."""
        return self._web_view.url().toString()
    
    def current_title(self) -> str:
        """Get the current page title."""
        return self._title
    
    def is_loading(self) -> bool:
        """Check if a page is currently loading."""
        return self._is_loading
    
    def get_state(self) -> TabState:
        """Get the tab state."""
        return self._state
    
    def closeEvent(self, event: "QCloseEvent") -> None:
        """Handle tab close event."""
        self._web_view.stop()
        self._web_view.deleteLater()
        super().closeEvent(event)
