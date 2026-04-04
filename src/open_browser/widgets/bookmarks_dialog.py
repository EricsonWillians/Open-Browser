"""
Elegant bookmarks dialog with modern design.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QWidget, QLineEdit, QFrame
)

from open_browser.models import Bookmark
from open_browser.storage import BookmarksManager
from open_browser.theme import get_theme


class BookmarkItemWidget(QWidget):
    """Custom widget for bookmark list items."""
    
    def __init__(self, bookmark: Bookmark, parent=None) -> None:
        super().__init__(parent)
        self.bookmark = bookmark
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the item widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        # Title
        self._title_label = QLabel(self.bookmark.title)
        self._title_label.setStyleSheet(f"""
            font-weight: 600;
            font-size: 14px;
            color: {get_theme().colors.text_primary};
        """)
        layout.addWidget(self._title_label)
        
        # URL
        self._url_label = QLabel(self._truncate_url(self.bookmark.url))
        self._url_label.setStyleSheet(f"""
            font-size: 12px;
            color: {get_theme().colors.text_secondary};
        """)
        layout.addWidget(self._url_label)
    
    def _truncate_url(self, url: str, max_len: int = 50) -> str:
        """Truncate URL for display."""
        if len(url) > max_len:
            return url[:max_len - 3] + "..."
        return url


class BookmarksDialog(QDialog):
    """
    Elegant dialog for managing bookmarks.
    """
    
    bookmark_selected = pyqtSignal(str)
    
    def __init__(
        self, 
        bookmarks_manager: BookmarksManager,
        parent=None
    ) -> None:
        super().__init__(parent)
        self._bookmarks_manager = bookmarks_manager
        
        self.setWindowTitle("Bookmarks")
        self.setMinimumSize(500, 600)
        self.setMaximumSize(600, 800)
        
        self._setup_ui()
        self._apply_theme()
        self._load_bookmarks()
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        title = QLabel("Bookmarks")
        title.setObjectName("title")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Manage your saved websites")
        subtitle.setObjectName("subtitle")
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # Search/filter
        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText("Search bookmarks...")
        self._search_box.textChanged.connect(self._filter_bookmarks)
        layout.addWidget(self._search_box)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {get_theme().colors.border};")
        divider.setFixedHeight(1)
        layout.addWidget(divider)
        
        # Bookmarks list
        self._list_widget = QListWidget(self)
        self._list_widget.setSpacing(4)
        self._list_widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self._list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list_widget.itemClicked.connect(self._on_item_clicked)
        self._list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._list_widget)
        
        # Empty state message
        self._empty_label = QLabel("No bookmarks yet")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(f"""
            color: {get_theme().colors.text_secondary};
            font-size: 14px;
            padding: 40px;
        """)
        layout.addWidget(self._empty_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self._open_button = QPushButton("Open")
        self._open_button.setObjectName("secondary")
        self._open_button.setEnabled(False)
        self._open_button.clicked.connect(self._on_open_clicked)
        
        self._delete_button = QPushButton("Delete")
        self._delete_button.setObjectName("danger")
        self._delete_button.setEnabled(False)
        self._delete_button.clicked.connect(self._on_delete_clicked)
        
        button_layout.addWidget(self._open_button)
        button_layout.addWidget(self._delete_button)
        button_layout.addStretch()
        
        self._close_button = QPushButton("Close")
        self._close_button.setObjectName("secondary")
        self._close_button.clicked.connect(self.close)
        button_layout.addWidget(self._close_button)
        
        layout.addLayout(button_layout)
    
    def _apply_theme(self) -> None:
        """Apply current theme."""
        theme = get_theme()
        c = theme.colors
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {c.bg_primary};
                border-radius: 16px;
            }}
            
            QLineEdit {{
                background-color: {c.bg_secondary};
                border: 2px solid {c.border};
                border-radius: 12px;
                padding: 12px 16px;
                color: {c.text_primary};
                font-size: 14px;
            }}
            
            QLineEdit:focus {{
                border-color: {c.accent};
            }}
            
            QListWidget {{
                background-color: {c.bg_secondary};
                border: 1px solid {c.border};
                border-radius: 16px;
                padding: 12px;
                outline: none;
            }}
            
            QListWidget::item {{
                background-color: transparent;
                border-radius: 12px;
                margin: 4px 0;
            }}
            
            QListWidget::item:selected {{
                background-color: {c.accent};
            }}
            
            QListWidget::item:hover:!selected {{
                background-color: {c.bg_hover};
            }}
        """)
    
    def _load_bookmarks(self) -> None:
        """Load bookmarks into the list."""
        self._list_widget.clear()
        bookmarks = self._bookmarks_manager.bookmarks
        
        if not bookmarks:
            self._list_widget.hide()
            self._empty_label.show()
        else:
            self._empty_label.hide()
            self._list_widget.show()
            
            for bookmark in bookmarks:
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, bookmark.url)
                item.setSizeHint(QSize(0, 70))
                
                widget = BookmarkItemWidget(bookmark)
                self._list_widget.addItem(item)
                self._list_widget.setItemWidget(item, widget)
        
        self.setWindowTitle(f"Bookmarks ({len(bookmarks)})")
    
    def _filter_bookmarks(self, text: str) -> None:
        """Filter bookmarks based on search text."""
        text = text.lower()
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            widget = self._list_widget.itemWidget(item)
            if widget:
                match = (text in widget.bookmark.title.lower() or 
                        text in widget.bookmark.url.lower())
                item.setHidden(not match)
    
    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """Handle item click."""
        self._open_button.setEnabled(True)
        self._delete_button.setEnabled(True)
    
    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click to open bookmark."""
        self._open_bookmark(item)
    
    def _on_open_clicked(self) -> None:
        """Handle open button click."""
        item = self._list_widget.currentItem()
        if item:
            self._open_bookmark(item)
    
    def _open_bookmark(self, item: QListWidgetItem) -> None:
        """Open the selected bookmark."""
        url = item.data(Qt.ItemDataRole.UserRole)
        self.bookmark_selected.emit(url)
        self.close()
    
    def _on_delete_clicked(self) -> None:
        """Handle delete button click."""
        item = self._list_widget.currentItem()
        if not item:
            return
        
        widget = self._list_widget.itemWidget(item)
        if not widget:
            return
        
        title = widget.bookmark.title
        
        # Simple confirmation (could be a custom dialog)
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Delete Bookmark",
            f'Are you sure you want to delete "{title}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._bookmarks_manager.remove(title)
            self._load_bookmarks()
            self._open_button.setEnabled(False)
            self._delete_button.setEnabled(False)
    
    def refresh(self) -> None:
        """Refresh the bookmarks list."""
        self._load_bookmarks()
