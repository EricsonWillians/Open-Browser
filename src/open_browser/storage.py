"""
Storage and persistence layer for Open Browser.

Handles loading and saving of bookmarks, settings, and other data.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from open_browser.models import Bookmark, BookmarksData, BrowserConfig

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class JsonStorage:
    """Generic JSON storage for Pydantic models."""
    
    def __init__(self, file_path: Path) -> None:
        """
        Initialize storage with a file path.
        
        Args:
            file_path: Path to the JSON file.
        """
        self.file_path = file_path
        self._ensure_directory()
    
    def _ensure_directory(self) -> None:
        """Ensure the parent directory exists."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save(self, data: BaseModel) -> bool:
        """
        Save a Pydantic model to JSON.
        
        Args:
            data: The model to save.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            self.file_path.write_text(
                data.model_dump_json(indent=2),
                encoding="utf-8"
            )
            logger.debug(f"Saved data to {self.file_path}")
            return True
        except (IOError, OSError) as e:
            logger.error(f"Failed to save to {self.file_path}: {e}")
            return False
    
    def load(self, model_class: type[T]) -> T | None:
        """
        Load a Pydantic model from JSON.
        
        Args:
            model_class: The class to instantiate from the JSON data.
            
        Returns:
            The loaded model, or None if loading failed.
        """
        if not self.file_path.exists():
            logger.debug(f"File {self.file_path} does not exist, returning None")
            return None
        
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            instance = model_class.model_validate(data)
            logger.debug(f"Loaded data from {self.file_path}")
            return instance
        except (json.JSONDecodeError, IOError, OSError) as e:
            logger.error(f"Failed to load from {self.file_path}: {e}")
            return None


class BookmarksManager:
    """Manages bookmarks with persistence."""
    
    def __init__(self, storage: JsonStorage | None = None) -> None:
        """
        Initialize the bookmarks manager.
        
        Args:
            storage: Optional custom storage instance.
        """
        if storage is None:
            config = BrowserConfig()
            storage = JsonStorage(config.bookmarks_path)
        self._storage = storage
        self._data = self._load_or_create()
    
    def _load_or_create(self) -> BookmarksData:
        """Load existing bookmarks or create new ones."""
        data = self._storage.load(BookmarksData)
        return data if data is not None else BookmarksData()
    
    @property
    def bookmarks(self) -> list[Bookmark]:
        """Get the list of bookmarks."""
        return self._data.bookmarks
    
    def add(self, title: str, url: str) -> bool:
        """
        Add a bookmark.
        
        Args:
            title: The bookmark title.
            url: The bookmark URL.
            
        Returns:
            True if added, False if already exists.
        """
        bookmark = Bookmark(title=title, url=url)
        if self._data.add(bookmark):
            self.save()
            return True
        return False
    
    def remove(self, title: str) -> bool:
        """
        Remove a bookmark by title.
        
        Args:
            title: The title of the bookmark to remove.
            
        Returns:
            True if removed, False if not found.
        """
        if self._data.remove(title):
            self.save()
            return True
        return False
    
    def has(self, title: str) -> bool:
        """Check if a bookmark with the given title exists."""
        return self._data.has(title)
    
    def get(self, title: str) -> Bookmark | None:
        """Get a bookmark by title."""
        return self._data.get_by_title(title)
    
    def toggle(self, title: str, url: str) -> bool:
        """
        Toggle a bookmark - add if not exists, remove if exists.
        
        Args:
            title: The bookmark title.
            url: The bookmark URL.
            
        Returns:
            True if bookmark now exists, False if it was removed.
        """
        if self.has(title):
            self.remove(title)
            return False
        else:
            self.add(title, url)
            return True
    
    def save(self) -> bool:
        """Save bookmarks to disk."""
        return self._storage.save(self._data)
    
    def reload(self) -> None:
        """Reload bookmarks from disk."""
        self._data = self._load_or_create()


class ConfigManager:
    """Manages browser configuration with persistence."""
    
    def __init__(self, storage: JsonStorage | None = None) -> None:
        """
        Initialize the config manager.
        
        Args:
            storage: Optional custom storage instance.
        """
        if storage is None:
            default_config = BrowserConfig()
            storage = JsonStorage(default_config.config_path)
        self._storage = storage
        self._config = self._load_or_create()
    
    def _load_or_create(self) -> BrowserConfig:
        """Load existing config or create default."""
        data = self._storage.load(BrowserConfig)
        return data if data is not None else BrowserConfig()
    
    @property
    def config(self) -> BrowserConfig:
        """Get the current configuration."""
        return self._config
    
    def update(self, **kwargs: object) -> None:
        """
        Update configuration settings.
        
        Args:
            **kwargs: Settings to update.
        """
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        self.save()
    
    def save(self) -> bool:
        """Save configuration to disk."""
        return self._storage.save(self._config)
    
    def reload(self) -> None:
        """Reload configuration from disk."""
        self._config = self._load_or_create()
