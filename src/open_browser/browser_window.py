"""
Main browser window with elegant design and modern UX.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QTabBar,
    QToolButton, QMessageBox
)

from open_browser.models import BrowserConfig
from open_browser.storage import BookmarksManager, ConfigManager
from open_browser.widgets import BrowserTab, NavigationBar, BookmarksDialog
from open_browser.theme import get_theme, Theme, ThemeMode
from open_browser.utils import LoggingMixin

if TYPE_CHECKING:
    from PyQt6.QtGui import QCloseEvent

logger = logging.getLogger(__name__)


class ElegantTabWidget(QTabWidget):
    """Custom tab widget with clean design."""
    
    add_tab_requested = pyqtSignal()
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the tab widget UI."""
        self.setTabShape(QTabWidget.TabShape.Rounded)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        
        # Add tab button
        self._add_button = QToolButton(self)
        self._add_button.setText("+")
        self._add_button.setToolTip("New Tab (Ctrl+T)")
        self._add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._add_button.clicked.connect(self.add_tab_requested)
        
        self.setCornerWidget(self._add_button, Qt.Corner.TopRightCorner)


class BrowserWindow(QMainWindow, LoggingMixin):
    """
    Main browser window with elegant design.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager | None = None,
        bookmarks_manager: BookmarksManager | None = None,
        icons_dir: Path | None = None,
    ) -> None:
        super().__init__()
        
        # Initialize managers
        self._config_manager = config_manager or ConfigManager()
        self._bookmarks_manager = bookmarks_manager or BookmarksManager()
        self._icons_dir = icons_dir or Path("GFX")
        self._config = self._config_manager.config
        
        # Window state
        self._bookmarks_dialog: BookmarksDialog | None = None
        self._theme = get_theme()
        
        self._setup_ui()
        self._setup_shortcuts()
        self._connect_signals()
        
        # Create initial tab
        self._add_new_tab(self._config.homepage)
        
        # Apply window settings
        self._apply_window_settings()
    
    def _setup_ui(self) -> None:
        """Set up the main window UI."""
        self.setWindowTitle("Open Browser")
        
        # Set window icon
        icon_path = self._icons_dir / "fav.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Navigation bar
        self._nav_bar = NavigationBar(self._icons_dir, self)
        layout.addWidget(self._nav_bar)
        
        # Tab widget
        self._tab_widget = ElegantTabWidget(self)
        layout.addWidget(self._tab_widget, stretch=1)
        
        # Apply theme
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        """Apply the current theme to the window."""
        self.setStyleSheet(self._theme.get_stylesheet())
        
        # Update all child widgets
        for widget in self.findChildren(QWidget):
            widget.update()
    
    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        # Ctrl+T: New tab
        QShortcut(
            QKeySequence.StandardKey.AddTab,
            self,
            activated=lambda: self._add_new_tab(self._config.homepage)
        )
        
        # Ctrl+W: Close tab
        QShortcut(
            QKeySequence.StandardKey.Close,
            self,
            activated=self._close_current_tab
        )
        
        # Ctrl+L: Focus address bar
        QShortcut(
            QKeySequence("Ctrl+L"),
            self,
            activated=self._nav_bar.focus_address_bar
        )
        
        # Ctrl+D: Bookmark current page
        QShortcut(
            QKeySequence("Ctrl+D"),
            self,
            activated=self._toggle_bookmark
        )
        
        # F5: Reload
        QShortcut(
            QKeySequence.StandardKey.Refresh,
            self,
            activated=self._reload_current_tab
        )
        
        # Ctrl+R: Reload (alternative)
        QShortcut(
            QKeySequence("Ctrl+R"),
            self,
            activated=self._reload_current_tab
        )
        
        # Escape: Stop loading
        QShortcut(
            QKeySequence("Escape"),
            self,
            activated=self._stop_current_tab
        )
        
        # Alt+Left: Go back
        QShortcut(
            QKeySequence("Alt+Left"),
            self,
            activated=self._go_back
        )
        
        # Alt+Right: Go forward
        QShortcut(
            QKeySequence("Alt+Right"),
            self,
            activated=self._go_forward
        )
        
        # F11: Toggle fullscreen (handled by Qt)
        QShortcut(
            QKeySequence("F11"),
            self,
            activated=self._toggle_fullscreen
        )
    
    def _connect_signals(self) -> None:
        """Connect signals between components."""
        # Navigation bar signals
        self._nav_bar.back_requested.connect(self._go_back)
        self._nav_bar.forward_requested.connect(self._go_forward)
        self._nav_bar.reload_requested.connect(self._reload_current_tab)
        self._nav_bar.stop_requested.connect(self._stop_current_tab)
        self._nav_bar.home_requested.connect(self._go_home)
        self._nav_bar.navigate_requested.connect(self._navigate_to)
        self._nav_bar.bookmark_requested.connect(self._toggle_bookmark)
        self._nav_bar.bookmarks_manager_requested.connect(self._show_bookmarks)
        
        # Tab widget signals
        self._tab_widget.currentChanged.connect(self._on_tab_changed)
        self._tab_widget.tabCloseRequested.connect(self._close_tab)
        self._tab_widget.add_tab_requested.connect(
            lambda: self._add_new_tab(self._config.homepage)
        )
    
    def _apply_window_settings(self) -> None:
        """Apply window size and position settings."""
        if self._config.start_maximized:
            self.showMaximized()
        else:
            self.resize(
                self._config.default_window_width,
                self._config.default_window_height
            )
            self._center_window()
    
    def _center_window(self) -> None:
        """Center the window on the screen."""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            center = screen.availableGeometry().center()
            frame = self.frameGeometry()
            frame.moveCenter(center)
            self.move(frame.topLeft())
    
    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
            self._nav_bar.show()
        else:
            self.showFullScreen()
            # Hide nav bar in fullscreen (can show on hover in future)
            # self._nav_bar.hide()
    
    # Tab Management
    
    def _add_new_tab(self, url: str | None = None) -> BrowserTab:
        """Add a new tab."""
        tab = BrowserTab(url or self._config.homepage, self)
        
        # Connect tab signals
        tab.title_changed.connect(lambda title: self._update_tab_title(tab, title))
        tab.url_changed.connect(lambda url: self._on_tab_url_changed(tab, url))
        tab.load_started.connect(lambda: self._on_tab_load_started(tab))
        tab.load_progress.connect(lambda p: self._on_tab_load_progress(tab, p))
        tab.load_finished.connect(lambda ok: self._on_tab_load_finished(tab, ok))
        tab.new_tab_requested.connect(self._add_new_tab_with_url)
        
        # Add to tab widget
        index = self._tab_widget.addTab(tab, "New Tab")
        self._tab_widget.setCurrentIndex(index)
        
        self.logger.debug(f"Added new tab with URL: {url}")
        return tab
    
    def _add_new_tab_with_url(self, url: QUrl) -> None:
        """Add a new tab with a specific URL."""
        self._add_new_tab(url.toString())
    
    def _close_tab(self, index: int) -> None:
        """Close a tab at the given index."""
        if self._tab_widget.count() <= 1:
            # Don't close the last tab, just clear it
            tab = self._tab_widget.widget(0)
            if isinstance(tab, BrowserTab):
                tab.load_url("about:blank")
            return
        
        tab = self._tab_widget.widget(index)
        if isinstance(tab, BrowserTab):
            tab.close()
            self._tab_widget.removeTab(index)
            self.logger.debug(f"Closed tab at index {index}")
    
    def _close_current_tab(self) -> None:
        """Close the currently active tab."""
        self._close_tab(self._tab_widget.currentIndex())
    
    def _get_current_tab(self) -> BrowserTab | None:
        """Get the currently active tab."""
        widget = self._tab_widget.currentWidget()
        return widget if isinstance(widget, BrowserTab) else None
    
    # Tab Event Handlers
    
    def _update_tab_title(self, tab: BrowserTab, title: str) -> None:
        """Update the tab title."""
        index = self._tab_widget.indexOf(tab)
        if index >= 0:
            # Truncate long titles
            display_title = title[:20] + "..." if len(title) > 23 else title
            self._tab_widget.setTabText(index, display_title)
            self._tab_widget.setTabToolTip(index, title)
    
    def _on_tab_url_changed(self, tab: BrowserTab, url: str) -> None:
        """Handle URL change in a tab."""
        if tab == self._get_current_tab():
            self._nav_bar.set_url(url)
            self._update_bookmark_button()
    
    def _on_tab_load_started(self, tab: BrowserTab) -> None:
        """Handle page load start."""
        if tab == self._get_current_tab():
            self._nav_bar.set_loading(True, 0)
    
    def _on_tab_load_progress(self, tab: BrowserTab, progress: int) -> None:
        """Handle page load progress."""
        if tab == self._get_current_tab():
            self._nav_bar.set_loading(True, progress)
    
    def _on_tab_load_finished(self, tab: BrowserTab, ok: bool) -> None:
        """Handle page load completion."""
        if tab == self._get_current_tab():
            self._nav_bar.set_loading(False, 100)
            self._update_navigation_buttons()
    
    def _on_tab_changed(self, index: int) -> None:
        """Handle tab switch."""
        tab = self._get_current_tab()
        if tab:
            self._nav_bar.set_url(tab.current_url())
            self._update_navigation_buttons()
            self._update_bookmark_button()
    
    # Navigation
    
    def _go_back(self) -> None:
        """Navigate back in current tab."""
        tab = self._get_current_tab()
        if tab:
            tab.back()
            self._update_navigation_buttons()
    
    def _go_forward(self) -> None:
        """Navigate forward in current tab."""
        tab = self._get_current_tab()
        if tab:
            tab.forward()
            self._update_navigation_buttons()
    
    def _reload_current_tab(self) -> None:
        """Reload the current tab."""
        tab = self._get_current_tab()
        if tab:
            tab.reload()
    
    def _stop_current_tab(self) -> None:
        """Stop loading in current tab."""
        tab = self._get_current_tab()
        if tab:
            tab.stop()
            self._nav_bar.set_loading(False)
    
    def _go_home(self) -> None:
        """Navigate to home page."""
        self._navigate_to(self._config.homepage)
    
    def _navigate_to(self, url: str) -> None:
        """Navigate to a URL in the current tab."""
        tab = self._get_current_tab()
        if tab:
            tab.load_url(url)
    
    def _update_navigation_buttons(self) -> None:
        """Update navigation button states."""
        tab = self._get_current_tab()
        if tab:
            self._nav_bar.set_can_go_back(tab.can_go_back())
            self._nav_bar.set_can_go_forward(tab.can_go_forward())
    
    # Bookmarks
    
    def _toggle_bookmark(self) -> None:
        """Toggle bookmark status for current page."""
        tab = self._get_current_tab()
        if not tab:
            return
        
        title = tab.current_title()
        url = tab.current_url()
        
        # Skip blank pages
        if url in ("about:blank", "", "chrome://welcome/"):
            return
        
        is_bookmarked = self._bookmarks_manager.toggle(title, url)
        self._nav_bar.set_bookmarked(is_bookmarked)
        
        self.logger.info(
            f"{'Added' if is_bookmarked else 'Removed'} bookmark: {title}"
        )
    
    def _update_bookmark_button(self) -> None:
        """Update bookmark button based on current page."""
        tab = self._get_current_tab()
        if tab:
            title = tab.current_title()
            is_bookmarked = self._bookmarks_manager.has(title)
            self._nav_bar.set_bookmarked(is_bookmarked)
    
    def _show_bookmarks(self) -> None:
        """Show the bookmarks dialog."""
        if self._bookmarks_dialog is None:
            self._bookmarks_dialog = BookmarksDialog(
                self._bookmarks_manager,
                self
            )
            self._bookmarks_dialog.bookmark_selected.connect(self._navigate_to)
        else:
            self._bookmarks_dialog.refresh()
        
        self._bookmarks_dialog.show()
        self._bookmarks_dialog.raise_()
        self._bookmarks_dialog.activateWindow()
    
    # Window Events
    
    def closeEvent(self, event: "QCloseEvent") -> None:
        """Handle window close event."""
        # Save bookmarks
        self._bookmarks_manager.save()
        
        # Clean up tabs
        for i in range(self._tab_widget.count()):
            tab = self._tab_widget.widget(i)
            if isinstance(tab, BrowserTab):
                tab.close()
        
        self.logger.info("Browser window closing")
        event.accept()
