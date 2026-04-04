#!/usr/bin/env python3
"""
Open Browser - A modern, minimal and fast web browser.

This is the legacy entry point. The browser has been modernized!
For the new modular implementation, use:
    python -m open_browser

Or install the package:
    pip install -e .
    open-browser
"""

import sys
import warnings

def show_migration_notice():
    """Show migration notice and run new implementation."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    Open Browser v2.0.0                           ║
╠══════════════════════════════════════════════════════════════════╣
║  The browser has been completely modernized!                     ║
║                                                                  ║
║  Legacy code has been moved to: run_legacy.py                    ║
║                                                                  ║
║  NEW: Modern Python 3.10+ with type hints                        ║
║  NEW: Modular architecture with clean separation of concerns     ║
║  NEW: PyQt6 with QtWebEngine (modern browser engine)             ║
║  NEW: Pydantic models for data validation                        ║
║  NEW: Proper project structure with pyproject.toml               ║
║                                                                  ║
║  To run the modern version:                                      ║
║    python -m open_browser                                        ║
║                                                                  ║
║  Or install and run:                                             ║
║    pip install -e .                                              ║
║    open-browser                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    show_migration_notice()
    
    # Run the new implementation
    try:
        from open_browser.main import main
        sys.exit(main())
    except ImportError as e:
        print(f"Error: {e}")
        print("\nPlease install the required dependencies:")
        print("    pip install -e .")
        sys.exit(1)
