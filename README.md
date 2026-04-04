# Open Browser v2.0.0

A modern, minimal and fast web browser built with Python and Qt6.

![Open Browser](GFX/fav.png)

## What's New in v2.0.0

This is a **complete modernization** of the original 10-year-old browser project:

### 🚀 Modern Stack
- **Python 3.10+** with full type hints and type safety
- **PyQt6** - Latest Qt bindings with modern features
- **QtWebEngine** - Modern Chromium-based browser engine (replaces deprecated QtWebKit)
- **Pydantic v2** - Data validation and settings management
- **pyproject.toml** - Modern Python packaging standard

### 🏗️ Architecture
- **Modular design** - Clean separation of concerns
- **Type-safe** - Full mypy-compatible type annotations
- **Extensible** - Easy to add new features and integrations
- **Maintainable** - Well-documented, testable code structure

### ✨ Features
- Multi-tab browsing with close buttons
- Smart address bar (URL detection and search)
- Bookmarks with JSON persistence
- Keyboard shortcuts (Ctrl+T, Ctrl+W, Ctrl+L, F5, etc.)
- Modern UI with stylesheet support
- Optional Dropbox integration for bookmark sync
- Cross-platform support (Linux, macOS, Windows)

## Prerequisites

- **Python 3.10 or higher**
- **Qt6 libraries** (installed automatically with PyQt6)

## Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/EricsonWillians/Open-Browser
cd Open-Browser

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .

# Run the browser
open-browser
```

### Development Installation

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run type checking
mypy src/open_browser

# Run linting
ruff check src/open_browser
```

### With Dropbox Support

```bash
pip install -e ".[dropbox]"
```

## Usage

### Running the Browser

```bash
# Method 1: Using the installed command
open-browser

# Method 2: Using Python module
python -m open_browser

# Method 3: Using the run script
python run.py

# Method 4: Verbose mode (debug logging)
python -m open_browser -v
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+T` | Open new tab |
| `Ctrl+W` | Close current tab |
| `Ctrl+L` | Focus address bar |
| `Ctrl+D` | Bookmark current page |
| `F5` / `Ctrl+R` | Reload page |
| `Escape` | Stop loading |
| `Alt+Left` | Go back |
| `Alt+Right` | Go forward |

## Project Structure

```
Open-Browser/
├── src/
│   └── open_browser/
│       ├── __init__.py          # Package initialization
│       ├── models.py            # Pydantic data models
│       ├── storage.py           # Persistence layer
│       ├── utils.py             # Utility functions
│       ├── main.py              # Application entry point
│       ├── browser_window.py    # Main window implementation
│       ├── widgets/             # UI components
│       │   ├── web_view.py      # Web engine view
│       │   ├── address_bar.py   # Smart address bar
│       │   ├── browser_tab.py   # Tab implementation
│       │   ├── navigation_bar.py # Navigation controls
│       │   └── bookmarks_dialog.py # Bookmarks manager
│       └── services/            # External integrations
│           └── dropbox.py       # Dropbox sync (optional)
├── tests/                       # Test suite
├── GFX/                         # Icons and images
├── pyproject.toml              # Modern Python packaging
├── run.py                      # Entry point script
├── run_legacy.py               # Original code (for reference)
└── README.md                   # This file
```

## Configuration

Configuration and bookmarks are stored in:
- **Linux/macOS**: `~/.open_browser/`
- **Windows**: `%USERPROFILE%\.open_browser\`

Files:
- `settings.json` - Browser configuration
- `bookmarks.json` - User bookmarks

## Development

### Type Checking

```bash
mypy src/open_browser
```

### Code Quality

```bash
# Linting
ruff check src/open_browser

# Formatting
ruff format src/open_browser
```

### Testing

```bash
pytest
```

## Migration from v1.x

The original PyQt4/QtWebKit code has been preserved as `run_legacy.py` for reference.

To use the new version:
1. Install the package: `pip install -e .`
2. Run: `open-browser`

Key differences:
- Modern web engine (QtWebEngine vs QtWebKit)
- Type-safe codebase
- Modular architecture
- Pydantic models for data
- Better error handling and logging

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original browser created by Ericson Willians (2016)
- Modernized version using modern Python best practices
- Icons from the original project
