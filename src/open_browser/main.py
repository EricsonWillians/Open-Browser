"""
Main entry point for Open Browser.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from open_browser.browser_window import BrowserWindow
from open_browser.storage import BookmarksManager, ConfigManager
from open_browser.theme import get_theme, ThemeMode


def setup_logging(verbose: bool = False) -> None:
    """Configure application logging."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    logging.getLogger("PyQt6").setLevel(logging.WARNING)


def create_application() -> QApplication:
    """Create and configure the QApplication instance."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Open Browser")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("open-browser")
    
    # Set modern default font
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    # Set Fusion style for modern look
    app.setStyle("Fusion")
    
    return app


def main() -> int:
    """Main entry point."""
    # Parse command line arguments
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    
    # Setup logging
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    logger.info("Starting Open Browser v2.0.0")
    
    # Create application
    app = create_application()
    
    # Initialize storage managers
    config_manager = ConfigManager()
    bookmarks_manager = BookmarksManager()
    
    # Create and show main window
    icons_dir = Path(__file__).parent.parent.parent / "GFX"
    if not icons_dir.exists():
        icons_dir = Path("GFX")
    
    window = BrowserWindow(
        config_manager=config_manager,
        bookmarks_manager=bookmarks_manager,
        icons_dir=icons_dir if icons_dir.exists() else None
    )
    window.show()
    
    logger.info("Browser window shown")
    
    # Run application event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
