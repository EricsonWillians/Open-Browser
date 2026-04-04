"""
Modern theme system for Open Browser.

Provides elegant dark and light themes with consistent styling.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Final


class ThemeMode(Enum):
    """Available theme modes."""
    LIGHT = auto()
    DARK = auto()
    AUTO = auto()


@dataclass(frozen=True)
class ThemeColors:
    """Color palette for a theme."""
    # Background colors
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str
    bg_hover: str
    bg_pressed: str
    
    # Text colors
    text_primary: str
    text_secondary: str
    text_disabled: str
    text_inverse: str
    
    # Accent colors
    accent: str
    accent_hover: str
    accent_pressed: str
    
    # Border colors
    border: str
    border_focus: str
    
    # Status colors
    success: str
    warning: str
    error: str
    info: str
    
    # Special
    shadow: str
    overlay: str


class Theme:
    """Theme manager with modern styling."""
    
    # Refined dark theme - cleaner and more elegant
    DARK: Final[ThemeColors] = ThemeColors(
        bg_primary="#1a1a2e",      # Deep blue-black
        bg_secondary="#16162a",    # Slightly darker for contrast
        bg_tertiary="#252542",     # Elevated surfaces
        bg_hover="#2d2d52",        # Subtle hover
        bg_pressed="#353560",      # Pressed state
        
        text_primary="#ffffff",    # Pure white for primary text
        text_secondary="#a0a0c0",  # Muted lavender-gray
        text_disabled="#505070",   # Dimmed
        text_inverse="#1a1a2e",    # Inverse for buttons
        
        accent="#6366f1",          # Indigo 500 - modern accent
        accent_hover="#818cf8",    # Indigo 400
        accent_pressed="#a5b4fc",  # Indigo 300
        
        border="#2a2a45",          # Very subtle border
        border_focus="#6366f1",    # Accent border on focus
        
        success="#22c55e",
        warning="#f59e0b",
        error="#ef4444",
        info="#3b82f6",
        
        shadow="rgba(0, 0, 0, 0.4)",
        overlay="rgba(0, 0, 0, 0.7)",
    )
    
    # Light theme
    LIGHT: Final[ThemeColors] = ThemeColors(
        bg_primary="#ffffff",
        bg_secondary="#f8f9fa",
        bg_tertiary="#e9ecef",
        bg_hover="#dee2e6",
        bg_pressed="#ced4da",
        
        text_primary="#212529",
        text_secondary="#6c757d",
        text_disabled="#adb5bd",
        text_inverse="#ffffff",
        
        accent="#4f46e5",
        accent_hover="#4338ca",
        accent_pressed="#3730a3",
        
        border="#e9ecef",
        border_focus="#4f46e5",
        
        success="#22c55e",
        warning="#f59e0b",
        error="#ef4444",
        info="#3b82f6",
        
        shadow="rgba(0, 0, 0, 0.1)",
        overlay="rgba(0, 0, 0, 0.5)",
    )
    
    def __init__(self, mode: ThemeMode = ThemeMode.DARK) -> None:
        """Initialize theme with specified mode."""
        self.mode = mode
        self.colors = self.DARK if mode == ThemeMode.DARK else self.LIGHT
    
    def set_mode(self, mode: ThemeMode) -> None:
        """Change theme mode."""
        self.mode = mode
        self.colors = self.DARK if mode == ThemeMode.DARK else self.LIGHT
    
    def get_stylesheet(self) -> str:
        """Generate complete application stylesheet."""
        c = self.colors
        
        return f"""
        /* ===== GLOBAL ===== */
        QMainWindow {{
            background-color: {c.bg_primary};
        }}
        
        /* ===== NAVIGATION BAR ===== */
        NavigationBar {{
            background-color: {c.bg_secondary};
            border: none;
        }}
        
        /* Navigation Buttons */
        IconButton {{
            background-color: transparent;
            border: none;
            border-radius: 6px;
            padding: 6px;
            color: {c.text_secondary};
        }}
        
        IconButton:hover {{
            background-color: {c.bg_hover};
            color: {c.text_primary};
        }}
        
        IconButton:pressed {{
            background-color: {c.bg_pressed};
        }}
        
        IconButton:disabled {{
            color: {c.text_disabled};
            background-color: transparent;
        }}
        
        /* ===== ADDRESS BAR ===== */
        AddressBar {{
            background-color: {c.bg_primary};
            border: 1px solid {c.border};
            border-radius: 20px;
            padding: 0 16px;
            color: {c.text_primary};
            font-size: 13px;
            selection-background-color: {c.accent};
        }}
        
        AddressBar:hover {{
            border-color: {c.bg_hover};
        }}
        
        AddressBar:focus {{
            border-color: {c.accent};
            background-color: {c.bg_primary};
        }}
        
        AddressBar::placeholder {{
            color: {c.text_secondary};
        }}
        
        /* ===== TABS ===== */
        QTabWidget::pane {{
            border: none;
            background-color: {c.bg_primary};
        }}
        
        QTabBar::tab {{
            background-color: {c.bg_secondary};
            color: {c.text_secondary};
            border: none;
            border-bottom: 2px solid transparent;
            padding: 12px 20px;
            margin-right: 2px;
            font-size: 12px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {c.bg_primary};
            color: {c.text_primary};
            border-bottom-color: {c.accent};
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {c.bg_hover};
            color: {c.text_primary};
        }}
        
        /* ===== BUTTONS ===== */
        QPushButton {{
            background-color: {c.accent};
            color: {c.text_inverse};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {c.accent_hover};
        }}
        
        QPushButton:pressed {{
            background-color: {c.accent_pressed};
        }}
        
        QPushButton:disabled {{
            background-color: {c.bg_tertiary};
            color: {c.text_disabled};
        }}
        
        /* ===== LISTS ===== */
        QListWidget {{
            background-color: {c.bg_secondary};
            border: 1px solid {c.border};
            border-radius: 8px;
            padding: 8px;
            outline: none;
        }}
        
        QListWidget::item {{
            background-color: transparent;
            border-radius: 6px;
            padding: 10px 14px;
            margin: 2px 0;
            color: {c.text_primary};
        }}
        
        QListWidget::item:selected {{
            background-color: {c.accent};
            color: {c.text_inverse};
        }}
        
        QListWidget::item:hover:!selected {{
            background-color: {c.bg_hover};
        }}
        
        /* ===== DIALOGS ===== */
        QDialog {{
            background-color: {c.bg_primary};
        }}
        
        /* ===== LABELS ===== */
        QLabel {{
            color: {c.text_primary};
            background-color: transparent;
        }}
        
        /* ===== LINE EDIT ===== */
        QLineEdit {{
            background-color: {c.bg_secondary};
            border: 1px solid {c.border};
            border-radius: 8px;
            padding: 10px 14px;
            color: {c.text_primary};
            selection-background-color: {c.accent};
        }}
        
        QLineEdit:focus {{
            border-color: {c.accent};
        }}
        
        /* ===== MENU ===== */
        QMenu {{
            background-color: {c.bg_secondary};
            border: 1px solid {c.border};
            border-radius: 8px;
            padding: 6px;
        }}
        
        QMenu::item {{
            padding: 8px 20px;
            border-radius: 6px;
            color: {c.text_primary};
        }}
        
        QMenu::item:selected {{
            background-color: {c.accent};
            color: {c.text_inverse};
        }}
        
        /* ===== TOOLTIPS ===== */
        QToolTip {{
            background-color: {c.bg_secondary};
            color: {c.text_primary};
            border: 1px solid {c.border};
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 12px;
        }}
        
        /* ===== SCROLLBARS ===== */
        QScrollBar:vertical {{
            background-color: transparent;
            width: 10px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {c.bg_tertiary};
            min-height: 40px;
            border-radius: 5px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {c.bg_hover};
        }}
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """


# Global theme instance
_current_theme: Theme | None = None


def get_theme() -> Theme:
    """Get the current theme instance."""
    global _current_theme
    if _current_theme is None:
        _current_theme = Theme(ThemeMode.DARK)
    return _current_theme


def set_theme_mode(mode: ThemeMode) -> None:
    """Set the global theme mode."""
    global _current_theme
    _current_theme = Theme(mode)
