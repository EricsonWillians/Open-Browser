"""
Utility functions for Open Browser.
"""

from __future__ import annotations

import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class URLUtils:
    """URL handling utilities."""
    
    # Common TLDs for URL validation
    COMMON_TLDS = frozenset({
        "com", "org", "net", "edu", "gov", "io", "co", "ai", "app",
        "dev", "cloud", "tech", "blog", "shop", "site", "online",
        "uk", "de", "fr", "jp", "cn", "ru", "br", "au", "in",
        "info", "biz", "name", "pro", "tv", "cc", "ws", "me"
    })
    
    # Simple URL pattern
    URL_PATTERN = re.compile(
        r"^(https?://|file://|data:|about:|chrome://)"
    )
    
    @classmethod
    def is_valid_url(cls, text: str) -> bool:
        """
        Check if text looks like a valid URL.
        
        Args:
            text: The text to check.
            
        Returns:
            True if it looks like a URL.
        """
        text = text.strip()
        
        # Check for scheme
        if cls.URL_PATTERN.match(text):
            return True
        
        # Check for domain-like pattern
        if " " in text:
            return False
        
        parsed = urlparse(f"http://{text}")
        if parsed.netloc:
            parts = parsed.netloc.split(".")
            if len(parts) >= 2:
                # Check for valid TLD or at least 2+ chars for TLD
                tld = parts[-1].lower()
                if len(tld) >= 2 and tld.isalpha():
                    return True
        
        return False
    
    @classmethod
    def normalize_url(cls, text: str) -> str:
        """
        Convert user input to a proper URL.
        
        Args:
            text: The user input.
            
        Returns:
            A normalized URL.
        """
        text = text.strip()
        
        # Already has scheme
        if cls.URL_PATTERN.match(text):
            return text
        
        # Local file
        if text.startswith("/") or text.startswith("./") or text.startswith("../"):
            return f"file://{text}"
        
        # Add https:// for domain-like URLs
        if cls.is_valid_url(text):
            return f"https://{text}"
        
        # Treat as search query
        return None
    
    @classmethod
    def format_for_display(cls, url: str, max_length: int = 50) -> str:
        """
        Format a URL for display in the UI.
        
        Args:
            url: The URL to format.
            max_length: Maximum length before truncation.
            
        Returns:
            Formatted URL string.
        """
        # Remove scheme for display
        display = url
        for prefix in ("https://", "http://", "file://"):
            if display.startswith(prefix):
                display = display[len(prefix):]
                break
        
        # Remove trailing slash
        display = display.rstrip("/")
        
        # Truncate if too long
        if len(display) > max_length:
            display = display[:max_length - 3] + "..."
        
        return display


class SearchUtils:
    """Search-related utilities."""
    
    SEARCH_ENGINES = {
        "google": "https://www.google.com/search?q={query}",
        "duckduckgo": "https://duckduckgo.com/?q={query}",
        "bing": "https://www.bing.com/search?q={query}",
        "yahoo": "https://search.yahoo.com/search?p={query}",
        "ecosia": "https://www.ecosia.org/search?q={query}",
        "brave": "https://search.brave.com/search?q={query}",
    }
    
    @classmethod
    def build_search_url(cls, query: str, engine: str = "google") -> str:
        """
        Build a search URL for the given query.
        
        Args:
            query: The search query.
            engine: The search engine to use.
            
        Returns:
            The search URL.
        """
        template = cls.SEARCH_ENGINES.get(engine, cls.SEARCH_ENGINES["google"])
        import urllib.parse
        return template.format(query=urllib.parse.quote_plus(query))
    
    @classmethod
    def process_input(cls, text: str, default_search: str = "google") -> str:
        """
        Process user input and convert to URL.
        
        If input is a URL, normalize it.
        If input is a search query, build a search URL.
        
        Args:
            text: The user input.
            default_search: The default search engine.
            
        Returns:
            A URL to navigate to.
        """
        text = text.strip()
        
        if not text:
            return "about:blank"
        
        # Try to normalize as URL
        url = URLUtils.normalize_url(text)
        if url is not None:
            return url
        
        # Treat as search query
        return cls.build_search_url(text, default_search)


class LoggingMixin:
    """Mixin to add logging support to classes."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get a logger for this class."""
        return logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__)
