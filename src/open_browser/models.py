"""
Data models for Open Browser.

This module contains Pydantic models for configuration,
bookmarks, and other data structures.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class Bookmark(BaseModel):
    """Represents a single bookmark with metadata."""
    
    title: str = Field(..., min_length=1, description="The title of the bookmark")
    url: str = Field(..., min_length=1, description="The URL of the bookmark")
    added_at: datetime = Field(default_factory=datetime.now, description="When the bookmark was added")
    favicon_url: str | None = Field(default=None, description="URL to the favicon")
    
    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        """Validate that the URL has a valid scheme."""
        parsed = urlparse(value)
        if not parsed.scheme:
            return f"https://{value}"
        if parsed.scheme not in ("http", "https", "file", "data"):
            raise ValueError(f"Unsupported URL scheme: {parsed.scheme}")
        return value
    
    def __hash__(self) -> int:
        """Enable using Bookmark in sets and as dict keys."""
        return hash((self.title, self.url))
    
    def __eq__(self, other: object) -> bool:
        """Check equality based on title and URL."""
        if not isinstance(other, Bookmark):
            return NotImplemented
        return self.title == other.title and self.url == other.url


class BookmarksData(BaseModel):
    """Container for all bookmarks with persistence."""
    
    bookmarks: list[Bookmark] = Field(default_factory=list)
    last_modified: datetime = Field(default_factory=datetime.now)
    
    def add(self, bookmark: Bookmark) -> bool:
        """
        Add a bookmark if it doesn't already exist.
        
        Returns:
            True if added, False if already exists.
        """
        if bookmark not in self.bookmarks:
            self.bookmarks.append(bookmark)
            self.last_modified = datetime.now()
            return True
        return False
    
    def remove(self, title: str) -> bool:
        """
        Remove a bookmark by title.
        
        Returns:
            True if removed, False if not found.
        """
        for i, bookmark in enumerate(self.bookmarks):
            if bookmark.title == title:
                self.bookmarks.pop(i)
                self.last_modified = datetime.now()
                return True
        return False
    
    def get_by_title(self, title: str) -> Bookmark | None:
        """Get a bookmark by its title."""
        for bookmark in self.bookmarks:
            if bookmark.title == title:
                return bookmark
        return None
    
    def has(self, title: str) -> bool:
        """Check if a bookmark with the given title exists."""
        return any(b.title == title for b in self.bookmarks)


class BrowserConfig(BaseModel):
    """Browser configuration settings."""
    
    # Window settings
    default_window_width: int = Field(default=1200, ge=400)
    default_window_height: int = Field(default=800, ge=300)
    start_maximized: bool = True
    
    # Homepage
    homepage: str = "https://www.google.com"
    
    # Search settings
    search_engine: str = "https://www.google.com/search?q={query}"
    
    # Privacy settings
    enable_javascript: bool = True
    enable_plugins: bool = True
    enable_local_storage: bool = True
    
    # Appearance
    show_bookmarks_bar: bool = False
    tab_position: str = "north"  # north, south, east, west
    
    # Data paths
    data_dir: Path = Field(default=Path.home() / ".open_browser")
    bookmarks_file: str = "bookmarks.json"
    config_file: str = "settings.json"
    
    @field_validator("data_dir", mode="before")
    @classmethod
    def ensure_path(cls, value: str | Path) -> Path:
        """Convert string to Path and ensure directory exists."""
        path = Path(value)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def bookmarks_path(self) -> Path:
        """Get the full path to the bookmarks file."""
        return self.data_dir / self.bookmarks_file
    
    @property
    def config_path(self) -> Path:
        """Get the full path to the config file."""
        return self.data_dir / self.config_file
    
    model_config = {"extra": "allow"}


class TabState(BaseModel):
    """Represents the state of a browser tab."""
    
    url: str
    title: str = "New Tab"
    history: list[str] = Field(default_factory=list)
    history_index: int = Field(default=-1, ge=-1)
    
    def can_go_back(self) -> bool:
        """Check if we can navigate back in history."""
        return self.history_index > 0
    
    def can_go_forward(self) -> bool:
        """Check if we can navigate forward in history."""
        return 0 <= self.history_index < len(self.history) - 1
    
    def go_back(self) -> str | None:
        """Go back in history and return the URL."""
        if self.can_go_back():
            self.history_index -= 1
            return self.history[self.history_index]
        return None
    
    def go_forward(self) -> str | None:
        """Go forward in history and return the URL."""
        if self.can_go_forward():
            self.history_index += 1
            return self.history[self.history_index]
        return None
    
    def navigate_to(self, url: str) -> None:
        """Navigate to a new URL, updating history."""
        # Remove any forward history when navigating to new page
        if self.history_index < len(self.history) - 1:
            self.history = self.history[: self.history_index + 1]
        
        self.history.append(url)
        self.history_index = len(self.history) - 1
        self.url = url
