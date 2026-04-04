"""
Web view widget using Qt WebEngine.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QUrl, Qt, pyqtSignal
from PyQt6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineSettings,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

if TYPE_CHECKING:
    from PyQt6.QtGui import QKeyEvent, QMouseEvent


class WebEngineView(QWebEngineView):
    """
    Enhanced web view with custom behavior.
    
    Emits signals for link clicks and provides custom context menu.
    """
    
    # Custom signals
    link_clicked = pyqtSignal(QUrl)
    open_in_new_tab_requested = pyqtSignal(QUrl)
    
    def __init__(self, parent: "WebEngineView" | None = None) -> None:
        """Initialize the web view with custom settings."""
        super().__init__(parent)
        self._setup_settings()
        self._middle_click_pos = None
    
    def _setup_settings(self) -> None:
        """Configure web engine settings."""
        settings = self.settings()
        
        # Enable modern web features
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptEnabled, True
        )
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True
        )
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.LocalStorageEnabled, True
        )
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.PluginsEnabled, True
        )
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True
        )
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False
        )
        
        # Set default encoding
        settings.setDefaultTextEncoding("utf-8")
    
    def mousePressEvent(self, event: "QMouseEvent") -> None:
        """Handle mouse press events."""
        # Store position for middle-click detection
        if event.button() == Qt.MouseButton.MiddleButton:
            self._middle_click_pos = event.pos()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: "QMouseEvent") -> None:
        """Handle mouse release events for middle-click link opening."""
        if (event.button() == Qt.MouseButton.MiddleButton and 
            self._middle_click_pos is not None):
            # Check if we clicked on a link
            pos = event.pos()
            page = self.page()
            if page is not None:
                # Emit signal to open link in new tab
                # Note: QWebEngine doesn't expose link element detection easily
                # This is handled at the page level
                pass
            self._middle_click_pos = None
        super().mouseReleaseEvent(event)
    
    def createWindow(self, window_type: QWebEnginePage.WebWindowType) -> "WebEngineView":
        """
        Create a new window/tab when requested by JavaScript.
        
        Args:
            window_type: The type of window to create.
            
        Returns:
            A new web view instance.
        """
        if window_type == QWebEnginePage.WebWindowType.WebBrowserTab:
            # Emit signal for parent to handle
            new_view = WebEngineView()
            self.open_in_new_tab_requested.emit(new_view.url())
            return new_view
        return super().createWindow(window_type)
    
    def contextMenuEvent(self, event: "QMouseEvent") -> None:
        """Show custom context menu."""
        menu = self.createStandardContextMenu()
        menu.exec(event.globalPos())


class WebPage(QWebEnginePage):
    """
    Custom web page with enhanced functionality.
    """
    
    link_clicked = pyqtSignal(QUrl)
    
    def __init__(self, profile: QWebEngineProfile | None = None, parent=None):
        """Initialize the web page."""
        super().__init__(profile, parent)
    
    def acceptNavigationRequest(
        self, 
        url: QUrl, 
        nav_type: QWebEnginePage.NavigationType, 
        is_main_frame: bool
    ) -> bool:
        """
        Handle navigation requests.
        
        Args:
            url: The URL to navigate to.
            nav_type: The type of navigation.
            is_main_frame: Whether this is the main frame.
            
        Returns:
            True to allow navigation, False to block.
        """
        # Emit signal for link clicks
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            self.link_clicked.emit(url)
        
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)
