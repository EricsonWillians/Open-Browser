"""
Minimal, elegant navigation bar with refined design.
"""

from __future__ import annotations

from pathlib import Path
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QPainter, QPaintEvent
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSizePolicy,
)

from open_browser.widgets.address_bar import AddressBar
from open_browser.theme import get_theme


class IconButton(QPushButton):
    """Clean icon button with minimal styling."""
    
    def __init__(self, icon_name: str, tooltip: str, icons_dir: Path, parent=None):
        super().__init__(parent)
        self.setToolTip(tooltip)
        self.setFixedSize(32, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Load icon
        icon_path = icons_dir / icon_name
        if icon_path.exists():
            self.setIcon(QIcon(str(icon_path)))
            self.setIconSize(QSize(14, 14))


class NavigationBar(QWidget):
    """
    Minimal navigation bar with superior contrast and clean design.
    """
    
    back_requested = pyqtSignal()
    forward_requested = pyqtSignal()
    reload_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    home_requested = pyqtSignal()
    navigate_requested = pyqtSignal(str)
    bookmark_requested = pyqtSignal()
    bookmarks_manager_requested = pyqtSignal()
    
    def __init__(self, icons_dir: Path | None = None, parent=None) -> None:
        super().__init__(parent)
        self._icons_dir = icons_dir or Path("GFX")
        self._is_loading: bool = False
        self._progress_value: int = 0
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Set up the minimal navigation bar."""
        self.setFixedHeight(48)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(2)
        
        # Navigation buttons
        self._back_button = IconButton("back.png", "Back (Alt+Left)", self._icons_dir)
        self._forward_button = IconButton("forward.png", "Forward (Alt+Right)", self._icons_dir)
        self._reload_button = IconButton("refresh.png", "Reload (F5)", self._icons_dir)
        
        layout.addWidget(self._back_button)
        layout.addWidget(self._forward_button)
        layout.addWidget(self._reload_button)
        
        # Spacer
        layout.addSpacing(8)
        
        # Home button
        self._home_button = IconButton("google.png", "Home", self._icons_dir)
        layout.addWidget(self._home_button)
        
        # Larger spacer before address bar
        layout.addSpacing(12)
        
        # Address bar - the centerpiece
        self._address_bar = AddressBar(self)
        self._address_bar.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self._address_bar, stretch=1)
        
        # Spacer after address bar
        layout.addSpacing(12)
        
        # Bookmark buttons
        self._bookmark_button = IconButton("star.png", "Bookmark (Ctrl+D)", self._icons_dir)
        self._bookmark_button.setCheckable(True)
        
        self._bookmarks_manager_button = IconButton("fav.png", "Bookmarks", self._icons_dir)
        
        layout.addWidget(self._bookmark_button)
        layout.addWidget(self._bookmarks_manager_button)
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """Custom paint for progress indicator."""
        super().paintEvent(event)
        
        if self._is_loading and self._progress_value > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            c = get_theme().colors
            
            # Draw thin progress line at bottom
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(c.accent))
            progress_width = int(self.width() * (self._progress_value / 100))
            painter.drawRect(0, self.height() - 2, progress_width, 2)
            
            painter.end()
    
    def _connect_signals(self) -> None:
        """Connect button signals."""
        self._back_button.clicked.connect(self.back_requested)
        self._forward_button.clicked.connect(self.forward_requested)
        self._reload_button.clicked.connect(self._on_reload_clicked)
        self._home_button.clicked.connect(self.home_requested)
        self._address_bar.navigate_requested.connect(self.navigate_requested)
        self._bookmark_button.clicked.connect(self.bookmark_requested)
        self._bookmarks_manager_button.clicked.connect(self.bookmarks_manager_requested)
    
    def _on_reload_clicked(self) -> None:
        """Handle reload/stop button click."""
        if self._is_loading:
            self.stop_requested.emit()
        else:
            self.reload_requested.emit()
    
    def set_url(self, url: str) -> None:
        """Set the address bar text."""
        self._address_bar.set_url(url)
    
    def get_url(self) -> str:
        """Get the current URL from the address bar."""
        return self._address_bar.text()
    
    def set_loading(self, loading: bool, progress: int = 0) -> None:
        """Update UI for loading state."""
        self._is_loading = loading
        self._progress_value = progress
        
        # Update reload button icon
        icon_name = "removestar.png" if loading else "refresh.png"
        icon_path = self._icons_dir / icon_name
        if icon_path.exists():
            self._reload_button.setIcon(QIcon(str(icon_path)))
        
        self._reload_button.setToolTip("Stop (Esc)" if loading else "Reload (F5)")
        self.update()  # Trigger repaint for progress
    
    def set_can_go_back(self, can_go: bool) -> None:
        """Update back button state."""
        self._back_button.setEnabled(can_go)
    
    def set_can_go_forward(self, can_go: bool) -> None:
        """Update forward button state."""
        self._forward_button.setEnabled(can_go)
    
    def set_bookmarked(self, bookmarked: bool) -> None:
        """Update bookmark button state."""
        self._bookmark_button.setChecked(bookmarked)
        
        icon_name = "removestar.png" if bookmarked else "star.png"
        icon_path = self._icons_dir / icon_name
        if icon_path.exists():
            self._bookmark_button.setIcon(QIcon(str(icon_path)))
        
        self._bookmark_button.setToolTip(
            "Remove bookmark" if bookmarked else "Bookmark (Ctrl+D)"
        )
    
    def focus_address_bar(self) -> None:
        """Focus and select the address bar."""
        self._address_bar.setFocus()
        self._address_bar.selectAll()
